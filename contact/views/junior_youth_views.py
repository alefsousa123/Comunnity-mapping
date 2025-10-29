from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from contact.models import GrupoPreJovens
from contact.forms import GrupoPreJovensForm
from contact.mixins import HistoricoAutomaticoMixin


class JuniorYouthHistoricoMixin(HistoricoAutomaticoMixin):
    """Mixin específico para views de grupos de pré-jovens"""
    pass

@login_required(login_url="contact:login")
def junior_youth_list(request):
    grupos = GrupoPreJovens.objects.filter(show=True, owner=request.user).order_by("-id")
    paginator = Paginator(grupos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "site_title": "Grupos de Pré-Jovens - "
    }
    return render(request, "contact/junior_youth_page.html", context)

@login_required(login_url="contact:login")
def junior_youth_detail(request, pk):
    grupo = get_object_or_404(GrupoPreJovens, pk=pk, show=True, owner=request.user)
    context = {
        "grupo": grupo,
        "site_title": f"{grupo.nome} - Grupo de Pré-Jovens"
    }
    return render(request, "contact/junior_youth.html", context)

@login_required(login_url="contact:login")
def junior_youth_create(request):
    historico_mixin = JuniorYouthHistoricoMixin()
    
    if request.method == "POST":
        form = GrupoPreJovensForm(request.POST, user=request.user)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.owner = request.user
            grupo.save()
            form.save_m2m()
            
            # Verificar se deve salvar no histórico
            ciclo_selecionado = form.cleaned_data.get('numero_ciclo_criacao')
            historico = historico_mixin.salvar_no_historico_se_necessario(
                grupo, ciclo_selecionado
            )
            
            if historico:
                messages.success(
                    request,
                    f'Grupo "{grupo.nome}" criado e adicionado ao histórico do ciclo {ciclo_selecionado}!'
                )
            else:
                messages.success(request, f'Grupo "{grupo.nome}" criado com sucesso!')
            
            return redirect("contact:grupoprejovens_detail", grupo.id)
    else:
        form = GrupoPreJovensForm(user=request.user)
    context = {
        "form": form,
        "prejovens": form.fields['pre_jovens'].queryset,
        "ruas": form.fields['rua'].queryset,
        "animadores": form.fields['animador'].queryset,
        "site_title": "Criar Grupo de Pré-Jovens"
    }
    return render(request, "contact/partials/_junior_youth_group-form.html", context)

@login_required(login_url="contact:login")
def junior_youth_update(request, pk):
    grupo = get_object_or_404(GrupoPreJovens, pk=pk, show=True, owner=request.user)
    if request.method == "POST":
        form = GrupoPreJovensForm(request.POST, instance=grupo, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("contact:grupoprejovens_detail", grupo.id)
    else:
        form = GrupoPreJovensForm(instance=grupo, user=request.user)
    context = {
        "form": form,
        "grupo": grupo,
        "prejovens": form.fields['pre_jovens'].queryset,
        "ruas": form.fields['rua'].queryset,
        "animadores": form.fields['animador'].queryset,
        "site_title": f"Editar Grupo: {grupo.nome}"
    }
    return render(request, "contact/partials/_junior_youth_group-form.html", context)

@login_required(login_url="contact:login")
def junior_youth_delete(request, pk):
    grupo = get_object_or_404(GrupoPreJovens, pk=pk, show=True, owner=request.user)
    confirmation = request.POST.get("confirmation", "yes")
    if request.method == "POST" and confirmation == "yes":
        grupo.delete()
        return redirect("contact:grupoprejovens_list")
    context = {
        "grupo": grupo,
        "confirmation": confirmation,
        "site_title": f"Deletar Grupo: {grupo.nome}"
    }
    return render(request, "contact/junior_youth.html", context)