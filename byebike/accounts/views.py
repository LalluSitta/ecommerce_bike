from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from .forms import FormRegistrazione

from .models import UserProfile

"""
La funzione di seguito descritta permette all' utente di registrarsi al sito.
Se il form è valido, l' utente deve riempire i campi proposti quali username,
la sua email e una password.
"""


def buyer_registration(request):
    if request.method == "POST":
        form = FormRegistrazione(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            utente = User.objects.create_user(username=username, password=password, email=email)
            UserProfile.objects.create(user=utente)
            buyer = Group.objects.get(name="Compratore")
            buyer.user_set.add(utente)
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")

    else:
        form = FormRegistrazione()
    context = {"form": form}
    return render(request, "accounts/registration.html", context)


def seller_registration(request):
    if request.method == "POST":
        form = FormRegistrazione(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            utente = User.objects.create_user(username=username, password=password, email=email)
            UserProfile.objects.create(user=utente)
            buyer = Group.objects.get(name="Venditore")
            buyer.user_set.add(utente)
            return HttpResponseRedirect('/profile/admin')

    else:
        form = FormRegistrazione()
    context = {"form": form}
    return render(request, "accounts/registration.html", context)
