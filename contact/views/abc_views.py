from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from contact.models import AulaCrianca
from contact.forms import AulaCriancaForm
from contact.mixins import HistoricoAutomaticoMixin


class ABCHistoricoMixin(HistoricoAutomaticoMixin):
    """Mixin específico para views de aulas de criança"""
    pass

@login_required(login_url="contact:login")
def abc_list(request):
    abcs = AulaCrianca.objects.filter(show=True, owner=request.user).order_by("-id")
    paginator = Paginator(abcs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "site_title": "Aulas Bahá'í de Crianças - "
    }
    return render(request, "contact/abc_page.html", context)

@login_required(login_url="contact:login")
def abc_detail(request, pk):
    abc = get_object_or_404(AulaCrianca, pk=pk, show=True, owner=request.user)
    context = {
        "abc": abc,
        "site_title": f"{abc.nome} - Aula Bahá'í de Criança"
    }
    return render(request, "contact/abc.html", context)

@login_required(login_url="contact:login")
def abc_create(request):
    historico_mixin = ABCHistoricoMixin()
    
    if request.method == "POST":
        form = AulaCriancaForm(request.POST, user=request.user)
        if form.is_valid():
            abc = form.save(commit=False)
            abc.owner = request.user
            abc.save()
            form.save_m2m()
            
            # Verificar se deve salvar no histórico
            ciclo_selecionado = form.cleaned_data.get('numero_ciclo_criacao')
            historico = historico_mixin.salvar_no_historico_se_necessario(
                abc, ciclo_selecionado
            )
            
            if historico:
                messages.success(
                    request,
                    f'Aula "{abc.nome}" criada e adicionada ao histórico do ciclo {ciclo_selecionado}!'
                )
            else:
                messages.success(request, f'Aula "{abc.nome}" criada com sucesso!')
            
            return redirect("contact:aulacrianca_detail", abc.id)
    else:
        form = AulaCriancaForm(user=request.user)
    # Passe os participantes e ruas para o template
    participantes = form.fields['participantes'].queryset
    ruas = form.fields['rua'].queryset
    # Exemplo para abc_create e abc_update
    professores = form.fields['professor'].queryset
    context = {
        "form": form,
        "participantes": participantes,
        "ruas": ruas,
        "professores": professores,
        "site_title": "Criar ABC"
    }
    return render(request, "contact/partials/_abc-form.html", context)

@login_required(login_url="contact:login")
def abc_update(request, pk):
    abc = get_object_or_404(AulaCrianca, pk=pk, show=True, owner=request.user)
    if request.method == "POST":
        post_data = request.POST.copy()
        # Se não veio 'rua' no POST, mantém o valor antigo
        if 'rua' not in post_data or not post_data.get('rua'):
            post_data['rua'] = abc.rua_id
        # Se não veio 'participantes' no POST, mantém os antigos
        if 'participantes' not in post_data or not post_data.getlist('participantes'):
            post_data.setlist('participantes', [str(pk) for pk in abc.participantes.values_list('pk', flat=True)])
        form = AulaCriancaForm(post_data, instance=abc, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("contact:aulacrianca_detail", abc.id)
        else:
            print(form.errors)
    else:
        form = AulaCriancaForm(instance=abc, user=request.user)
    participantes = form.fields['participantes'].queryset
    ruas = form.fields['rua'].queryset
    professores = form.fields['professor'].queryset
    context = {
        "form": form,
        "abc": abc,
        "participantes": participantes,
        "ruas": ruas,
        "professores": professores,
        "site_title": f"Editar ABC: {abc.nome}"
    }
    return render(request, "contact/partials/_abc-form.html", context)

@login_required(login_url="contact:login")
def abc_delete(request, pk):
    abc = get_object_or_404(AulaCrianca, pk=pk, show=True, owner=request.user)
    confirmation = request.POST.get("confirmation", "yes")
    if request.method == "POST" and confirmation == "yes":
        abc.delete()
        return redirect("contact:aulacrianca_list")
    context = {
        "abc": abc,
        "confirmation": confirmation,
        "site_title": f"Deletar ABC: {abc.nome}"
    }
    return render(request, "contact/abc.html", context)