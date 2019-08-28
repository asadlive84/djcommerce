from django.urls import path
from core import views
from django.views.generic.base import TemplateView
app_name = 'core'


class CheckOut(TemplateView):
    pass

class ProductPage(TemplateView):
    pass


urlpatterns =[
    path('', views.items_list, name='items_list'),
    path('checkout/', CheckOut.as_view(template_name='checkout-page.html'), name="checkout"),
    #path'checkout/', CheckOut.as_view(template_name='checkout-page.html'), name="checkout"),
    path('product/', ProductPage.as_view(template_name='product-page.html'), name="product"),
]