from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from products.models import Product, Category
from django.http import JsonResponse


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/product_list.html'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(status='available').select_related('category', 'farmer')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category__name=category)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related products (same category)
        product = self.get_object()
        context['related_products'] = Product.objects.filter(
            category=product.category,
            status='available'
        ).exclude(id=product.id)[:4]
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'description', 'price', 'category', 'stock_quantity', 'status', 'image']
    success_url = reverse_lazy('products:list')

    def form_valid(self, form):
        form.instance.farmer = self.request.user
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_farmer:
            messages.error(request, 'Only farmers can add products.')
            return redirect('products:list')
        return super().dispatch(request, *args, **kwargs)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'description', 'price', 'category', 'stock_quantity', 'status', 'image']

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        if product.farmer != request.user:
            messages.error(request, 'You can only edit your own products.')
            return redirect('products:list')
        return super().dispatch(request, *args, **kwargs)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('products:list')

    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        if product.farmer != request.user:
            messages.error(request, 'You can only delete your own products.')
            return redirect('products:list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)


def debug_products(request):
    """Debug view to check products and categories"""
    products_count = Product.objects.count()
    available_products_count = Product.objects.filter(status='available').count()
    categories_count = Category.objects.count()
    
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    queryset = Product.objects.filter(status='available')
    
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    if category_filter:
        queryset = queryset.filter(category__name=category_filter)
    
    filtered_count = queryset.count()
    
    return JsonResponse({
        'total_products': products_count,
        'available_products': available_products_count,
        'categories': categories_count,
        'search_query': search_query,
        'category_filter': category_filter,
        'filtered_results': filtered_count,
        'categories_list': list(Category.objects.values('name')),
        'sample_products': list(Product.objects.filter(status='available').values('name', 'category__name')[:5])
    })
