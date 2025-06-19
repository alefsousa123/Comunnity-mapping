from django.shortcuts import render


# Create your views here.
def index(request):
    """
    Render the contact page.
    """
    return render(request, "contact/index.html")
