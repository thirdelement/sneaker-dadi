from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def cart_contents(request):
    cart_items = []
    total = 0
    product_count = 0
    # Get cart if it exists or initialize to an empty dict if not
    cart = request.session.get('cart', {})
    # Iterate through all items in cart and tally total cost and product count.
    for item_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=item_id)
        for size, quantity in quantity["items_by_size"].items():
            # If product is on sale use the sale price
            if product.on_sale is True:
                total += quantity * Decimal(product.price * (100 - product.discount_percent) / 100).quantize(Decimal('0.00'))
            else:
                total += quantity * product.price
            product_count += quantity
            cart_items.append({
                'item_id': item_id,
                'size': size, 
                'quantity': quantity,
                'product': product,
                })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # delivery = 5.95
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    order_total = delivery + total
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'order_total': order_total,
    }

    return context