from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
import random
from datetime import datetime, timedelta

# Data for daily specials and menu items
menu_items = [
    {'name': 'Pizza', 'price': 12.99, },
    {'name': 'Burger', 'price': 9.99,},
    {'name': 'Pasta', 'price': 10.99, },
    {'name': 'Salad', 'price': 7.99},
]

daily_specials = [
    {'name': 'Sashimi Platter', 'price': 79.39, },
    {'name': 'Galbi-jjim', 'price': 99.23,},
    {'name': 'Karaage', 'price': 10.29, },
    {'name': 'Daily Pot', 'price': 45.99},
]

# View for the main page
def main(request):
    return render(request, 'restaurant/main.html')

# View for the order page
def order(request):
    daily_special = random.choice(daily_specials)
    context = {
        'menu_items': menu_items,
        'daily_special': daily_special
    }
    return render(request, 'restaurant/order.html', context)

# View for the confirmation page
def confirmation(request):
    if request.method == 'POST':
        ordered_items = []
        total_price = 0
        
        for item in menu_items:
            if request.POST.get(item['name']):
                ordered_items.append(item['name'])
                total_price += item['price']
        
        customer_name = request.POST.get('name')
        customer_phone = request.POST.get('phone')
        customer_email = request.POST.get('email')

        # Generate a random ready time between 30 and 60 minutes from now
        #ready_time = timezone.now() + timedelta(minutes=random.randint(30, 60))
        ready_time = datetime.now()
        random_minutes = random.randint(30, 60)
        ready_time = ready_time + timedelta(minutes=random_minutes)
        formatted_ready_time = ready_time.strftime("%a %b %d %H:%M:%S %Y")

        context = {
            'ordered_items': ordered_items,
            'total_price': total_price,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'ready_time': formatted_ready_time
        }
        
        return render(request, 'restaurant/confirmation.html', context)
