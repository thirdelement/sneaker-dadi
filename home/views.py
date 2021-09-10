from django.shortcuts import render
from django.db.models import Sum

from products.models import Product
from django.db.models import F


# Top two selling products for male and female
def top_sellers(request):
    # Most sold male product
    # Credit: https://stackoverflow.com/questions/9278796/ordering-a-query-by-aggregate-sum-in-django-but-not-getting-result-as-expected
    top_sellers_male = Product.objects.filter(gender='m').annotate(total_quantity=Sum('orderlineitem__quantity')).order_by(F('total_quantity').desc(nulls_last=True))[:2]
    # Most sold female product
    top_sellers_female = Product.objects.filter(gender='f').annotate(total_quantity=Sum('orderlineitem__quantity')).order_by(F('total_quantity').desc(nulls_last=True))[:2]
    # Most recently sold male product
    trending_male = Product.objects.filter(gender='m').order_by(F('orderlineitem__order__date').desc(nulls_last=True))
    # Get top two distinct products
    # Credit: https://stackoverflow.com/questions/19283225/how-can-i-remove-duplicate-objects-in-an-order-by-query
    male_trender = set()
    male_trend_distinct = []
    for item in trending_male:
        if item not in male_trender:
            male_trend_distinct.append(item)
            male_trender.add(item)
    trending_male = male_trend_distinct[:2]
    # Most recently sold female product
    trending_female = Product.objects.filter(gender='f').order_by(F('orderlineitem__order__date').desc(nulls_last=True))
    # Get top two distinct products
    fem_trender = set()
    fem_trend_distinct = []
    for item in trending_female:
        if item not in fem_trender:
            fem_trend_distinct.append(item)
            fem_trender.add(item)
    trending_female = fem_trend_distinct[:2]
   
    context = {
        'top_sellers_male': top_sellers_male,
        'top_sellers_female': top_sellers_female,
        'trending_male': trending_male,
        'trending_female': trending_female, 
    }
  
    return render(request, 'home/index.html', context)
