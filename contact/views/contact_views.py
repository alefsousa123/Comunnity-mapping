from django.shortcuts import render, get_object_or_404, redirect
from contact.models import Contact
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
@login_required(login_url="contact:login")
def index(request):
    """
    Render the contact page.
    Recupera todos os contatos marcados como 'show=True'
    e ordena do mais recente para o mais antigo.
    """
    age_group = request.GET.get("age_group", "").strip()
    contatos = Contact.objects.filter(show=True, owner=request.user).order_by("-id")

    # Filtro por faixa etária em Python
    if age_group:
        contatos = [c for c in contatos if c.age_group.lower() == age_group.lower()]

    paginator = Paginator(contatos, 10)  # Show 10 contacts per page
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
@login_required(login_url="contact:login")
def search(request):
    search_value = request.GET.get("q", "").strip()
    age_group = request.GET.get("age_group", "").strip()
    if not search_value and not age_group:
        return redirect("contact:index")

    contatos = Contact.objects.filter(show=True, owner=request.user)
    if search_value:
        contatos = contatos.filter(
            Q(first_name__icontains=search_value) |
            Q(last_name__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(familia__nome__icontains=search_value) |
            Q(rua__nome__icontains=search_value) |
            Q(rua__bairro__icontains=search_value)  # <-- Adicionado para buscar pelo bairro
        )
    if age_group:
        contatos = contatos.filter(age_group__iexact=age_group)

    contatos = contatos.order_by("-id")
    paginator = Paginator(contatos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "site_title": "Busca de Contatos - "
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