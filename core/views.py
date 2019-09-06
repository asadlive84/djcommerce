from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages
from django.views.generic.base import View
from django.core import exceptions
from core.models import Item, OrderItem, Order
from core.forms import CheckoutForm


def items_list(request):
    item = Item.objects.all()
    context = {
        'item': item,
    }
    return render(request, 'home-page.html', context)


class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = 'home-page.html'


class CheckOutView(View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form,
        }

        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        print(self.request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return redirect("core:checkout")

        messages.warning(self.request, "Failed checkout!")
        return redirect("core:checkout")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'order_summary.html', context)
        except exceptions.ObjectDoesNotExist:
            messages.error(self.request, "You do not have any active order!")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


def home(request):
    items = Item.objects.all()
    context = {
        'items': items,
    }
    return render(request, 'home-page.html', context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():

        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated to your cart")
        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
    else:
        order = Order.objects.create(user=request.user, order_date=timezone.now())
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")

    return redirect("core:product", slug=slug)


@login_required
def remove_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        print(order)
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            # order_item.quantity = 0
            messages.info(request, "This product was removed from your cart")
            return redirect('core:order-summary')
        else:
            messages.info(request, "This product was not in your cart")
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, "You do not have any active order.")
        return redirect('core:product', slug=slug)

    return redirect("core:product", slug=slug)


@login_required
def remove_single_product_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        print(order)
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This product quantity was updated")
            return redirect('core:order-summary')
        else:
            messages.info(request, "This product was not in your cart")
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, "You do not have any active order.")
        return redirect('core:product', slug=slug)

    return redirect("core:product", slug=slug)


@login_required
def add_single_product_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        print(order)
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)[0]
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This product quantity was updated")
            return redirect('core:order-summary')
        else:
            messages.info(request, "This product was not in your cart")
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, "You do not have any active order.")
        return redirect('core:product', slug=slug)

    return redirect("core:product", slug=slug)
