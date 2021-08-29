from django.shortcuts import render
from django.db.models import Sum

from products.models import Product 


# Top two selling products for male and female
def top_sellers(request):
    # Most sold male product
    top_sellers_male = Product.objects.filter(gender='m').annotate(total_quantity=Sum('orderlineitem__quantity')).order_by('-total_quantity')[:2]
    # Most sold female product
    top_sellers_female = Product.objects.filter(gender='f').annotate(total_quantity=Sum('orderlineitem__quantity')).order_by('-total_quantity')[:2]
    # Most recently sold male products
    trending_male = Product.objects.filter(gender='m').order_by('-orderlineitem__order__date')[:2]
    # Most recently sold female products
    trending_female = Product.objects.filter(gender='f').order_by('-orderlineitem__order__date')[:2]
    return render(request, 'home/index.html', {'top_sellers_male': top_sellers_male, 'top_sellers_female': top_sellers_female, 'trending_male': trending_male, 'trending_female': trending_female})
