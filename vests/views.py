from django.shortcuts import render, redirect
from .models import Vest
from django.http import HttpResponse, JsonResponse 
import json
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import paypalrestsdk
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

paypalrestsdk.configure({
  "mode": settings.PAYPAL_MODE,
  "client_id": settings.PAYPAL_CLIENT_ID,
  "client_secret": settings.PAYPAL_CLIENT_SECRET })
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
    return render(request, 'payment.html')
 
def shipping_details(request):
    if request.method == 'POST':
        # Save shipping details in the session
        request.session['shipping_details'] = request.POST
        # Redirect to PayPal payment page
        return redirect('paypal_payment')
    else:
        # Display shipping details form
        return render(request, 'payment.html')

def paypal_payment(request):
    if request.method == 'POST':
        # Get the cart and shipping details from the session
        cart = request.session.get('cart', {})
        shipping_details = request.session.get('shipping_details', {})
        items = []
        total = 0

        # Build the list of items for the payment
        for size, quantity in cart.items():
            vest = Vest.objects.filter(size=size).first()
            if vest:
                items.append({
                    "name": f"Vest {size}",
                    "sku": f"VEST-{size}",
                    "price": str(vest.price),
                    "currency": "USD",
                    "quantity": quantity
                })
                total += vest.price * quantity

        # Create the payment object
        # ...

                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"},
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri(reverse('paypal_execute')),
                        "cancel_url": request.build_absolute_uri(reverse('paypal_cancel'))},
                    "transactions": [{
                        "item_list": {
                            "items": items},
                        "amount": {
                            "total": str(total),
                            "currency": "USD"},
                        "description": "Vest Infinity Order"}]})

        # Create the payment
        if payment.create():
            for link in payment.links:
                if link.method == "REDIRECT":
                    # Redirect the user to the PayPal payment page
                    return redirect(link.href)
        else:
            return JsonResponse({'error': 'An error occurred while creating the PayPal payment'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def paypal_execute(request):
    if request.method == 'GET':
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')

        # Execute the payment
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            # The payment has been completed successfully
            return redirect('confirmation')
        else:
            return JsonResponse({'error': 'An error occurred while executing the PayPal payment'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def paypal_cancel(request):
    # The payment has been cancelled by the user
    return redirect('cart')
