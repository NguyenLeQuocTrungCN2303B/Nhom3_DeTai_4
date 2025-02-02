from django.urls import path
from . import views

urlpatterns = [
    path('A_Product_Mng/', views.customer, name='Customer'),
    path('A_Product_Mng/', views.product, name='Product'),
]