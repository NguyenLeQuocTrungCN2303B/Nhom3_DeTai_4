from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from A_Product_Mng.models import Product
# Create your views here.
def home(request):
    return render(request , 'home.html')

def products(request):
    products = Product.objects.all()
    template = loader.get_template('home/products.html')
    context ={
        'products':products,
    }
    return HttpResponse(template.render(context,request))

