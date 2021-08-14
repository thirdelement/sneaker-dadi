from django.shortcuts import render
from django.db.models import Count

from products.models import Product

from datetime import datetime, timedelta


def top_sellers(request):
    top_sellers_male = Product.objects.filter(gender='m').filter(orderlineitem__order__date__gte=datetime.now()-timedelta(days=30)).annotate(num_quantity=Count('orderlineitem__quantity'))[:2]
    top_sellers_female = Product.objects.filter(gender='f').filter(orderlineitem__order__date__gte=datetime.now()-timedelta(days=30)).annotate(num_quantity=Count('orderlineitem__quantity'))[:2]
    return render(request, 'home/index.html', {'top_sellers_male': top_sellers_male, 'top_sellers_female': top_sellers_female})