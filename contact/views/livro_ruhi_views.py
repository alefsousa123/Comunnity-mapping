from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from contact.models import LivroRuhi
from contact.forms import LivroRuhiForm
from datetime import date


@login_required(login_url="contact:login")
def livro_ruhi_list(request):
    """Lista todos os livros Ruhi do usuário"""
    livros = LivroRuhi.objects.filter(usuario=request.user).order_by('nome_livro')
    
    # Estatísticas rápidas
    total_livros = livros.count()
    livros_concluidos = livros.filter(status='concluido').count()
    livros_em_andamento = livros.filter(status='em_andamento').count()
    livros_nao_iniciados = livros.filter(status='nao_iniciado').count()
    
    context = {
        'livros': livros,
        'total_livros': total_livros,
        'livros_concluidos': livros_concluidos,
        'livros_em_andamento': livros_em_andamento,
        'livros_nao_iniciados': livros_nao_iniciados,
        'site_title': 'Meus Livros Ruhi'
    }
    
    return render(request, 'contact/livro_ruhi_list.html', context)


@login_required(login_url="contact:login")
def livro_ruhi_create(request):
    """Criar um novo livro Ruhi"""
    if request.method == 'POST':
        form = LivroRuhiForm(request.POST, usuario=request.user)
        if form.is_valid():
            try:
                livro = form.save()
                messages.success(request, f'Livro "{livro.get_nome_livro_display()}" adicionado com sucesso!')
                return redirect('contact:livro_ruhi_list')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {str(e)}')
    else:
        form = LivroRuhiForm(usuario=request.user)
    
    context = {
        'form': form,
        'site_title': 'Adicionar Livro Ruhi',
        'form_title': 'Adicionar Livro Ruhi'
    }
    
    return render(request, 'contact/livro_ruhi_form.html', context)


@login_required(login_url="contact:login")
def livro_ruhi_update(request, pk):
    """Editar um livro Ruhi existente"""
    livro = get_object_or_404(LivroRuhi, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = LivroRuhiForm(request.POST, instance=livro, usuario=request.user)
        if form.is_valid():
            livro = form.save()
            messages.success(request, f'Livro "{livro.get_nome_livro_display()}" atualizado com sucesso!')
            return redirect('contact:livro_ruhi_list')
    else:
        form = LivroRuhiForm(instance=livro, usuario=request.user)
    
    context = {
        'form': form,
        'livro': livro,
        'site_title': f'Editar {livro.get_nome_livro_display()}',
        'form_title': f'Editar {livro.get_nome_livro_display()}'
    }
    
    return render(request, 'contact/livro_ruhi_form.html', context)


@login_required(login_url="contact:login")
def livro_ruhi_delete(request, pk):
    """Deletar um livro Ruhi"""
    livro = get_object_or_404(LivroRuhi, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', 'no')
        if confirmation == 'yes':
            nome_livro = livro.get_nome_livro_display()
            livro.delete()
            messages.success(request, f'Livro "{nome_livro}" removido com sucesso!')
            return redirect('contact:livro_ruhi_list')
    
    context = {
        'livro': livro,
        'site_title': f'Excluir {livro.get_nome_livro_display()}',
        'confirmation': request.POST.get('confirmation', 'no')
    }
    
    return render(request, 'contact/livro_ruhi_detail.html', context)


@login_required(login_url="contact:login")
def livro_ruhi_detail(request, pk):
    """Detalhes de um livro Ruhi específico"""
    livro = get_object_or_404(LivroRuhi, pk=pk, usuario=request.user)
    
    context = {
        'livro': livro,
        'site_title': f'{livro.get_nome_livro_display()}'
    }
    
    return render(request, 'contact/livro_ruhi_detail.html', context)


@login_required(login_url="contact:login")
def livro_ruhi_marcar_iniciado(request, pk):
    """Marcar um livro como iniciado (hoje)"""
    livro = get_object_or_404(LivroRuhi, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        livro.data_inicio = date.today()
        livro.status = 'em_andamento'
        livro.save()
        messages.success(request, f'Livro "{livro.get_nome_livro_display()}" marcado como iniciado!')
    
    return redirect('contact:livro_ruhi_list')


@login_required(login_url="contact:login")
def livro_ruhi_marcar_concluido(request, pk):
    """Marcar um livro como concluído (hoje)"""
    livro = get_object_or_404(LivroRuhi, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        if not livro.data_inicio:
            livro.data_inicio = date.today()
        livro.data_termino = date.today()
        livro.status = 'concluido'
        livro.save()
        messages.success(request, f'Livro "{livro.get_nome_livro_display()}" marcado como concluído!')
    
    return redirect('contact:livro_ruhi_list')