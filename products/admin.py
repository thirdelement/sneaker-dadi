from django.contrib import admin
from .models import Product, Category

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_id',
        'name',
        'category',
        'price',
        'gender',
        'image1',
    )

    ordering = ('product_id',)

    def clean(self):
        cleaned_data = super(ProductAdmin, self).clean()
        on_sale = cleaned_data.get("on_sale")
        discount_percent = cleaned_data.get("discount_percent")
        if on_sale and not discount_percent:
            raise forms.ValidationError("Discount percent is a required field.")
        return cleaned_data

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)