from django.utils import timezone
from turtle import home
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from .models import Item, Order, OrderItem, Payment, ShippingAddress, RecommendedItem
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm
from accounts.views import UserProfile


# Create your views here.


''' 
Funzione utilizzata per visualizzare e eseguire azioni sulla homepage
'''


def homepage(request):
    object_list = Item.objects.filter(ordinato=False).order_by("-data")
    if (request.user.is_authenticated):
        recommended_items = RecommendedItem.objects.filter(user=request.user)
        for racc in recommended_items:
            racc.save()
        if recommended_items.exists():
            order_qs = Order.objects.filter(user=request.user, is_ordered=True)
            order_item_qs = OrderItem.objects.filter(
                user=request.user, is_ordered=True, recommended=False)

            for item in order_item_qs:
                for racc in recommended_items:
                    if (item.product.condizione == 'N'):
                        racc.condizioneN += 1
                    if (item.product.condizione == 'U'):
                        racc.condizioneU += 1
                    racc.num_item += 1
                    racc.sum_prezzo += item.product.prezzo
                    racc.prezzo = racc.sum_prezzo / racc.num_item
                    item.recommended = True
                    item.save()

            for racc in recommended_items:
                print(racc.prezzo)
                print(racc.num_item)
                racc.save()
                print(racc.num_item)

        else:
            recommended_items = RecommendedItem.objects.create(
                user=request.user)
            order_qs = Order.objects.filter(user=request.user, is_ordered=True)
            order_item_qs = OrderItem.objects.filter(
                user=request.user, is_ordered=True, recommended=False)

            for item in order_item_qs:
                if (item.product.condizione == 'N'):
                    recommended_items.condizioneN += 1
                if (item.product.condizione == 'U'):
                    racc.condizioneU += 1
                recommended_items.num_item += 1
                recommended_items.sum_prezzo += item.product.prezzo
                recommended_items.prezzo = recommended_items.sum_prezzo / recommended_items.num_item
                item.recommended = True
                item.save()
            recommended_items.save()
            print('Da creare')

    recommendation_list = []
    newconvenient_list = []
    usedconvenient_list = []
    if (request.user.is_authenticated):
        recommended_items = RecommendedItem.objects.filter(user=request.user)
        for it in object_list:
            for recommended in recommended_items:
                if (it.venditore != request.user):
                    if ((it.prezzo >= recommended.prezzo and it.prezzo <= recommended.prezzo + 100) or (
                            it.prezzo <= recommended.prezzo and it.prezzo >= recommended.prezzo - 100)):
                        if ((recommended.condizioneN == recommended.condizioneU) and (
                                recommended.condizioneN >= 1 or recommended.condizioneU >= 1)):
                            if (it not in recommendation_list):
                                recommendation_list.append(it)
                        if ((recommended.condizioneN > recommended.condizioneU) and (
                                recommended.condizioneN >= 1 or recommended.condizioneU >= 1)):
                            if (it.condizione == 'N'):
                                if (it not in recommendation_list):
                                    recommendation_list.append(it)
                        else:
                            if ((recommended.condizioneN < recommended.condizioneU) and (recommended.condizioneN >= 1 or recommended.condizioneU >= 1)):
                                if (it.condizione == 'U'):
                                    if (it not in recommendation_list):
                                        recommendation_list.append(it)

    for it in object_list:
        if (it.prezzo <= 700 and it.condizione == 'N'):
            newconvenient_list.append(it)
        if (it.prezzo <= 500 and it.condizione == 'U'):
            usedconvenient_list.append(it)

    recommendation_list = sorted(recommendation_list[:4], key=lambda item: (
        item.prezzo))  # ordino gli item consigliati da quello con prezzo minore
    newconvenient_list = sorted(
        newconvenient_list[:4], key=lambda item: (item.prezzo))
    usedconvenient_list = sorted(
        usedconvenient_list[:4], key=lambda item: (item.prezzo))

    context = {
        'object_list': object_list,
        "recommendation_list": recommendation_list,
        "newconvenient_list": newconvenient_list,
        "usedconvenient_list": usedconvenient_list
    }
    print(recommendation_list)
    return render(request, 'bike/homepage.html', context)


'''
Barra di ricerca
@param: ritorna la pagina contenente i risultati della ricerca
'''


def cerca(request):
    if "kw" in request.GET:
        querystring = request.GET.get("kw")
        if len(querystring) == 0:
            return redirect("/cerca/")
        items = Item.objects.filter(
            titolo__icontains=querystring, ordinato=False).order_by("-pk")
        context = {"items": items}
        return render(request, 'bike/search.html', context)
    else:
        return render(request, 'bike/search.html')


def CategoryFilter(request, cat):
    object_list = Item.objects.filter(
        categoria=cat, ordinato=False).order_by("-pk")
    paginator = Paginator(object_list, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'object_list': object_list,
        'object_list': page_obj,
        'page_obj': page_obj
    }
    return render(request, 'bike/categories.html', context)


'''
Visualizza la pagina del profilo utente
@param username : Nome dell' utente
return: la pagina del profilo utente
'''


def UserProfileView(request, username):
    if request.user.username != username:
        return OtherUserProfileView(request, username)
    user = get_object_or_404(User, username=username)
    user_items = Item.objects.filter(venditore=user.pk, ordinato=False).order_by("-pk")
    utenti = User.objects.order_by('-id')
    vendite = Item.objects.filter(venditore=user.pk, ordinato=True).order_by("-data")
    acquisti = Payment.objects.filter(user=user).order_by("-pk")
    paginator = Paginator(user_items, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_items": page_obj, "acquisti": acquisti, "vendite":vendite, "utenti": utenti, "page_obj": page_obj}
    return render(request, 'bike/user_profile.html', context)


def OtherUserProfileView(request, username):
    user = get_object_or_404(User, username=username)
    user_items = Item.objects.filter(venditore=user.pk, ordinato=False).order_by("-pk")
    paginator = Paginator(user_items, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_items": page_obj, "page_obj": page_obj}
    return render(request, 'bike/other_user_profile.html', context)


'''
Utilizzata per la creazione e inserimento di un articolo
Estende la view CreateView di Django
'''


class ItemCreate(CreateView):
    model = Item
    fields = ["titolo", "descrizione", "tipologia", "immagine", "categoria", "condizione",
              "genere", "prezzo"]
    template_name = "bike/item_create.html"

    def form_valid(self, form):
        form.instance.venditore_id = self.request.user.pk
        print(form.instance.titolo)
        return super(ItemCreate, self).form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy("homepage")
        return success_url


# Views per la visualizzazione di un articolo
class ItemDetailView(DetailView):
    model = Item
    template_name: "bike/item_detail.html"


'''
Classe utilizzata per l' eliminazione di un articolo
'''


class ItemDelete(DeleteView):
    model = Item
    template_name = 'bike/item_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)

        if user.id is not item.venditore.id:
            messages.info(request, "Non puoi accedere a questa pagina!")
            return homepage(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)
        user = get_object_or_404(User, username=item.venditore)
        return reverse_lazy('profile', kwargs={'username': user})


'''
Classe utilizzata per modificare i campi di un articolo
'''


class ItemModify(UpdateView):
    model = Item
    fields = ["titolo", "descrizione", "tipologia", "immagine", "categoria", "condizione",
              "genere", "prezzo"]
    template_name = 'bike/item_modify.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)

        if user.id is not item.venditore.id:
            messages.info(request, "Non puoi accedere a questa pagina!")
            return homepage(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)
        user = get_object_or_404(User, username=item.venditore)
        return reverse_lazy('profile', kwargs={'username': user})


class UserItemDetailView(DetailView):
    model = Item
    template_name = "bike/user_item_detail.html"


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        product=item, user=request.user, is_ordered=False)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=item.slug).exists():
            order_item.quantità = 1
            order_item.save()
            messages.info(
                request, "Hai già aggiunto questo articolo al carrello!")
        else:
            order.items.add(order_item)
            messages.info(
                request, "L' articolo è stato aggiunto con successo al carrello")
            return redirect('homepage')
    else:
        date_ordered = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=date_ordered)
        order.items.add(order_item)
        messages.info(
            request, "L' articolo è stato aggiunto con successo al carrello")

    return redirect('homepage')


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                product=item, user=request.user, is_ordered=False)[0]
            order.items.remove(order_item)
            messages.info(
                request, "L' articolo è stato rimosso correttamente dal carrello")
            return redirect(reverse_lazy('cart'))
        else:
            messages.info(request, "L' articolo non è nel carrello")
            return redirect(reverse_lazy('item_view', kwargs={'slug': slug}))
    else:
        messages.info(request, "Non hai un ordine attivo")
        return redirect(reverse_lazy('item_view', kwargs={'slug': slug}))


class CartView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {'object': order}
            return render(self.request, 'bike/order/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Il carrello è vuoto")
            return redirect('homepage')


'''
Funzione utilizzata per verificare che i campi dei vari form siano non vuoti
'''


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        context = {'form': form}

        shipping_address_qs = ShippingAddress.objects.filter(
            user=self.request.user, default=True)
        if shipping_address_qs.exists():
            context.update(
                {'default_shipping_address': shipping_address_qs[0]})
        return render(self.request, 'bike/order/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                form.use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if form.use_default_shipping:
                    print('Uso indirizzo di default')
                    address_qs = ShippingAddress.objects.filter(
                        user=self.request.user, default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order_items = order.items.all()
                        order_items.update(is_ordered=True)
                        order.shipping_address = shipping_address
                        for item in order_items:
                            item.product.ordinato = True
                            item.product.acquirente = order.get_username()
                            item.product.indirizzo = order.get_address()
                            item.product.data = timezone.now()
                            item.product.save()
                            item.save()

                        order.shipping_address = shipping_address
                        order.is_ordered = True
                        order.ordered_date = timezone.now()
                        order.save()
                        payment = Payment()
                        payment.user = self.request.user
                        payment.amount = order.get_total()
                        payment.order = order
                        payment.save()
                    else:
                        messages.info(
                            self.request, "Nessun indirizzo di default")
                        return redirect('checkout')
                else:
                    form.stato = form.cleaned_data.get('stato')
                    form.città = form.cleaned_data.get('città')
                    form.via = form.cleaned_data.get('via')
                    form.cap = form.cleaned_data.get('cap')
                    form.interno = form.cleaned_data.get('interno')
                    form.note = form.cleaned_data.get('note')

                    form.opzioni_pagamento = form.cleaned_data.get(
                        'opzioni_pagamento')
                    if is_valid_form([form.stato, form.città, form.via, form.cap]):
                        shipping_address = ShippingAddress(
                            user=self.request.user,
                            stato=form.stato,
                            città=form.città,
                            via=form.via,
                            cap=form.cap,
                            interno=form.interno,
                            note=form.note
                        )
                        shipping_address.save()
                        order_items = order.items.all()
                        order_items.update(is_ordered=True)
                        order.shipping_address = shipping_address
                        for item in order_items:
                            item.product.ordinato = True
                            item.product.acquirente = order.get_username()
                            item.product.data = timezone.now()
                            item.product.indirizzo = order.get_address()
                            item.product.save()
                            item.save()

                        order.shipping_address = shipping_address
                        order.is_ordered = True
                        order.ordered_date = timezone.now()
                        order.save()
                        payment = Payment()
                        payment.user = self.request.user
                        payment.amount = order.get_total()
                        payment.order = order
                        payment.save()

                        form.save_info = form.cleaned_data.get('save_info')
                        if form.save_info:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, "Compila tutti i campi per continuare")
                        return redirect('checkout')

            messages.info(
                self.request, "L' ordine è stato ricevuto con successo")
            return redirect('homepage')

            messages.warning(
                self.request, "Il pagamento non è andato a buon fine")
            return redirect('homepage')
            return render(self.request, 'bike/order/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Non hai nessun ordine in corso")
            return redirect('cart')


def address_view(request, username):
    if request.user.username != username:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return homepage(request)
    user = get_object_or_404(User, username=username)
    user_address = ShippingAddress.objects.filter(user=user.pk)
    context = {"user": user, "user_address": user_address}
    return render(request, 'accounts/address_page.html', context)


def address_detail(request, pk):
    address = ShippingAddress.objects.get(pk=pk)
    if request.user.id != address.user.id:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return homepage(request)
    return render(request, 'accounts/address.html', context={"object": address})


'''
Utilizzato per l' eliminazione di un indirizzo
'''


class AddressDelete(DeleteView):
    model = ShippingAddress
    template_name = 'accounts/address_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)

        if user.id is not address.user.id:
            messages.info(request, "Non puoi accedere a questa pagina !")
            return homepage(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)
        user = get_object_or_404(User, username=address.user)
        return reverse_lazy('address_page', kwargs={"username": user})


'''
Modifica l' indirizzo e permette di scegliere l' indirizzo di default
'''


class AddressChange(UpdateView):
    model = ShippingAddress
    fields = ('città', 'via', 'stato', 'cap', 'default')
    template_name = 'accounts/address_change.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)

        if user.id is not address.user.id:
            messages.info(request, "Non puoi accedere a questa pagina !")
            return homepage(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)
        user = get_object_or_404(User, username=address.user)
        return reverse_lazy('address_page', kwargs={"username": user})


'''
Utilizzato per visualizzare il riepilogo degli ordini
'''


class OrderDisplay(View):
    model = Order
    template_name = 'bike/order/order_display.html'

    def get(self, *argss, **kwargs):
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id, is_ordered=True)
        context = {
            'User': self.request.user,
            'lista_acquisti': order.items.all()
        }
        return render(self.request, 'bike/order/order_display.html', context)

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        order_id = self.kwargs["pk"]
        order = get_object_or_404(Order, id=order_id)

        if user.id is not order.user.id:
            messages.info(request, "Non puoi accedere a questa pagina !")
            return homepage(request)

        return super().dispatch(request, *args, **kwargs)


class AcquistiView(View):
    model = User
    template_name = 'bike/acquisti.html'

    def get(self, *args, **kwargs):
        user_id = self.request.user.id
        user = User.objects.get(id=user_id)
        acquisti = Payment.objects.filter(user=user).order_by("-pk")
        paginator = Paginator(acquisti, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'User': user,
            'lista_acquisti': page_obj,
            'page_obj': page_obj
        }
        return render(self.request, 'bike/acquisti.html', context)



