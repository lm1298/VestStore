from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def product(request):
    return render(request, 'product.html')
def get_quantities(request):
        # Query the database to get available quantities for the selected size