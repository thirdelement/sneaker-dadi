from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Q
from django.db.models.functions import Lower, Round

from .models import Product, Category, ProductReview
from .forms import ProductForm, ReviewAdd

from datetime import datetime
from decimal import Decimal


def all_products(request):
    """" A view to show all products, including sorting and search queries. """

    products = Product.objects.all()
    query = None
    categories = None
    gender = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
        
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories) 
            categories = Category.objects.filter(name__in=categories)
            
        if 'gender' in request.GET:
            gender = request.GET['gender'].split(',')
            products = products.filter(gender__in=gender)
            gender = Product.objects.filter(gender__in=gender)  
            
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)
    
    current_sorting = f'{sort}+{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_gender': gender, 
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """" A view to show individual product details. """

    product = get_object_or_404(Product, pk=product_id)
    reviewForm = ReviewAdd()

    # Check if user has added product review
    # Credit: Code Artisan Lab - https://www.youtube.com/watch?v=kcMfRJ7AGJY&list=PLgnySyq8qZmrxJvJbZC1eb7PD4bu0a-sB&index=32
    can_add_review = True
    if request.user.is_authenticated:
        reviewCheck = ProductReview.objects.filter(user=request.user, product=product).count()
        if reviewCheck > 0:
            can_add_review = False

    # Get reviews
    reviews = ProductReview.objects.filter(product=product)
    
    # Get avg rating for reviews
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))

    # Get number of reviews
    # Credit: Great Adib - https://www.youtube.com/watch?v=MmLRE2fCcec&t=46s
    num_reviews = ProductReview.objects.filter(product=product).count()

    # Get related products
    related_products_male = Product.objects.filter(category=product.category).exclude(product_id=product.product_id).order_by('-gender')[:4]
    related_products_female = Product.objects.filter(category=product.category).exclude(product_id=product.product_id).order_by('gender')[:4]
    print('Related products female', related_products_female)
    context = {
        'product': product,
        'reviewForm': reviewForm, 
        'can_add_review': can_add_review,
        'reviews': reviews,
        'avg_reviews': avg_reviews,
        'num_reviews': num_reviews,
        'related_products_male': related_products_male,
        'related_products_female': related_products_female,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # Add extra_tags to identify message in toast_success.html
            messages.success(request, 'Successfully updated product!', extra_tags=' ')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
        'on_edit_product': True
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
      
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))


# Save Review
# Credit: Code Artisan Lab - https://www.youtube.com/watch?v=7tyMyLCjKVg&list=PLgnySyq8qZmrxJvJbZC1eb7PD4bu0a-sB&index=31
@login_required
def save_review(request, product_id):
    product = Product.objects.get(pk=product_id)
    user = request.user
    date = datetime.now()
    review = ProductReview.objects.create(
        user=user,
        product=product,
        review_text=request.POST['review_text'],
        review_rating=request.POST['review_rating'],
        )
    data = {
        'user': user.username,
        'review_text': request.POST['review_text'],
        'review_rating': request.POST['review_rating'],
        'created_on': date.strftime("%d %B %Y"),
        'review_id': review.id,
    }

    # Get avg rating for reviews
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    # Save average rating to database
    product.save_average_rating()

    return JsonResponse({'bool': True, 'data': data, 'avg_reviews': avg_reviews})
    

# Delete review
@login_required
def delete_review(request, review_id):
    review = ProductReview.objects.filter(pk=review_id).last()
    product_id = review.product_id
    review.delete()
    messages.success(request, 'Review deleted!')
    return redirect(reverse('product_detail', args=[product_id]))


# Delete review
# @login_required
# def edit_review(request, review_id):
    # review = ProductReview.objects.filter(pk=review_id).last()
    # product_id = review.product_id
    # review.delete()
    # messages.success(request, 'Review deleted!')
    # return redirect(reverse('product_detail', args=[product_id]))

def products_on_sale(request):
    """" A view to show all products on sale, including sorting. """
    sort = None
    direction = None
    products = Product.objects.filter(on_sale=True)

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

    current_sorting = f'{sort}+{direction}'
   
    context = {
        'products': products,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products_on_sale.html', context)
