from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models import ConfiguracaoEstatisticas
from ..forms import CyclePlanForm


@login_required
def gerenciar_planos_ciclos(request):
    """View para gerenciar múltiplos planos de ciclos"""
    planos = ConfiguracaoEstatisticas.objects.filter(
        owner=request.user
    ).order_by('-principal', 'titulo_plano')
    
    context = {
        'planos': planos,
        'titulo': 'Gerenciar Planos de Ciclos'
    }
    return render(request, 'contact/cycle_management.html', context)


@login_required
def criar_plano_ciclo(request):
    """View para criar um novo plano de ciclos"""
    if request.method == 'POST':
        form = CyclePlanForm(user=request.user, data=request.POST)
        if form.is_valid():
            plano = form.save(commit=False)
            plano.owner = request.user
            plano.save()
            
            messages.success(
                request, 
                f'Plano "{plano.titulo_plano}" criado com sucesso!'
            )
            return redirect('gerenciar_planos_ciclos')
    else:
        form = CyclePlanForm(user=request.user)
    
    context = {
        'form': form,
        'titulo': 'Criar Novo Plano de Ciclos',
        'action': 'Criar'
    }
    return render(request, 'contact/cycle_plan_form.html', context)


@login_required
def editar_plano_ciclo(request, plano_id):
    """View para editar um plano de ciclos existente"""
    plano = get_object_or_404(
        ConfiguracaoEstatisticas, 
        id=plano_id, 
        owner=request.user
    )
    
    if request.method == 'POST':
        form = CyclePlanForm(
            user=request.user, 
            data=request.POST, 
            instance=plano
        )
        if form.is_valid():
            plano = form.save()
            
            messages.success(
                request, 
                f'Plano "{plano.titulo_plano}" atualizado com sucesso!'
            )
            return redirect('gerenciar_planos_ciclos')
    else:
        form = CyclePlanForm(user=request.user, instance=plano)
    
    context = {
        'form': form,
        'plano': plano,
        'titulo': f'Editar Plano: {plano.titulo_plano}',
        'action': 'Salvar Alterações'
    }
    return render(request, 'contact/cycle_plan_form.html', context)


@login_required
@require_http_methods(["POST"])
def excluir_plano_ciclo(request, plano_id):
    """View para excluir um plano de ciclos"""
    plano = get_object_or_404(
        ConfiguracaoEstatisticas, 
        id=plano_id, 
        owner=request.user
    )
    
    titulo = plano.titulo_plano
    
    # Verificar se há atividades vinculadas a este plano
    atividades_vinculadas = (
        plano.grupos_prejovens.count() + 
        plano.aulas_criancas.count() +
        plano.circulos_estudo.count() +
        plano.estudos_atuais.count() +
        plano.historicos_estudo.count()
    )
    
    if atividades_vinculadas > 0:
        messages.error(
            request,
            f'Não é possível excluir o plano "{titulo}" pois há '
            f'{atividades_vinculadas} atividade(s) vinculada(s) a ele.'
        )
    else:
        plano.delete()
        messages.success(
            request,
            f'Plano "{titulo}" excluído com sucesso!'
        )
    
    return redirect('gerenciar_planos_ciclos')


@login_required
def obter_ciclos_plano(request, plano_id):
    """View AJAX para obter ciclos disponíveis de um plano específico"""
    try:
        plano = get_object_or_404(
            ConfiguracaoEstatisticas,
            id=plano_id,
            owner=request.user
        )
        
        ciclos = plano.obter_ciclos_disponiveis()
        
        # Formatar ciclos para o frontend
        ciclos_data = []
        for numero, periodo in ciclos:
            ciclos_data.append({
                'numero': numero,
                'inicio': periodo['inicio'].strftime('%d/%m/%Y'),
                'fim': periodo['fim'].strftime('%d/%m/%Y'),
                'label': f'Ciclo {numero} ({periodo["inicio"].strftime("%m/%Y")} - {periodo["fim"].strftime("%m/%Y")})'
            })
        
        return JsonResponse({
            'success': True,
            'ciclos': ciclos_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def alternar_plano_principal(request, plano_id):
    """View para alternar qual plano é o principal"""
    plano = get_object_or_404(
        ConfiguracaoEstatisticas,
        id=plano_id,
        owner=request.user
    )
    
    if not plano.principal:
        # Remover principal de outros planos
        ConfiguracaoEstatisticas.objects.filter(
            owner=request.user,
            principal=True
        ).update(principal=False)
        
        # Tornar este plano o principal
        plano.principal = True
        plano.save()
        
        messages.success(
            request,
            f'Plano "{plano.titulo_plano}" definido como principal!'
        )
    else:
        messages.info(
            request,
            f'Plano "{plano.titulo_plano}" já é o principal.'
        )
    
    return redirect('gerenciar_planos_ciclos')


@login_required
def obter_info_plano(request, plano_id):
    """View AJAX para obter informações de um plano"""
    try:
        plano = get_object_or_404(
            ConfiguracaoEstatisticas,
            id=plano_id,
            owner=request.user
        )
        
        # Calcular ciclo atual
        ciclo_atual_info = plano.calcular_ciclo_atual()
        ciclo_atual_numero = ciclo_atual_info['numero'] if isinstance(ciclo_atual_info, dict) else ciclo_atual_info
        
        return JsonResponse({
            'success': True,
            'plano': {
                'id': plano.id,
                'titulo': plano.titulo_plano,
                'descricao': plano.descricao,
                'principal': plano.principal,
                'data_inicio_plano': plano.data_inicio_plano.strftime('%d/%m/%Y'),
                'duracao_ciclo_meses': plano.duracao_ciclo_meses,
                'total_ciclos_plano': plano.total_ciclos_plano,
                'ciclo_atual': ciclo_atual_numero,
                'ciclo_atual_info': ciclo_atual_info,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def obter_info_plano_teste(request, plano_id):
    """View de teste para AJAX - sem autenticação"""
    try:
        # Simular dados do plano 1 (principal)
        if plano_id == 1:
            return JsonResponse({
                'success': True,
                'plano': {
                    'id': 1,
                    'titulo': 'Plano Principal 2024-2025',
                    'descricao': 'Plano de nove anos principal',
                    'principal': True,
                    'data_inicio_plano': '01/01/2024',
                    'duracao_ciclo_meses': 3,
                    'total_ciclos_plano': 19,
                    'ciclo_atual': 16,  # Ciclo atual real
                    'ciclo_atual_info': {
                        'numero': 16,
                        'nome': 'Ciclo 16',
                        'progresso': 31.5
                    }
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'plano': {
                    'id': plano_id,
                    'titulo': f'Plano {plano_id}',
                    'descricao': 'Plano de teste',
                    'principal': False,
                    'data_inicio_plano': '01/01/2024',
                    'duracao_ciclo_meses': 3,
                    'total_ciclos_plano': 15,
                    'ciclo_atual': 5,
                    'ciclo_atual_info': {
                        'numero': 5,
                        'nome': 'Ciclo 5',
                        'progresso': 50.0
                    }
                }
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })