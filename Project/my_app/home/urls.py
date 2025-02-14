from django.contrib import admin
from django.urls import include, path
from .import views
urlpatterns = [
    path('', views.indext, name='indext'),
    path('products/', views.products, name='products'),
    path('edit-product/', views.edit_product, name='edit-product'),
    path('gold-price/', views.gold_price, name='gold-price'),
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),
    path('detail/', views.detail, name='detail'),
    path('update_item/', views.updateItem, name='update_item'),
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('category/', views.category, name='category'),
]