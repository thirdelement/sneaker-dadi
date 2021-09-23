from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order, OrderLineItem


@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, ' ')
        else:
            messages.error(request, 'Update failed. Please ensure \
                the form is valid.')
    else:
        form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile': True
    }

    return render(request, template, context)


@login_required
def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    profile = get_object_or_404(UserProfile, user=request.user)
    # Check profile is the same as profile that ordered
    if profile == order.user_profile:
        messages.info(request, (
            f'This is a past confirmation for order number {order_number}. '
            'A confirmation email was sent on the order date.'
        ))
    else:
        messages.error(request, 'Sorry, that order is not available.')
        return redirect(reverse('home'))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order, 
        'from_profile': True,
    }

    return render(request, template, context)