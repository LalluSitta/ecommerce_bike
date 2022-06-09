from django.urls import path, include
from . import views


urlpatterns = [
    path('registrazione_utente/', views.buyer_registration, name="buyer_registration"),
    path('registrazione_venditore/', views.seller_registration, name="seller_registration")
]
