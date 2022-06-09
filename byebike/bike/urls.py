from . import views
from django.urls import path
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('cerca/', views.cerca, name="cerca"),
    path('categorie/<str:cat>', views.CategoryFilter, name="categorie"),

    path('user/acquisti', login_required(views.AcquistiView.as_view()), name='acquisti'),
    path('profile/<username>', views.UserProfileView, name="profile"),
    path('product/<slug>', views.ItemDetailView.as_view(), name='item_view'),
    path('item/<int:pk>/delete/', login_required(views.ItemDelete.as_view()), name='item_delete'),
    path('item/<int:pk>/modify/', login_required(views.ItemModify.as_view()), name='item_modify'),
    path('user_item_page/<slug>', views.UserItemDetailView.as_view(), name='user_item_view'),
    path('add_to_cart/<slug>', login_required(views.add_to_cart), name='add_to_cart'),
    path('remove_from_cart/<slug>', login_required(views.remove_from_cart), name='remove_from_cart'),
    path('cart/', login_required(views.CartView.as_view()), name='cart'),
    path('checkout/', login_required(views.CheckoutView.as_view()), name='checkout'),
    path('user/<username>/address_page/', login_required(views.address_view), name='address_page'),
    path('user/address/<int:pk>/', login_required(views.address_detail), name='address'),
    path('user/address/<int:pk>/delete/', login_required(views.AddressDelete.as_view()), name='address_delete'),
    path('user/address/<int:pk>/modify/', login_required(views.AddressChange.as_view()), name='address_modifica'),
    path('order_display/<pk>', login_required(views.OrderDisplay.as_view()), name='order_display'),
    path('createitem/', login_required(views.ItemCreate.as_view()), name="create_item"),



]
