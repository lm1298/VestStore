from django.shortcuts import render, redirect
from .models import Vest, ShippingDetail, Order
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
import json
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import paypalrestsdk
from django.conf import settings
from django.db import transaction
from django.urls import reverse

paypalrestsdk.configure({
  "mode": settings.PAYPAL_MODE,
  "client_id": settings.PAYPAL_CLIENT_ID,
  "client_secret": settings.PAYPAL_CLIENT_SECRET })
# Create your views here.
def home(request):
    cart_empty = True if not request.session.get('cart') else False
    return render(request, 'home.html', {'cart_empty': cart_empty})

def about(request):
    return render(request, 'about.html')

def product(request):
    vests = Vest.objects.all()
    cart_empty = True if not request.session.get('cart') else False
    return render(request, 'product.html', {'vests': vests, 'cart_empty': cart_empty})

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
    cart_empty = True if not request.session.get('cart') else False

    for size, quantity in cart.items():
        vest = Vest.objects.filter(size=size).first()
        if vest:
            items.append({'size': size, 'quantity': quantity, 'price': float(vest.price)})

    context = {'items': items}
    return render(request, 'cart.html', {'items': items, 'cart_empty': cart_empty})

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

@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = {size: quantity for size, quantity in data.items() if quantity > 0}
        request.session['cart'] = cart
        return JsonResponse({'message': 'Cart updated successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def checkout(request):
    cart_empty = True if not request.session.get('cart') else False
    return render(request, 'payment.html', {'cart_empty': cart_empty})
 
@transaction.atomic
def create_order(request):
    if request.method == 'POST':
        # Retrieve shipping details from the form submission
        full_name = request.POST.get('full_name')
        email = request.POST.get('customer_email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')

        # Create the order instance
        shippingdetail = ShippingDetail.objects.create(
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            zip_code=zip_code
        )

        # Retrieve items from the cart and create order items
        cart = request.session.get('cart', {})
        for size, quantity in cart.items():
            vest = Vest.objects.get(size=size)
            Order.objects.create(
                shippingdetail=shippingdetail,
                size=size,
                quantity=quantity,
                price=vest.price
            )

            # Update the quantity of vests in the database
            vest.quantity -= quantity
            vest.save()

            # Check if the quantity dropped below 5 and send notification
            if vest.quantity < 5:
                vest.send_low_quantity_notification()

        # Clear the cart after creating the order
        request.session['cart'] = {}

        

        # Redirect to a page indicating successful order placement
        # return redirect('confirmation')
        return JsonResponse({'message': 'Order placed successfully'}, status=200)
    else:
        return HttpResponseNotAllowed(['POST'])