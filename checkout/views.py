from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from cart.contexts import cart_contents

import stripe


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        cart = request.session.get('cart', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # create an instance of the form using the form data
        order_form = OrderForm(form_data)
        # if form is valid iterate through the cart items 
        # to create each line item
        if order_form.is_valid():
            order = order_form.save()
            for item_id, quantity in cart.items():
                try:
                    # Get product ID from the cart
                    product = Product.objects.get(id=item_id)
                    # Iterate through each size and create a line item 
                    # accordingly
                    for size, quantity in quantity['items_by_size'].items():
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=quantity,
                            size=size,
                            )
                        order_line_item.save()
                # in case product is not found add an error msg & return user to cart
                except Product.DoesNotExist:
                    messages.error(request, (
                        "A product in your cart was not found in our database."
                        "Please contact us for assistance.")
                    )
                    order.delete()
                    return redirect(reverse('view_cart'))

            # Attach whether the user wanted to save their profile info & 
            # redirect to checkout_success 
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            # If order is not valid attach below message
            messages.error(request, 'There was an error with your form. \
                Please check your details.')
    # else if get method
    else: 

        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "There's nothing in your cart at the moment")
            return redirect(reverse('products'))

        current_cart = cart_contents(request)
        total = current_cart['order_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')
    
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # Get save info from the session to check if user wants to save details
    save_info = request.session.get('save_info')
    # Use the order number to get the order created and send back to the template
    order = get_object_or_404(Order, order_number=order_number)
    # Attach a success message
    messages.success(request, f'Your order number is {order_number}. \
        A confirmation email will be sent to {order.email}.')

    # Delete user shopping cart in the session as no longer needed
    if 'cart' in request.session:
        del request.session['cart']

    # Set template, context & render template
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'on_checkout_success': True,
    }

    return render(request, template, context)
