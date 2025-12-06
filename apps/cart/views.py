from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .cart import Cart
from .forms import CartAddProductForm
from catalog.recommender import Recommender
from coupons.forms import CouponApplyForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd["quantity"],
            override_quantity=cd["quantity"]
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        item_qty = 0
        item_total_price = 0

        if str(product_id) in cart.cart:
            item_qty = cart.cart[str(product_id)]['quantity']
            item_total_price = item_qty * product.price

        return JsonResponse({
            'success': True,
            'unique_count': cart.unique_count,
            'cart_total_price': cart.get_total_price_after_discount(),
            'item_total_price': item_total_price,
            'cart_subtotal': cart.get_total_price(),
            'cart_discount': cart.get_discount(),
            'item_qty': item_qty,
            'product_id': product_id
        })

    return redirect("cart:cart_detail")

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    coupon_apply_form = CouponApplyForm(request.POST)
    r = Recommender()
    cart_products = [item['product'] for item in cart]

    if cart_products:
        recommended_products = r.suggest_products_for(cart_products, max_results=4)
    else:
        recommended_products = []

    return render(request, "cart/detail.html", {"cart": cart, 'coupon_apply_form': coupon_apply_form, 'recommended_products': recommended_products})
