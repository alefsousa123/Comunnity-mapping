from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from contact.models import Rua, GrupoFamilias
from contact.forms import RuaForm

@login_required(login_url="contact:login")
def rua_create(request):
    site_title = "Criar Rua"
    
    # Verificar se viemos do formulário de família
    redirect_to_familia = request.GET.get('redirect_to_familia') == 'true'
    
    if request.method == "POST":
        form = RuaForm(request.POST)
        if form.is_valid():
            rua = form.save(commit=False)
            rua.owner = request.user
            rua.save()
            
            # Se viemos do formulário de família, redirecionar de volta
            if redirect_to_familia:
                return redirect(f"{reverse('contact:familia_create')}?new_rua_id={rua.id}")
            
            return redirect("contact:ruas_list")
        return render(
            request,
            "contact/partials/_rua-form.html",
            {
                "form": form, 
                "site_title": site_title, 
                "form_title": site_title,
                "redirect_to_familia": redirect_to_familia
            }
        )
    else:
        form = RuaForm()
    return render(
        request,
        "contact/partials/_rua-form.html",
        {
            "form": form, 
            "site_title": site_title, 
            "form_title": site_title,
            "redirect_to_familia": redirect_to_familia
        }
    )

@login_required(login_url="contact:login")
def rua_update(request, rua_id):
    rua = get_object_or_404(Rua, pk=rua_id, owner=request.user)
    site_title = "Atualizar Rua"
    if request.method == "POST":
        form = RuaForm(request.POST, instance=rua)
        if form.is_valid():
            form.save()
            return redirect("contact:rua_detail", rua_id=rua.id)
        return render(
            request,
            "contact/partials/_rua-form.html",
            {"form": form, "site_title": site_title, "form_title": site_title}
        )
    else:
        form = RuaForm(instance=rua)
    return render(
        request,
        "contact/partials/_rua-form.html",
        {"form": form, "site_title": site_title, "form_title": site_title}
    )

@login_required(login_url="contact:login")
def rua_delete(request, rua_id):
    rua = get_object_or_404(Rua, pk=rua_id, owner=request.user)
    confirmation = request.POST.get('confirmation', 'no')
    if confirmation == 'yes':
        rua.delete()
        return redirect("contact:ruas_list")
    return render(
        request,
        "contact/rua.html",
        {
            'rua': rua,
            'confirmation': confirmation,
        }
    )

@login_required(login_url="contact:login")
def rua_detail(request, rua_id):
    rua = get_object_or_404(Rua, pk=rua_id, owner=request.user)
    familias_conectadas = rua.familias.all()
    pessoas_conectadas = rua.contatos.all()
    aulas_crianca = rua.aulas_crianca.all()
    grupos_pre_jovens = rua.grupos_pre_jovens.all()
    circulos_estudo = rua.circulos_estudo.all()
    grupos_familias = GrupoFamilias.objects.filter(ruas=rua)

    criancas = [p for p in pessoas_conectadas if p.age_group.lower() == "criança"]
    pre_jovens = [p for p in pessoas_conectadas if p.age_group == "Pré jovem"]
    jovens = [p for p in pessoas_conectadas if p.age_group.lower() == "jovem"]
    adultos = [p for p in pessoas_conectadas if p.age_group.lower() == "adulto"]

    context = {
        "rua": rua,
        "familias_conectadas": familias_conectadas,
        "pessoas_conectadas": pessoas_conectadas,
        "aulas_crianca": aulas_crianca,
        "grupos_pre_jovens": grupos_pre_jovens,
        "circulos_estudo": circulos_estudo,
        "grupos_familias": grupos_familias,
        "criancas": criancas,
        "pre_jovens": pre_jovens,
        "jovens": jovens,
        "adultos": adultos,
    }

    return render(
        request,
        "contact/rua.html",
        context=context
    )

@login_required(login_url="contact:login")
def ruas_list(request):
    ruas = Rua.objects.filter(owner=request.user)
    # Adapte para paginação se quiser
    return render(request, "contact/rua_page.html", {"page_obj": ruas})

@login_required()
def search_ruas(request):
    search_value = request.GET.get("q", "").strip()
    if not search_value:
        return redirect("contact:ruas_list")

    ruas = (
        Rua.objects
        .filter(owner=request.user)
        .filter(
            Q(nome__icontains=search_value) |
            Q(bairro__icontains=search_value)
        )
        .order_by("-id")
    )
    paginator = Paginator(ruas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "site_title": "Busca de Ruas - "
    }

    return render(
        request,
        "contact/rua_page.html",
        context=context
    )