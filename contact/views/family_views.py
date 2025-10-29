from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from contact.models import Familia, Contact, Rua
from contact.forms import FamiliaForm
from datetime import date

@login_required(login_url="contact:login")
def familia_create(request):
    site_title = "Criar Família"
    
    # Verificar se estamos retornando da criação de um novo contato ou rua
    new_contact_id = request.GET.get('new_contact_id')
    new_rua_id = request.GET.get('new_rua_id')
    
    if request.method == "POST":
        form = FamiliaForm(request.POST, user=request.user)
        if form.is_valid():
            familia = form.save(commit=False)
            familia.owner = request.user
            familia.save()
            form.save()  # Salva os membros
            return redirect("contact:family")
        
        # Passar contatos e ruas para o template em caso de erro
        contatos = Contact.objects.filter(owner=request.user)
        ruas = Rua.objects.filter(owner=request.user)
        return render(
            request,
            "contact/partials/_familia-form.html",
            {
                "form": form, 
                "site_title": site_title, 
                "form_title": site_title,
                "contatos": contatos,
                "ruas": ruas
            }
        )
    else:
        form = FamiliaForm(user=request.user)
        
        # Se um novo contato foi criado, pré-selecionar ele
        if new_contact_id:
            try:
                new_contact = Contact.objects.get(id=new_contact_id, owner=request.user)
                form.fields['membros'].initial = [new_contact]
            except Contact.DoesNotExist:
                pass
        
        # Se uma nova rua foi criada, pré-selecionar ela
        if new_rua_id:
            try:
                new_rua = Rua.objects.get(id=new_rua_id, owner=request.user)
                form.fields['rua'].initial = new_rua
            except Rua.DoesNotExist:
                pass
    
    contatos = Contact.objects.filter(owner=request.user)
    ruas = Rua.objects.filter(owner=request.user)
    return render(
        request,
        "contact/partials/_familia-form.html",
        {
            "form": form, 
            "site_title": site_title, 
            "form_title": site_title,
            "contatos": contatos,
            "ruas": ruas,
            "new_contact_id": new_contact_id,  # Para destacar o novo contato
            "new_rua_id": new_rua_id  # Para destacar a nova rua
        }
    )

@login_required(login_url="contact:login")
def familia_detail(request, familia_id):
    familia = get_object_or_404(Familia, pk=familia_id, owner=request.user)
    return render(request, "contact/family.html", {"familia": familia})

@login_required(login_url="contact:login")
def familia_update(request, familia_id):
    familia = get_object_or_404(Familia, pk=familia_id, owner=request.user)
    
    if request.method == "POST":
        form = FamiliaForm(request.POST, instance=familia, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("contact:familia_detail", familia_id=familia.id)
        
        # Passar contatos e ruas para o template em caso de erro
        contatos = Contact.objects.filter(owner=request.user)
        ruas = Rua.objects.filter(owner=request.user)
        return render(
            request,
            "contact/partials/_familia-form.html",
            {
                "form": form,
                "site_title": "Atualizar Família - ",
                "form_title": "Atualizar Família",
                "contatos": contatos,
                "ruas": ruas
            }
        )
    else:
        form = FamiliaForm(instance=familia, user=request.user)

    contatos = Contact.objects.filter(owner=request.user)
    ruas = Rua.objects.filter(owner=request.user)
    return render(
        request,
        "contact/partials/_familia-form.html",
        {
            "form": form,
            "site_title": "Atualizar Família - ",
            "form_title": "Atualizar Família",
            "contatos": contatos,
            "ruas": ruas
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