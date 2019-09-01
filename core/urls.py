from django.urls import path
from core import views
from django.views.generic.base import TemplateView
app_name = 'core'


class CheckOut(TemplateView):
    pass

class ProductPage(TemplateView):
    pass


urlpatterns =[
    path('', views.HomeView.as_view(), name='items_list'),
    path('checkout/', CheckOut.as_view(template_name='checkout-page.html'), name="checkout"),
    #path'checkout/', CheckOut.as_view(template_name='checkout-page.html'), name="checkout"),
    path('product/<slug>/', views.ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('remove-to-cart/<slug>/', views.remove_to_cart, name="remove-to-cart"),
    path('order-summary/', views.OrderSummaryView.as_view(), name="order-summary"),
    path('remove_single_product_from_cart/<slug>/', views.remove_single_product_from_cart, name="remove_single_product_from_cart"),
    path('add_single_product_from_cart/<slug>/', views.add_single_product_from_cart, name="add_single_product_from_cart"),

]