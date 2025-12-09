import django_filters
from django import forms
from django.db.models import Q
from .models import Product, Brand, AttributeValue


class ProductFilter(django_filters.FilterSet):

    query = django_filters.CharFilter(
        method='filter_search',
        label='Пошук',
        widget=forms.TextInput
    )

    min_price = django_filters.NumberFilter(
        field_name='variants__price',
        lookup_expr='gte',
        label='Min Price',
        distinct=True,
        widget=forms.NumberInput
    )

    max_price = django_filters.NumberFilter(
        field_name='variants__price',
        lookup_expr='lte',
        label='Max Price',
        distinct=True,
        widget=forms.NumberInput
    )

    brand = django_filters.ModelMultipleChoiceFilter(
        queryset=Brand.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Brands'
    )

    o = django_filters.OrderingFilter(
        fields=(
            ('variants__price', 'price'),
            ('created', 'date'),
        ),
        field_labels={
            'price': 'Price (Low to High)',
            '-price': 'Price (High to Low)',
            '-date': 'Newest First',
        },
        widget=forms.Select
    )

    class Meta:
        model = Product
        fields = ['brand', 'min_price', 'max_price']

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)

        if category:
            for attr in category.available_attributes.all().prefetch_related('values'):
                filter_key = f'attr_{attr.slug}'

                self.filters[filter_key] = django_filters.ModelMultipleChoiceFilter(
                    field_name='variants__attributes',
                    queryset=AttributeValue.objects.filter(attribute=attr),
                    to_field_name='id',
                    label=attr.name,
                    widget=forms.CheckboxSelectMultiple,
                    conjoined=False,
                    distinct=True
                )

        input_style = 'w-full bg-gray-50 border-2 border-black p-2 font-mono text-sm'

        self.form.fields['query'].widget.attrs.update({
            'placeholder': 'Search...',
            'class': input_style
        })
        self.form.fields['min_price'].widget.attrs.update({
            'placeholder': '0',
            'class': input_style
        })
        self.form.fields['max_price'].widget.attrs.update({
            'placeholder': '1000',
            'class': input_style
        })

        self.form.fields['o'].widget.attrs.update({
            'class': 'bg-white border-2 border-black p-1 font-mono text-sm focus:outline-none cursor-pointer'
        })

        checkbox_style = 'appearance-none w-4 h-4 border-2 border-black bg-white checked:bg-black transition-colors cursor-pointer mr-2'

        self.form.fields['brand'].widget.attrs.update({'class': checkbox_style})

        for name, field in self.form.fields.items():
            if name.startswith('attr_'):
                field.widget.attrs.update({'class': checkbox_style})

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        ).distinct()