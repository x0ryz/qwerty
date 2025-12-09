from decimal import Decimal
from django.conf import settings
from catalog.models import ProductVariant
from coupons.models import Coupon


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self):
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product')
        cart = self.cart.copy()

        for variant in variants:
            item = cart[str(variant.id)]
            item["product"] = variant.product
            item["variant"] = variant
            item["price"] = variant.price
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def add(self, variant, quantity=1, override_quantity=False):
        variant_id = str(variant.id)
        if variant_id not in self.cart:
            self.cart[variant_id] = {"quantity": 0}

        if override_quantity:
            self.cart[variant_id]["quantity"] = quantity
        else:
            self.cart[variant_id]["quantity"] += quantity

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, variant):
        variant_id = str(variant.id)

        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self)

    @property
    def unique_count(self):
        return len(self.cart)

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        if 'coupon_id' in self.session:
            del self.session['coupon_id']
        self.save()

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
