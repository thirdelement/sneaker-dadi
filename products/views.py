from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower

from .models import Product, Category, ProductReview
from .forms import ProductForm, ReviewAdd


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
    
    current_sorting = f'{sort}_{direction}'

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
    reviewCheck = ProductReview.objects.filter(user=request.user, product=product).count()
    if request.user.is_authenticated:
        if reviewCheck > 0:
            can_add_review = False
    # End check

    context = {
        'product': product,
        'reviewForm': reviewForm, 
        'can_add_review': can_add_review
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
    review = ProductReview.objects.create(
        user=user,
        product=product,
        review_text=request.POST['review_text'],
        review_rating=request.POST['review_rating'],
        )
    data = {
        # 'user': user.username,
        # 'review_text': request.POST['review_text'],
        # 'review_rating': request.POST['review_rating']
    }

    # # Fetch avg rating for reviews
    # avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating = Avg('review_rating'))
    # # End

    # return JsonResponse({'bool': True, 'data': data, 'avg_reviews': avg_reviews})
    return JsonResponse({'bool': True, 'data': data})