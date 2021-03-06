from django.shortcuts import render,\
     redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages

from products.models import Product


def view_cart(request):
    """ A view that renders the cart contents page """

    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """ Add a product to the shopping cart """

    # get quantity from form and convert to integer as string on form
    quantity = int(request.POST.get('quantity'))
    size = request.POST['size']
    """
    Get the redirect URL from the form so 
    we know where to redirect once finished
    """
    redirect_url = request.POST.get('redirect_url')
    # get the cart if it exists or initialize to an empty dict if it doesn't
    cart = request.session.get('cart', {})

    # If there's already a key in the cart matching the item_id
    if item_id in list(cart.keys()):
        # Check if another item of same ID and size already exists
        if size in cart[item_id]['items_by_size'].keys():
            # Increment quantity for that key
            cart[item_id]['items_by_size'][size] += quantity
            messages.success(request, ' ')
        else:
            # If item size does not exist set size amount equal to quantity
            cart[item_id]['items_by_size'][size] = quantity
            messages.success(request, ' ')
    # If item not in cart
    else:
        # Add to item, size and quantity to cart 
        cart[item_id] = {'items_by_size': {size: quantity}}
        messages.success(request, ' ')
        
    # Overwrite the variable in the session with the updated version 
    request.session['cart'] = cart
    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""

    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('cart', {})
    size = request.POST['size']
    
    """
    If quantity is greater than zero and 
    less than 100 set the item size quantity
    """
    if 0 < quantity < 100:
        if item_id in list(cart.keys()):
            if size in cart[item_id]['items_by_size'].keys():
                cart[item_id]['items_by_size'][size] = quantity
                messages.success(request, ' ')
        else:
            del cart[item_id]['items_by_size'][size]
            if not cart[item_id]['items_by_size']:
                cart.pop(item_id)
                messages.success(request, ' ')
    
    request.session['cart'] = cart
    return redirect(reverse('view_cart'))


def remove_from_cart(request, item_id):
    """Remove the item from the shopping cart"""

    try:
        size = request.POST['size']
        cart = request.session.get('cart', {})

        # Delete the size key in the items_by_size dict
        del cart[item_id]['items_by_size'][size]
        # If items_by_size dict is now empty remove entire item
        if not cart[item_id]['items_by_size']:
            cart.pop(item_id)
        messages.success(request, 'Product removed from cart.')

        request.session['cart'] = cart
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)