
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number',
        'product_name',
        'mrr_number',
        'date',
        'total_received',
        'distributed',
        'remaining',
        'unit_price',
        'total_price',
    )
    list_filter = ('date', 'product_name',)
    search_fields = ('product_name', 'mrr_number',)
    readonly_fields = ('remaining', 'total_price')
    ordering = ('-date',)
