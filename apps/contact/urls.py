from django.urls import path

from . import views

app_name = 'contact'

urlpatterns = [
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('api/purchase-inquiry/', views.purchase_inquiry, name='purchase_inquiry'),
]

