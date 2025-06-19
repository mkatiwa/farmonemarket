from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
import datetime
import json

from orders.models import Order, OrderItem
from products.models import Product, Category


class FarmerDashboardView(LoginRequiredMixin, View):
    """
    View for farmer dashboard
    """
    def get(self, request):
        # Check if user is a farmer
        if not request.user.is_farmer:
            messages.error(request, 'Only farmers can access the farmer dashboard.')
            return redirect('products:list')

        # Get farmer's products
        products = Product.objects.filter(farmer=request.user)
        total_products = products.count()
        active_products = products.filter(status='available').count()
        out_of_stock_products = products.filter(status='out_of_stock').count()
        hidden_products = products.filter(status='hidden').count()

        # Get products with low stock
        low_stock_products = products.filter(
            status='available', 
            stock_quantity__lte=5
        )

        # Get orders containing farmer's products
        order_items = OrderItem.objects.filter(farmer=request.user)

        # Get total orders
        total_orders = Order.objects.filter(
            items__farmer=request.user
        ).distinct().count()

        # Get pending orders
        pending_orders = Order.objects.filter(
            items__farmer=request.user,
            order_status='pending'
        ).distinct().count()

        # Get processing orders
        processing_orders = Order.objects.filter(
            items__farmer=request.user,
            order_status__in=['processing', 'shipped']
        ).distinct().count()

        # Get completed orders
        completed_orders = Order.objects.filter(
            items__farmer=request.user,
            order_status='delivered'
        ).distinct().count()

        # Calculate monthly revenue
        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = order_items.filter(
            order__order_status='paid',
            order__created_at__gte=first_day_of_month
        ).aggregate(
            total=Sum('product_price')
        )['total'] or 0

        # Calculate total revenue
        total_revenue = order_items.filter(
            order__order_status='paid'
        ).aggregate(
            total=Sum('product_price')
        )['total'] or 0

        # Calculate average order value
        avg_order_value = order_items.filter(
            order__order_status='paid'
        ).values('order').annotate(
            order_total=Sum('product_price')
        ).aggregate(
            avg=Avg('order_total')
        )['avg'] or 0

        # Get recent orders
        recent_orders = Order.objects.filter(
            items__farmer=request.user
        ).distinct().order_by('-created_at')[:5]

        # Get top selling products
        top_products = order_items.values(
            'product_name'
        ).annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('product_price'))
        ).order_by('-total_sold')[:5]

        # Get sales data for chart (last 7 days)
        today = timezone.now().date()
        sales_data = []
        for i in range(6, -1, -1):
            day = today - datetime.timedelta(days=i)
            day_sales = order_items.filter(
                order__created_at__date=day,
                order__order_status='paid'
            ).aggregate(
                total=Sum('product_price')
            )['total'] or 0
            sales_data.append({
                'date': day.strftime('%a'),
                'sales': float(day_sales)
            })

        context = {
            'total_products': total_products,
            'active_products': active_products,
            'out_of_stock_products': out_of_stock_products,
            'hidden_products': hidden_products,
            'low_stock_products': low_stock_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'completed_orders': completed_orders,
            'monthly_revenue': monthly_revenue,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'recent_orders': recent_orders,
            'top_products': top_products,
            'sales_data': json.dumps(sales_data),
            'products': products,
        }

        return render(request, 'dashboard/farmer_dashboard.html', context)


class BuyerDashboardView(LoginRequiredMixin, View):
    """
    View for buyer dashboard
    """
    def get(self, request):
        # Check if user is a buyer
        if not request.user.is_buyer:
            messages.error(request, 'Only buyers can access the buyer dashboard.')
            return redirect('products:list')

        # Get buyer's orders
        orders = Order.objects.filter(customer=request.user)
        total_orders = orders.count()
        pending_orders = orders.filter(order_status='pending').count()

        # Calculate total spent
        total_spent = orders.filter(
            order_status='paid'
        ).aggregate(
            total=Sum('items__product_price')
        )['total'] or 0

        # Get recent orders
        recent_orders = orders.order_by('-created_at')[:5]

        # Get favorite products (most ordered)
        favorite_products = OrderItem.objects.filter(
            order__customer=request.user
        ).values(
            'product_name'
        ).annotate(
            count=Count('product_name')
        ).order_by('-count').count()

        # Get new products
        new_products = Product.objects.filter(
            status='available'
        ).order_by('-created_at')[:4]

        context = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_spent': total_spent,
            'recent_orders': recent_orders,
            'favorite_products': favorite_products,
            'new_products': new_products,
        }

        return render(request, 'dashboard/buyer_dashboard.html', context)


class FarmerProductsView(LoginRequiredMixin, View):
    """
    View for managing farmer's products
    """
    def get(self, request):
        # Check if user is a farmer
        if not request.user.is_farmer:
            messages.error(request, 'Only farmers can access this page.')
            return redirect('products:list')

        # Get query parameters
        status_filter = request.GET.get('status', 'all')
        category_filter = request.GET.get('category', 'all')
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', 'name')

        # Get farmer's products
        products = Product.objects.filter(farmer=request.user)

        # Apply filters
        if status_filter != 'all':
            products = products.filter(status=status_filter)

        if category_filter != 'all':
            products = products.filter(category__id=category_filter)

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Apply sorting
        if sort_by == 'name':
            products = products.order_by('name')
        elif sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'stock_low':
            products = products.order_by('stock_quantity')
        elif sort_by == 'stock_high':
            products = products.order_by('-stock_quantity')
        elif sort_by == 'newest':
            products = products.order_by('-created_at')
        elif sort_by == 'oldest':
            products = products.order_by('created_at')

        # Get categories for filter dropdown
        categories = Category.objects.all()

        context = {
            'products': products,
            'categories': categories,
            'status_filter': status_filter,
            'category_filter': category_filter,
            'search_query': search_query,
            'sort_by': sort_by,
        }

        return render(request, 'dashboard/farmer_products.html', context)


class FarmerOrdersView(LoginRequiredMixin, View):
    """
    View for managing farmer's orders
    """
    def get(self, request):
        # Check if user is a farmer
        if not request.user.is_farmer:
            messages.error(request, 'Only farmers can access this page.')
            return redirect('products:list')

        # Get query parameters
        status_filter = request.GET.get('status', 'all')
        date_filter = request.GET.get('date', 'all')
        search_query = request.GET.get('search', '')

        # Get orders containing farmer's products
        orders = Order.objects.filter(
            items__farmer=request.user
        ).distinct().order_by('-created_at')

        # Apply filters
        if status_filter != 'all':
            orders = orders.filter(order_status=status_filter)

        if date_filter == 'today':
            today = timezone.now().date()
            orders = orders.filter(created_at__date=today)
        elif date_filter == 'week':
            week_ago = timezone.now().date() - datetime.timedelta(days=7)
            orders = orders.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = timezone.now().date() - datetime.timedelta(days=30)
            orders = orders.filter(created_at__date__gte=month_ago)

        if search_query:
            orders = orders.filter(
                Q(uuid__icontains=search_query) |
                Q(customer__email__icontains=search_query) |
                Q(customer__first_name__icontains=search_query) |
                Q(customer__last_name__icontains=search_query)
            )

        context = {
            'orders': orders,
            'status_filter': status_filter,
            'date_filter': date_filter,
            'search_query': search_query,
        }

        return render(request, 'dashboard/farmer_orders.html', context)


class FarmerAnalyticsView(LoginRequiredMixin, View):
    """
    View for farmer analytics
    """
    def get(self, request):
        # Check if user is a farmer
        if not request.user.is_farmer:
            messages.error(request, 'Only farmers can access this page.')
            return redirect('products:list')

        # Get query parameters
        period = request.GET.get('period', 'month')

        # Get orders containing farmer's products
        order_items = OrderItem.objects.filter(farmer=request.user)

        # Set date range based on period
        today = timezone.now().date()
        if period == 'week':
            start_date = today - datetime.timedelta(days=7)
            date_format = '%a'  # Day of week
            delta = datetime.timedelta(days=1)
        elif period == 'month':
            start_date = today - datetime.timedelta(days=30)
            date_format = '%d %b'  # Day and month
            delta = datetime.timedelta(days=1)
        elif period == 'year':
            start_date = today - datetime.timedelta(days=365)
            date_format = '%b'  # Month
            delta = datetime.timedelta(days=30)
        else:  # Default to month
            start_date = today - datetime.timedelta(days=30)
            date_format = '%d %b'
            delta = datetime.timedelta(days=1)

        # Get sales data for chart
        sales_data = []
        current_date = start_date
        while current_date <= today:
            if period == 'year':
                # For yearly view, group by month
                month_start = current_date.replace(day=1)
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - datetime.timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1, day=1) - datetime.timedelta(days=1)

                day_sales = order_items.filter(
                    order__created_at__date__gte=month_start,
                    order__created_at__date__lte=month_end,
                    order__order_status='paid'
                ).aggregate(
                    total=Sum('product_price')
                )['total'] or 0

                sales_data.append({
                    'date': month_start.strftime(date_format),
                    'sales': float(day_sales)
                })

                current_date = month_end + datetime.timedelta(days=1)
            else:
                # For daily view
                day_sales = order_items.filter(
                    order__created_at__date=current_date,
                    order__order_status='paid'
                ).aggregate(
                    total=Sum('product_price')
                )['total'] or 0

                sales_data.append({
                    'date': current_date.strftime(date_format),
                    'sales': float(day_sales)
                })

                current_date += delta

        # Get top selling products
        top_products = order_items.values(
            'product_name'
        ).annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('product_price'))
        ).order_by('-total_sold')[:10]

        # Get sales by category
        category_sales = order_items.filter(
            product__isnull=False
        ).values(
            'product__category__name'
        ).annotate(
            total=Sum(F('quantity') * F('product_price'))
        ).order_by('-total')

        # Calculate total revenue
        total_revenue = order_items.filter(
            order__order_status='paid'
        ).aggregate(
            total=Sum('product_price')
        )['total'] or 0

        # Calculate average order value
        avg_order_value = order_items.filter(
            order__order_status='paid'
        ).values('order').annotate(
            order_total=Sum('product_price')
        ).aggregate(
            avg=Avg('order_total')
        )['avg'] or 0

        context = {
            'sales_data': json.dumps(sales_data),
            'top_products': top_products,
            'category_sales': category_sales,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'period': period,
        }

        return render(request, 'dashboard/farmer_analytics.html', context)


class FarmerInventoryView(LoginRequiredMixin, View):
    """
    View for managing farmer's inventory
    """
    def get(self, request):
        # Check if user is a farmer
        if not request.user.is_farmer:
            messages.error(request, 'Only farmers can access this page.')
            return redirect('products:list')

        # Get query parameters
        status_filter = request.GET.get('status', 'all')
        category_filter = request.GET.get('category', 'all')
        stock_filter = request.GET.get('stock', 'all')

        # Get farmer's products
        products = Product.objects.filter(farmer=request.user)

        # Apply filters
        if status_filter != 'all':
            products = products.filter(status=status_filter)

        if category_filter != 'all':
            products = products.filter(category__id=category_filter)

        if stock_filter == 'low':
            products = products.filter(stock_quantity__lte=5)
        elif stock_filter == 'out':
            products = products.filter(stock_quantity=0)

        # Get categories for filter dropdown
        categories = Category.objects.all()

        # Get low stock products
        low_stock_products = products.filter(
            status='available', 
            stock_quantity__lte=5
        ).count()

        # Get out of stock products
        out_of_stock_products = products.filter(
            status='out_of_stock'
        ).count()

        context = {
            'products': products,
            'categories': categories,
            'status_filter': status_filter,
            'category_filter': category_filter,
            'stock_filter': stock_filter,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
        }

        return render(request, 'dashboard/farmer_inventory.html', context)


class UpdateInventoryView(LoginRequiredMixin, View):
    """
    View for updating product inventory
    """
    def post(self, request, product_id):
        # Check if user is a farmer
        if not request.user.is_farmer:
            return JsonResponse({'success': False, 'message': 'Only farmers can update inventory.'})

        product = get_object_or_404(Product, id=product_id, farmer=request.user)

        try:
            new_quantity = int(request.POST.get('quantity', 0))
            new_status = request.POST.get('status', product.status)

            if new_quantity < 0:
                return JsonResponse({'success': False, 'message': 'Quantity cannot be negative.'})

            product.stock_quantity = new_quantity
            product.status = new_status
            product.save()

            return JsonResponse({
                'success': True, 
                'message': 'Inventory updated successfully.',
                'new_quantity': new_quantity,
                'new_status': product.get_status_display()
            })
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid quantity value.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
