from math import log
from django.shortcuts import render, redirect, get_object_or_404
from contact.forms import ContactForm
from django.urls import reverse
from contact.models import Contact
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

@login_required(login_url="contact:login")
def create(request):
    form_action = reverse("contact:create")
    site_title = "Criar Contato"
    
    # Verificar se viemos do formulário de família
    redirect_to_familia = request.GET.get('redirect_to_familia') == 'true'
    
    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES, user=request.user)
        context = {
            'form': form,
            'form_action': form_action,
            'site_title': site_title,
        }
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            
            # Se viemos do formulário de família, redirecionar de volta
            if redirect_to_familia:
                return redirect(f"{reverse('contact:familia_create')}?new_contact_id={contact.id}")
            
            return redirect("contact:index")
        return render(
            request,
            "contact/create.html",
            context=context
        )

    context = {
        'form': ContactForm(user=request.user),
        'form_action': form_action,
        'site_title': site_title,
        'redirect_to_familia': redirect_to_familia,
    }
    return render(
        request,
        "contact/create.html",
        context=context
    )

@login_required(login_url="contact:login")
def update(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, show=True, owner=request.user)
    form_action = reverse("contact:update", kwargs={'contact_id': contact_id})
    site_title = "Editar Contato"
    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES, instance=contact, user=request.user)
        context = {
            'form': form,
            'form_action': form_action,
            'site_title': site_title,
        }
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            return redirect("contact:contact", contact_id=contact.id)
        return render(
            request,
            "contact/create.html",
            context=context
        )

    context = {
        'form': ContactForm(instance=contact, user=request.user),
        'form_action': form_action,
        'site_title': site_title,
    }
    return render(
        request,
        "contact/create.html",
        context=context
    )

@login_required(login_url="contact:login")
def delete(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, show=True, owner=request.user)
    confirmation = request.POST.get('confirmation', 'no')
    if confirmation == 'yes':
        contact.delete()
        return redirect("contact:index")
    return render(
        request,
        "contact/contact.html",
        {
            'contact': contact,
            'confirmation': confirmation,
        }
    )

@login_required(login_url="contact:login")
def search(request):
    search_value = request.GET.get("q", "").strip()
    if not search_value:
        return redirect("contact:index")

    contatos = (
        Contact.objects
        .filter(show=True, owner=request.user)
        .filter(
            Q(first_name__icontains=search_value) |
            Q(last_name__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(familia__nome__icontains=search_value) |
            Q(rua__nome__icontains=search_value)  # <-- busca pelo nome da rua
        )
        .order_by("-id")
    )
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