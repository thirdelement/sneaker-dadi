from django.db import models
from multiselectfield import MultiSelectField
from decimal import Decimal


# Create your models here.
class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    SIZE_CHOICES = (
        ('4/37', '4/37'),
        ('5/38', '5/38'),
        ('6/39', '6/39'),
        ('7/41', '7/41'),
        ('8/42', '8/42'),
        ('9/43', '9/43'),
        ('10/44', '10/44'),
        ('11/45', '11/45'),
        ('11.5/46', '11.5/46'),
    )
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    product_id = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # sale_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    on_sale = models.BooleanField(default=False)
    # discount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    discount_percent = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    size = MultiSelectField(choices=SIZE_CHOICES)
    gender = models.CharField(max_length=1)
    image1 = models.ImageField(null=True, blank=True)
    image2 = models.ImageField(null=True, blank=True)
    image3 = models.ImageField(null=True, blank=True)
    image4 = models.ImageField(null=True, blank=True)
     
    def __str__(self):
        return self.name
  
    def get_sale_price(self):
        '''Calculate cost with discount percentage
        Credit: https://helperbyte.com/questions/77886/django-how-to-make-a-discount-for-the-item
        '''
        sale = Decimal(self.price * (100 - self.discount_percent) / 100).quantize(Decimal('0.00'))
        return sale
    
    def clean(self):
        '''Raise validation error if on_sale is True and discount_percent field is empty 
        Credit: https://stackoverflow.com/questions/13440097/django-modelform-booleanfield-required-field-is-not-working
        '''
        from django.core.exceptions import ValidationError
        if self.on_sale and not self.discount_percent:
            raise ValidationError("Discount percent is a required field.")
        