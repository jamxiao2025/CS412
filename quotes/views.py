from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import random
quotes = ["I hope not to define myself by suffering","You just do what you can and you have as much fun as possible","Fuck Coachella","how you looking up to me and talkin down?","We’ll never be those kids again","Guys, I'm being told it's curfew, so that's the end of the show. Thank you so much.",'be good to yourself. be good to people. be good.', 'i mean, honest to God, i can probably count on my hands the people who ive asked for advice this year.', 'are you excited about your life?']
images = ['frank1.jpeg','frank2.jpeg','frank3.jpeg','frank4.jpeg','frank5.jpeg','frank6.jpeg','frank7.jpeg','frank8.jpeg']
# Create your views here.
def quote(request):
    """
    Function to handle the URL request for /quotes (home page).
    Delegate rendering to the template quotes/quote.html 
    """
    template_name = 'quotes/quote.html'
    context = {
        "quote": random.choice(quotes),
        "image_path": random.choice(images)
    }

    return render(request, template_name, context)

def show_all(request):
    """
    Function to handle the URL request for /show_all page.
    Delegate rendering to the template quotes/show_all.html
    """
    template_name = 'quotes/show_all.html'
    context = {
        "quotes": quotes,
        "images": images
    }
    return render(request, template_name, context)

def about(request):
    """
    Function to handle the URL request for /about page.
    Delegate rendering to the template quotes/about.html
    """
    template_name = 'quotes/about.html'
    context = {
        "image": 'frankabout.jpeg'
    }
    return render(request, template_name, context)