from django.shortcuts import render
from core.models import Item

def items_list(request):
    item = Item.objects.all()
    context = {
        'item': item,
    }
    return render(request, 'items_list.html', context)
