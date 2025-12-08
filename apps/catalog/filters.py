import django_filters
from django import forms
from django.db.models import Q
from .models import Product, Brand, Category, Switch, Color


class ProductFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(
        method='filter_search',
        label='Search',
    )

    min_price = django_filters.NumberFilter(
        field_name='variants__price',
        lookup_expr='gte',
        label='Min Price',
    )
    max_price = django_filters.NumberFilter(
        field_name='variants__price',
        lookup_expr='lte',
        label='Max Price',
    )

    brand = django_filters.ModelMultipleChoiceFilter(
        queryset=Brand.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Brands'
    )

    switches = django_filters.ModelMultipleChoiceFilter(
        field_name='variants__switch',
        queryset=Switch.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Switches'
    )

    colors = django_filters.ModelMultipleChoiceFilter(
        field_name='variants__color',
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Colors'
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
        super().__init__(*args, **kwargs)

        self.form.fields['query'].widget.attrs.update({
            'placeholder': 'Search...',
            'class': 'w-full bg-gray-50 border-2 border-black p-2 font-mono text-sm'
        })

        self.form.fields['min_price'].widget.attrs.update({
            'placeholder': '0',
            'class': 'w-full bg-gray-50 border-2 border-black p-2 font-mono text-sm'
        })
        self.form.fields['max_price'].widget.attrs.update({
            'placeholder': '1000',
            'class': 'w-full bg-gray-50 border-2 border-black p-2 font-mono text-sm'
        })

        checkbox_class = 'appearance-none w-4 h-4 border-2 border-black bg-white checked:bg-black transition-colors cursor-pointer mr-2'

        self.form.fields['brand'].widget.attrs.update({'class': checkbox_class})
        self.form.fields['switches'].widget.attrs.update({'class': checkbox_class})
        self.form.fields['colors'].widget.attrs.update({'class': checkbox_class})

        self.form.fields['o'].widget.attrs.update({
            'class': 'bg-white border-2 border-black p-1 font-mono text-sm focus:outline-none cursor-pointer'
        })

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )