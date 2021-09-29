from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, ProductReview


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    image1 = forms.ImageField(
        label='Image1', required=False, widget=CustomClearableFileInput)
    image2 = forms.ImageField(
        label='Image2', required=False, widget=CustomClearableFileInput)
    image3 = forms.ImageField(
        label='Image3', required=False, widget=CustomClearableFileInput)
    image4 = forms.ImageField(
        label='Image4', required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names


# Review Form
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        exclude = ('user', 'product', 'created_on')
