from math import sin
from django.shortcuts import render, get_object_or_404, redirect
from contact.models import Contact
from django.db.models import Q
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    """
    Render the contact page.
    Recupera todos os contatos marcados como 'show=True'
    e ordena do mais recente para o mais antigo.
    """
    contacts = (
        Contact.objects
        .filter(show=True, owner=request.user)
        .order_by("-id")
    )
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the contacts for the requested page

    context = {
        "page_obj": page_obj,
        "site_title": "Contatos - "
    }

    return render(
        request,
        "contact/index.html",
        context=context
    )


def search(request):
    search_value = request.GET.get("q", "").strip()
    if not search_value:
        return redirect("contact:index")
    """
    Render the contact page.
    Recupera todos os contatos marcados como 'show=True'
    e ordena do mais recente para o mais antigo.
    """
    contacts = (
        Contact.objects
        .filter(show=True, owner=request.user)
        .filter(
            Q(first_name__icontains=search_value) |
            Q(last_name__icontains=search_value) |
            Q(phone__icontains=search_value) |
            Q(email__icontains=search_value)
        )
        .order_by("-id")
    )
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "site_title": "search - "
    }

    return render(
        request,
        "contact/index.html",
        context=context
    )


def contact(request, contact_id):
    single_contact = get_object_or_404(
        Contact,
        pk=contact_id,
        show=True,
        owner=request.user
    )
    site_title = f'{single_contact.first_name} - '
    context = {
        "contact": single_contact,
        "site_title": site_title
    }

    return render(
        request,
        "contact/contact.html",
        context=context
    )