from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from contact.models import ReuniaoDevocional, Rua
from contact.forms import ReuniaoDevocionalForm
from contact.mixins import HistoricoAutomaticoMixin


class ReuniaoDevocionalHistoricoMixin(HistoricoAutomaticoMixin):
    """Mixin específico para views de reuniões devocionais"""
    pass

@login_required
def reuniao_devocional_list(request):
    """Lista todas as reuniões devocionais do usuário."""
    reunioes = ReuniaoDevocional.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(reunioes, 10)  # 10 reuniões por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reunioes': page_obj,
        'total_reunioes': reunioes.count(),
    }
    
    return render(request, 'contact/reuniao_devocional_list.html', context)

@login_required
def reuniao_devocional_detail(request, pk):
    """Detalhes de uma reunião devocional específica."""
    reuniao = get_object_or_404(ReuniaoDevocional, pk=pk, usuario=request.user)
    
    context = {
        'reuniao': reuniao,
    }
    
    return render(request, 'contact/reuniao_devocional_detail.html', context)

@login_required
def reuniao_devocional_create(request):
    """Criar uma nova reunião devocional."""
    historico_mixin = ReuniaoDevocionalHistoricoMixin()
    
    if request.method == 'POST':
        form = ReuniaoDevocionalForm(request.POST, user=request.user)
        if form.is_valid():
            reuniao = form.save(commit=False)
            reuniao.usuario = request.user
            reuniao.save()
            form.save_m2m()  # Para campos Many-to-Many
            
            # Verificar se deve salvar no histórico
            ciclo_selecionado = form.cleaned_data.get('numero_ciclo_criacao')
            historico = historico_mixin.salvar_no_historico_se_necessario(
                reuniao, ciclo_selecionado
            )
            
            if historico:
                messages.success(
                    request, 
                    f'Reunião "{reuniao.nome}" criada e adicionada ao histórico do ciclo {ciclo_selecionado}!'
                )
            else:
                messages.success(request, 'Reunião Devocional criada com sucesso!')
            
            return redirect('contact:reuniao_devocional_detail', pk=reuniao.pk)
    else:
        form = ReuniaoDevocionalForm(user=request.user)
    
    context = {
        'form': form,
        'action': 'Criar',
    }
    
    return render(request, 'contact/reuniao_devocional_form.html', context)

@login_required
def reuniao_devocional_update(request, pk):
    """Editar uma reunião devocional existente."""
    reuniao = get_object_or_404(ReuniaoDevocional, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = ReuniaoDevocionalForm(request.POST, instance=reuniao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reunião Devocional atualizada com sucesso!')
            return redirect('contact:reuniao_devocional_detail', pk=reuniao.pk)
    else:
        form = ReuniaoDevocionalForm(instance=reuniao)
    
    context = {
        'form': form,
        'reuniao': reuniao,
        'action': 'Editar',
    }
    
    return render(request, 'contact/reuniao_devocional_form.html', context)

@login_required
def reuniao_devocional_delete(request, pk):
    """Deletar uma reunião devocional."""
    reuniao = get_object_or_404(ReuniaoDevocional, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        reuniao.delete()
        messages.success(request, 'Reunião Devocional deletada com sucesso!')
        return redirect('contact:reuniao_devocional_list')
    
    context = {
        'reuniao': reuniao,
    }
    
    return render(request, 'contact/reuniao_devocional_delete.html', context)