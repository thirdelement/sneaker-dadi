from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.db.models.functions import Lower

from .models import Product, Category, ProductReview
from profiles.models import UserProfile
from .forms import ProductForm, ReviewForm
from checkout.models import OrderLineItem


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
            if sortkey == 'average_rating' and direction == 'desc':
                """
                Sorting nulls last using F expression.
                Credit: 
                https://docs.djangoproject.com/en/3.1/ref/models/
                expressions/#using-f-to-sort-null-values
                https://github.com/Edb83/moose-juice/blob/master/products/views.py
                """
                products = products.order_by(F(
                    'average_rating').desc(nulls_last=True))
            else:
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
                messages.error(request, "You didn't enter\
                     any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(
                name__icontains=query) | Q(
                    description__icontains=query)
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
    form = ReviewForm()

    can_add_review = True
 
    # Check if user has added product review and if so show this on form
    if request.user.is_authenticated:
        reviewCheck = ProductReview.objects.filter(
            user=request.user, product=product).count()
        if reviewCheck > 0:
            can_add_review = False
            review = get_object_or_404(
                ProductReview, product=product, user=request.user)
            form = ReviewForm(instance=review)

    # Get reviews
    reviews = ProductReview.objects.filter(product=product)

    # Get number of reviews
    # Credit: Great Adib - https://www.youtube.com/watch?v=MmLRE2fCcec&t=46s
    num_reviews = ProductReview.objects.filter(product=product).count()

    # Get related products
    related_products_male = Product.objects.filter(
        category=product.category).exclude(
            product_id=product.product_id).order_by('-gender')
    related_products_female = Product.objects.filter(
        category=product.category).exclude(
            product_id=product.product_id).order_by('gender')
    context = {
        'product': product,
        'form': form, 
        'can_add_review': can_add_review,
        'reviews': reviews,
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
            messages.error(request, 'Failed to add product. Please ensure the \
                form is valid.')
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
            messages.success(
                request, 'Successfully updated product!', extra_tags=' ')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure \
                the form is valid.')
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


@login_required
def add_review(request, product_id):
    """ Add product review """
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        profile = get_object_or_404(UserProfile, user_id=request.user)
    else:
        profile = None

    if not request.user.is_authenticated:
        messages.error(request, 'Sorry, you have to be logged in to do that.', extra_tags=' ')
        return redirect(reverse('product_detail', args=[product.id]))

    elif request.user.is_authenticated:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                # Check whether user has ordered product previously
                # Credit: 
                # https://github.com/Edb83/moose-juice/blob/master/products/views.py
                if OrderLineItem.objects.filter(
                    order__user_profile=profile).filter(
                        product=product).exists():
                    review.verified_purchase = True
                review.save()
                # Save average rating to database
                product.save_average_rating()
                messages.success(request, 'You have successfully added a \
                    review.', extra_tags=' ')
                return redirect(reverse('product_detail', args=[product.id]))
            else:
                messages.error(
                    request,
                    "There was a problem adding the review.  Please check and \
                        try again.")
    else:
        form = ReviewForm()
    context = {
        'form': form,
        'profile': profile
    }

    return render(request, context)


@login_required
def delete_review(request, review_id):
    """ Delete review """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    elif request.user.is_superuser:
        review = ProductReview.objects.filter(pk=review_id).last()
        # review = ProductReview.objects.filter(pk=review_id)
        product_id = review.product_id
        review.delete()
        # Save average rating to database
        review.product.save_average_rating()
        messages.success(request, f"{ review.user }'s review has been \
        deleted.", extra_tags=' ')
        return redirect(reverse('product_detail', args=[product_id]))


@login_required
def edit_review(request, review_id):
    """ Edit product review """
    review = get_object_or_404(ProductReview, pk=review_id)
    product = review.product
    if not request.user.is_authenticated:
        messages.error(request, 'Sorry, you have to be logged in to do that.', extra_tags=' ')
        return redirect(reverse('product_detail', args=[product.id]))

    elif request.user.is_authenticated:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                # Save average rating to database
                product.save_average_rating()
                messages.success(request, 'Your review has been updated.', extra_tags=' ')
                return redirect(reverse('product_detail', args=[product.id]))
            else:
                messages.error(
                    request,
                    "The review update failed.  Please check and try again.", extra_tags=' ')
        else:
            form = ReviewForm(instance=review)

        context = {
            'form': form,
            'review': review,
            'product': product
        }

        return render(request, 'products/product_detail.html', context)


def products_on_sale(request):
    """ A view to show all products on sale, including sorting. """
    sort = None
    direction = None
    products = Product.objects.filter(on_sale=True)

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'average_rating' and direction == 'desc':
                # Sorting nulls last using F expression
                products = products.order_by(F(
                    'average_rating').desc(nulls_last=True))
            else:
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
