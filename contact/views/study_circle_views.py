from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from contact.models import CirculoEstudo
from contact.forms import CirculoEstudoForm
from contact.mixins import HistoricoAutomaticoMixin


class StudyCircleHistoricoMixin(HistoricoAutomaticoMixin):
    """Mixin específico para views de círculos de estudo"""
    pass

@login_required(login_url="contact:login")
def study_circle_list(request):
    circulos = CirculoEstudo.objects.filter(show=True, owner=request.user).order_by("-id")
    paginator = Paginator(circulos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "site_title": "Círculos de Estudo - "
    }
    return render(request, "contact/study_circle_page.html", context)

@login_required(login_url="contact:login")
def study_circle_detail(request, pk):
    circulo = get_object_or_404(CirculoEstudo, pk=pk, show=True, owner=request.user)
    confirmation = request.POST.get("confirmation", "yes")
    context = {
        "circulo": circulo,
        "confirmation": confirmation,
        "site_title": f"{circulo.nome} - Círculo de Estudo"
    }
    return render(request, "contact/study_circle.html", context)

@login_required(login_url="contact:login")
def study_circle_create(request):
    historico_mixin = StudyCircleHistoricoMixin()
    
    if request.method == "POST":
        form = CirculoEstudoForm(request.POST, user=request.user)
        if form.is_valid():
            circulo = form.save(commit=False)
            circulo.owner = request.user
            circulo.show = True  # se necessário
            circulo.save()
            form.save_m2m()  # se houver campos ManyToMany
            
            # Verificar se deve salvar no histórico
            ciclo_selecionado = form.cleaned_data.get('numero_ciclo_criacao')
            historico = historico_mixin.salvar_no_historico_se_necessario(
                circulo, ciclo_selecionado
            )
            
            if historico:
                messages.success(
                    request,
                    f'Círculo "{circulo.nome}" criado e adicionado ao histórico do ciclo {ciclo_selecionado}!'
                )
            else:
                messages.success(request, f'Círculo "{circulo.nome}" criado com sucesso!')
            
            return redirect("contact:circuloestudo_list")
    else:
        form = CirculoEstudoForm(user=request.user)
    context = {
        "form": form,
        "participantes": form.fields['participantes'].queryset,
        "professores": form.fields['tutor'].queryset,
        "ruas": form.fields['rua'].queryset,
        "site_title": "Criar Círculo de Estudo"
    }
    return render(request, "contact/partials/study_circle-form.html", context)

@login_required(login_url="contact:login")
def study_circle_update(request, pk):
    circulo = get_object_or_404(CirculoEstudo, pk=pk, show=True, owner=request.user)
    if request.method == "POST":
        form = CirculoEstudoForm(request.POST, instance=circulo, user=request.user)
        if form.is_valid():
            circulo = form.save(commit=False)
            circulo.owner = request.user  # Garante que o owner não muda
            circulo.save()
            form.save_m2m()
            return redirect("contact:circuloestudo_detail", circulo.id)
    else:
        form = CirculoEstudoForm(instance=circulo, user=request.user)
    context = {
        "form": form,
        "circulo": circulo,
        "participantes": form.fields['participantes'].queryset,
        "professores": form.fields['tutor'].queryset,
        "ruas": form.fields['rua'].queryset,
        "site_title": f"Editar Círculo: {circulo.nome}"
    }
    return render(request, "contact/partials/study_circle-form.html", context)

@login_required(login_url="contact:login")
def study_circle_delete(request, pk):
    circulo = get_object_or_404(CirculoEstudo, pk=pk, show=True, owner=request.user)
    confirmation = request.POST.get("confirmation", "yes")
    if request.method == "POST" and confirmation == "yes":
        circulo.delete()
        return redirect("contact:circuloestudo_list")
    context = {
        "circulo": circulo,
        "confirmation": confirmation,
        "site_title": f"Deletar Círculo: {circulo.nome}"
    }
    return render(request, "contact/study_circle.html", context)