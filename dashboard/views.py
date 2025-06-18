from datetime import timezone

from django.shortcuts import render
from django.views.generic import TemplateView

from orders.models import Order
from products.models import Product


# Create your views here.


def dashboard(request):
    user = request.user
    total_revenue = 0
    all_products = Product.objects.filter(user=user)
    out_of_stock = Product.objects.filter(is_out_of_stock=True)
    total_products = Product.objects.filter(user=user).count()
    orders = Order.objects.filter(user=user)
    recent_orders = orders.order_by('-created')[0:5]
    low_in_stock = [] # TODO

    rev = Order.objects.filter(user=user, status=Order.Status.PAID, created_at__lte=timezone.now()) # TODO
    for order in rev:
        total_revenue += order.total_price

    context = {
        'all_products': all_products,
        'out_of_stock': out_of_stock,
        'total_products': total_products,
        'orders': orders,
        'products': all_products,
        'total_revenue': total_revenue,
        "recent_orders": recent_orders,
    }

    return render(request, 'dashboard/dashboard.html', context=context)
