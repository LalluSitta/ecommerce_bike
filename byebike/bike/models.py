from email.policy import default
from django.contrib.auth.models import User
from django.db import models
from autoslug import AutoSlugField
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils import timezone



CONDIZIONE=(
    ('N', 'Nuovo'),
    ('U', 'Usato'),
)
TIPOLOGIA=(
    ('B', 'Bicicletta'),
    ('A', 'Accessori'),
)
GENERE=(
    ('D', 'Donna'),
    ('U', 'Uomo'),
    ('B', 'Bambino'),
)

CATEGORIA=(
    ('A', 'Accessori'),
    ('B', 'Bambino'),
    ('C', 'Città'),
    ('D', 'Corsa'),
    ('E', 'Elettriche'),
    ('M', 'Mountain'),
)

# Create your models here.

class Item(models.Model):
    titolo = models.CharField(max_length=30)
    descrizione = models.TextField(max_length=200) #colore, materiale, categoria, grandezza, brand, grandezza ruota
    tipologia = models.CharField(choices=TIPOLOGIA, max_length=15)
    slug = AutoSlugField(populate_from='titolo', unique=True) #chiave primaria unica
    immagine= models.ImageField()
    condizione= models.CharField(choices=CONDIZIONE, max_length=15)
    categoria = models.CharField(choices=CATEGORIA, max_length=15)
    genere = models.CharField(choices=GENERE, max_length=15)
    ordinato=models.BooleanField(default=False) # indica se l' oggetto è stato acquistato o no
    prezzo = models.FloatField(validators=[MinValueValidator(0.0)]) #mettiamo validators per controllare che sia davvero un float 
    venditore = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item")
    data = models.DateTimeField(auto_now_add=True) # data in cui viene effettuato l' ordine

    def __str__(self):
        return self.titolo

    def get_absolute_url(self):
        return reverse("item_view", kwargs={"slug": self.slug})

    def visualizza_articolo(self):
        return reverse("user_item_view", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Articoli"



class OrderItem(models.Model):
    product = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    is_ordered = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    ordered_date = models.DateTimeField(default=timezone.now)
    recommended = models.BooleanField(default=False)

    def __str__(self):
        return self.product.titolo

    def get_tot_price(self):
        return self.product.prezzo * self.quantity

    def get_final_price(self):
        return self.get_tot_price()

    class Meta:
        verbose_name_plural = 'Articoli Ordinati'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField()
    shipping_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def __str__(self):
        return self.user.username

    def get_username(self):
        return self.user.username

    def get_address(self):
        return self.shipping_address.città + " " + self.shipping_address.via

    class Meta:
        verbose_name_plural = 'Ordini'


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stato = models.CharField(max_length=30)
    città = models.CharField(max_length=30)
    cap = models.CharField(max_length=5)
    via = models.CharField(max_length=50)
    interno = models.CharField(max_length=30, blank=True)
    note = models.TextField(blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Indirizzi'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Pagamenti'


class RecommendedItem(models.Model):
    num_item = models.PositiveIntegerField(default=0)
    condizioneN = models.PositiveIntegerField(default=0)
    condizioneU = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prezzo = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    sum_prezzo = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Articoli Consigliati'



