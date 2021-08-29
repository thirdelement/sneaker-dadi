from django.db import models
from django.db.models import Avg, Count, Sum
from django.contrib.auth.models import User
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
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
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
    
    def get_average_rating(self):
        """
        Calculate average rating 
        Credit: https://stackoverflow.com/questions/11255243/how-to-get-average-across-different-models-in-django
        """
        reviews = ProductReview.objects.filter(product=self)
        count = len(reviews)
        sum = 0
        if count:
            for review in reviews:
                sum += int(review.review_rating)
            return (sum/count)
        else:
            return (0)


# Product review
# Credit: Code Artisan Lab - https://www.youtube.com/watch?v=7tyMyLCjKVg&list=PLgnySyq8qZmrxJvJbZC1eb7PD4bu0a-sB&index=31
RATING = (
    (1, '1'), 
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    review_text = models.TextField(max_length=250)
    review_rating = models.CharField(choices=RATING, max_length=150)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Reviews'

    def get_review_rating(self):
        return self.review_rating

