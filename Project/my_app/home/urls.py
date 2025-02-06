from django.contrib import admin
from django.urls import include, path
from .import views
urlpatterns = [
    path('', views.home, name='home'),
    path('products', views.products, name='products'),
    path('edit-product', views.edit_product, name='edit-product'),
    path('gold-price', views.gold_price, name='gold-price'),
]