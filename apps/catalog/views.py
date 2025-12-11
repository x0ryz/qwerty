import json
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Min, Prefetch
from django.core.paginator import Paginator

from .models import Category, Product, ProductImage, AttributeValue
from .filters import ProductFilter
from .recommender import Recommender
from cart.forms import CartAddProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product/list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        qs = Product.objects.all()

        category_slug = self.request.GET.get('category') or self.kwargs.get('category_slug')
        self.category = None

        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            qs = qs.filter(category=self.category)

        main_images = ProductImage.objects.filter(is_main=True)
        qs = qs.annotate(
            min_price=Min('variants__price'),
            orders_count=Count('variants__order_items')
        ).prefetch_related(
            Prefetch('images', queryset=main_images, to_attr='main_img_list')
        )

        self.filterset = ProductFilter(
            self.request.GET,
            queryset=qs,
            category=self.category
        )

        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        context['filter'] = self.filterset
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Оптимізація запитів (те саме, що було, це good practice)
        return super().get_queryset().prefetch_related(
            'variants__attributes__attribute',
            'images__attribute_value',
            'category',
            'brand',
            'keyboard_specs',  # Якщо є
            'switch_specs'     # Якщо є
        )

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            # Якщо це HTMX запит - віддаємо файл з OOB оновленнями
            return ['catalog/product/partials/htmx_update.html']
        # Якщо звичайний візит - повну сторінку
        return ['catalog/product/detail.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        request = self.request

        # 1. Отримуємо поточні вибрані опції з URL (напр. ?Color=10&Switch=5)
        # Ми фільтруємо тільки ті параметри, які є атрибутами
        current_selection = {}
        for key, value in request.GET.items():
            if value.isdigit(): # Захист, очікуємо ID
                current_selection[key] = int(value)

        # 2. Отримуємо всі доступні варіанти
        variants = product.variants.filter(available=True).prefetch_related('attributes__attribute')

        # 3. Збираємо унікальні атрибути, які існують у варіантах
        # Структура: { "Color": [ValueObj1, ValueObj2], "Switch": [...] }
        attributes_map = {}
        for variant in variants:
            for attr_val in variant.attributes.all():
                attr_name = attr_val.attribute.name
                if attr_name not in attributes_map:
                    attributes_map[attr_name] = set()
                attributes_map[attr_name].add(attr_val)

        # 4. Формуємо список груп для шаблону з готовими HTMX URL
        attribute_groups = []
        for attr_name, values in attributes_map.items():
            values_list = sorted(list(values), key=lambda x: x.id)
            group_data = {
                'name': attr_name,
                'values': []
            }

            for val in values_list:
                # Генеруємо URL для цієї кнопки.
                # Беремо поточні параметри, замінюємо поточний атрибут на цей val.id
                params = request.GET.copy()
                params[attr_name] = val.id
                url = f"?{params.urlencode()}"

                is_selected = current_selection.get(attr_name) == val.id

                group_data['values'].append({
                    'label': val.value,
                    'value': val.id,
                    'is_selected': is_selected,
                    'update_url': url
                })
            attribute_groups.append(group_data)

        # 5. Спроба знайти конкретний варіант
        # Варіант вважається знайденим, якщо він має ВСІ вибрані атрибути
        selected_variant = None

        # Перевіряємо, чи кількість вибраних атрибутів збігається з кількістю груп
        if len(current_selection) == len(attributes_map) and len(attributes_map) > 0:
            # Фільтруємо варіанти
            candidates = variants
            for attr_name, val_id in current_selection.items():
                candidates = candidates.filter(
                    attributes__attribute__name=attr_name,
                    attributes__id=val_id
                )
            selected_variant = candidates.first()

        # 6. Логіка Зображень (Server-side)
        # Базові зображення (без прив'язки)
        general_images = [img.image.url for img in product.images.filter(attribute_value__isnull=True)]

        # Специфічні зображення
        specific_images = []
        # Проходимо по вибраних ID, шукаємо чи є для них картинки
        for val_id in current_selection.values():
            imgs = product.images.filter(attribute_value_id=val_id)
            for img in imgs:
                specific_images.append(img.image.url)

        # Логіка пріоритету: Специфічні -> Загальні
        gallery_images = specific_images if specific_images else general_images

        # Якщо геть пусто
        current_image = gallery_images[0] if gallery_images else None
        thumbnails = gallery_images # Можна додати слайсинг [0:4], якщо треба

        # 7. Рекомендації
        r = Recommender()
        recommended_products = r.suggest_products_for([product], 4)

        # 8. Фінальний контекст
        context.update({
            'is_htmx': request.headers.get('HX-Request') == 'true',
            'cart_product_form': CartAddProductForm(),

            'attribute_groups': attribute_groups, # Нова структура для кнопок
            'selected_variant': selected_variant, # Знайдений варіант (або None)

            'current_image': current_image,
            'thumbnails': thumbnails,
            'min_price': min(v.price for v in variants) if variants else 0,

            'recommended_products': recommended_products,
        })

        return context