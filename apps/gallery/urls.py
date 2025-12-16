from django.urls import path

from . import views

app_name = 'gallery'

urlpatterns = [
    path('galerie/', views.GalleryView.as_view(), name='gallery'),
    path('galerie/<slug:slug>/', views.CategoryListView.as_view(), name='category'),
    path('toile/<slug:slug>/', views.PaintingDetailView.as_view(), name='painting_detail'),
    path('recherche/', views.SearchView.as_view(), name='search'),
]

