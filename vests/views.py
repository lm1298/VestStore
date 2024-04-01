from django.shortcuts import render
from .models import Vest
from django.http import HttpResponse, JsonResponse 
import json
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

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
    if size:
        # Query the database to get available quantities for the selected size
        quantities = list(Vest.objects.filter(size=size).values_list("quantity", flat=True))
        return JsonResponse(quantities, safe=False)
    else:
        return JsonResponse({"error": "Size parameter is required"}, status=400)
    
def cart(request):
    cart = request.session.get('cart', {})
    items = []

    for size, quantity in cart.items():
        vest = Vest.objects.filter(size=size).first()
        if vest:
            items.append({'size': size, 'quantity': quantity, 'price': float(vest.price)})

    context = {'items': items}
    return render(request, 'cart.html', {'items': items})

def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        selected_size = data.get('size')
        selected_quantity = int(data.get('quantity'))
        cart = request.session.get('cart', {})

        current_cart_quantity = cart.get(selected_size, 0)
        
        # Retrieve the available quantity for the selected size from the database
        vest = Vest.objects.filter(size=selected_size).first()
        available_quantity = vest.quantity if vest else 0
        
        # Calculate the maximum quantity that can be added to the cart
        max_quantity = available_quantity - current_cart_quantity
        
        # Check if the selected quantity exceeds the maximum allowed quantity
        if selected_quantity > max_quantity:
            message = f'Only {max_quantity} more can be added to the cart.'
            return JsonResponse({'error': message, 'popup': True}, status=400)

        if selected_size in cart:
            cart[selected_size] += selected_quantity
        else:
            cart[selected_size] = selected_quantity

        request.session['cart'] = cart
        print(cart.items())
        return JsonResponse({'message': 'Item added to cart'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def confirmation(request):
    return render(request, 'confirmation.html')

