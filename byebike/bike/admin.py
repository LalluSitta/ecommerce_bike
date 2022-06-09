from django.contrib import admin
from bike.models import Item
from .models import Order, ShippingAddress, Payment

# Register your models here.

class ItemModelAdmin(admin.ModelAdmin):
    model = Item
    list_display = ["titolo", "prezzo", "condizione", "genere"]

    

admin.site.register(Item, ItemModelAdmin) #mostra graficamente il DB
admin.site.register(Order)
admin.site.register(ShippingAddress)
admin.site.register(Payment)