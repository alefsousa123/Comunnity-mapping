from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from contact.models import Familia
from contact.forms import FamiliaForm
from datetime import date

@login_required(login_url="contact:login")
def familia_create(request):
    if request.method == "POST":
        form = FamiliaForm(request.POST, user=request.user)
        if form.is_valid():
            familia = form.save(commit=False)
            familia.owner = request.user
            familia.save()
            return redirect("contact:family")
    else:
        form = FamiliaForm(user=request.user)
    return render(request, "contact/partials/_familia-form.html", {"form": form})

@login_required(login_url="contact:login")
def familia_detail(request, familia_id):
    familia = get_object_or_404(Familia, pk=familia_id, owner=request.user)
    return render(request, "contact/family.html", {"familia": familia})

@login_required(login_url="contact:login")
def familia_update(request, familia_id):
    familia = get_object_or_404(Familia, pk=familia_id, owner=request.user)
    form = FamiliaForm(instance=familia)

    if request.method == "POST":
        form = FamiliaForm(request.POST, instance=familia)
        if form.is_valid():
            form.save()
            return redirect("contact:familia_detail", familia_id=familia.id)

    return render(
        request,
        "contact/partials/_familia-form.html",  # voltou ao template original
        {
            "form": form,
            "site_title": "Atualizar Família - ",
            "form_title": "Atualizar Família",
        }
    )

@login_required(login_url="contact:login")
def familia_delete(request, familia_id):
    familia = get_object_or_404(Familia, pk=familia_id, owner=request.user)
    confirmation = request.POST.get('confirmation', 'no')
    if confirmation == 'yes':
        familia.delete()
        return redirect("contact:family")
    return render(
        request,
        "contact/family.html",
        {
            'familia': familia,
            'confirmation': confirmation,
        }
    )

@login_required(login_url="contact:login")
def family(request):
    """
    Render the contact page.
    Recupera todos os contatos marcados como 'show=True'
    e ordena do mais recente para o mais antigo.
    """
    familias = Familia.objects.filter(owner=request.user).order_by('data_ultima_reuniao')
    today = date.today()
    for familia in familias:
        if familia.data_ultima_reuniao:
            familia.dias_sem_visita = (today - familia.data_ultima_reuniao).days
        else:
            familia.dias_sem_visita = None
    context = {
        "page_obj": familias,
        "today": today,
    }
    return render(request, "contact/family_page.html", context)

@login_required(login_url="contact:login")
def search_familias(request):
    search_value = request.GET.get("q", "").strip()
    if not search_value:
        return redirect("contact:family")

    familias = (
        Familia.objects
        .filter(show=True, owner=request.user)
        .filter(
            Q(nome__icontains=search_value) |
            Q(endereco__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(rua__nome__icontains=search_value)  # <-- busca pelo nome da rua
        )
        .order_by("-id")
    )
    paginator = Paginator(familias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "site_title": "Busca de Famílias - "
    }

    return render(
        request,
        "contact/family_page.html",
        context=context
    )

@login_required(login_url="contact:login")
def marcar_visitado(request, familia_id):
    familia = get_object_or_404(Familia, pk=familia_id, owner=request.user)
    if request.method == "POST":
        familia.data_ultima_reuniao = timezone.now().date()
        familia.save()
    return redirect("contact:family")