from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('a-propos/', views.AboutView.as_view(), name='about'),
    path('livraison-retour/', views.DeliveryView.as_view(), name='delivery'),
    path('termes-conditions/', views.TermsView.as_view(), name='terms'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('robots.txt', views.robots_txt, name='robots'),
]







