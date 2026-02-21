from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import Painting, Category, Finish


class CategoryListView(ListView):
    """List paintings in a category with pagination and filters"""
    model = Painting
    template_name = 'pages/category.html'
    context_object_name = 'paintings'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        queryset = Painting.objects.filter(
            category=self.category,
            is_active=True
        ).select_related('category', 'finish').prefetch_related('images')

        # Apply filters
        finish = self.request.GET.get('finish')
        if finish:
            queryset = queryset.filter(finish__id=finish)

        status = self.request.GET.get('status')
        if status:
            if status == 'available':
                queryset = queryset.filter(status__in=['available_maison_pere', 'available_direct'])
            else:
                queryset = queryset.filter(status=status)

        price_min = self.request.GET.get('price_min')
        if price_min:
            queryset = queryset.filter(price_cad__gte=price_min)

        price_max = self.request.GET.get('price_max')
        if price_max:
            queryset = queryset.filter(price_cad__lte=price_max)

        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['price_cad', '-price_cad', 'title', '-title', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['finishes'] = Finish.objects.all()
        context['current_filters'] = {
            'finish': self.request.GET.get('finish', ''),
            'status': self.request.GET.get('status', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        return context


class PaintingDetailView(DetailView):
    """Detail view for a single painting"""
    model = Painting
    template_name = 'pages/painting_detail.html'
    context_object_name = 'painting'

    def get_queryset(self):
        return Painting.objects.filter(is_active=True).select_related(
            'category', 'finish'
        ).prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Related paintings from same category
        if self.object.category:
            context['related_paintings'] = Painting.objects.filter(
                category=self.object.category,
                is_active=True
            ).exclude(pk=self.object.pk).select_related('category').prefetch_related('images')[:4]
        else:
            context['related_paintings'] = []
        return context


class SearchView(ListView):
    """Search paintings by title"""
    model = Painting
    template_name = 'pages/search.html'
    context_object_name = 'paintings'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Painting.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query),
                is_active=True
            ).select_related('category', 'finish').prefetch_related('images')
        return Painting.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class GalleryView(ListView):
    """All paintings with filters"""
    model = Painting
    template_name = 'pages/gallery.html'
    context_object_name = 'paintings'
    paginate_by = 12

    def get_queryset(self):
        queryset = Painting.objects.filter(
            is_active=True
        ).select_related('category', 'finish').prefetch_related('images')

        # Apply filters
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        finish = self.request.GET.get('finish')
        if finish:
            queryset = queryset.filter(finish__id=finish)

        status = self.request.GET.get('status')
        if status:
            if status == 'available':
                queryset = queryset.filter(status__in=['available_maison_pere', 'available_direct'])
            else:
                queryset = queryset.filter(status=status)

        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['price_cad', '-price_cad', 'title', '-title', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['finishes'] = Finish.objects.all()
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'finish': self.request.GET.get('finish', ''),
            'status': self.request.GET.get('status', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        return context

