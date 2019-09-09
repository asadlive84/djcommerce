from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages
from django.views.generic.base import View
from django.core import exceptions
from core.models import Item, OrderItem, Order, BillingAddress, Payment
from core.forms import CheckoutForm

from django.conf import settings

import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY



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

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_options = form.cleaned_data.get('payment_options')

                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                    # save_info=save_info,
                    # same_shipping_address=same_shipping_address,
                    # payment_options=payment_options,

                )
                billing_address.save()

                order.billing_address = billing_address
                order.save()

                return redirect("core:checkout")

            messages.warning(self.request, "Failed checkout!")
            return redirect("core:checkout")

        except exceptions.ObjectDoesNotExist:
            messages.error(self.request, "You do not have any active order!")
            return redirect("core:order-summary")


class PaymentView(View):

    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order,
        }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency='usd',
                source=token,
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order.ordered = True
            order.payment = payment
            
            order.save()

            messages.success(self.request, "Your order was successful")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})

            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")


        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, f"Rate Limit Error")
            return redirect("/")


        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, f"Invalid Request Error")
            return redirect("/")


        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, f"Authentication Error")
            return redirect("/")


        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, f"APIConnection Error")
            return redirect("/")


        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, f"Stripe Error")
            return redirect("/")


        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, f"Opps!! error!")


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
