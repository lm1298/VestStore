from django.shortcuts import render
from .models import Vest
from django.http import JsonResponse 

# Create your views here.
def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def product(request):
    vests = Vest.objects.all()
    return render(request, 'product.html', {'vests': vests})
def get_quantities(request):
    size = request.GET.get("size")
    print(size)
    if size:
        # Query the database to get available quantities for the selected size
        quantities = list(Vest.objects.filter(size=size).values_list("quantity", flat=True))
        print(quantities)
        return JsonResponse(quantities, safe=False)
    else:
        return JsonResponse({"error": "Size parameter is required"}, status=400)