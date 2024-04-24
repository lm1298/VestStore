from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
# Create your models here.
class Vest(models.Model):
    size = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)

    def send_low_quantity_notification(self):
        if self.quantity < 5:
            subject = f"Low Quantity Alert: Size {self.size}"
            message = render_to_string('email.html', {'vest': self})
            admin_email = User.objects.get(is_superuser=True).email
            send_mail(subject, message, 'settings.EMAIL_HOST_USER', [admin_email], html_message=message)

class ShippingDetail(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    shippingdetail = models.ForeignKey(ShippingDetail, related_name='items', on_delete=models.CASCADE)
    # vest = models.ForeignKey('Vest', on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price