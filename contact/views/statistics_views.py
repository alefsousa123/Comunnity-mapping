from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from contact.models import (
    ConfiguracaoEstatisticas, 
    EstatisticasEditaveis,
    HistoricoCiclo,
    GrupoPreJovens, 
    AulaCrianca, 
    CirculoEstudo,
    ReuniaoDevocional,
    GrupoFamilias,
    Rua,
    Familia,
    Contact,
    EstudoAtual,
    CategoriaLivro,
    HistoricoEstudo
)


@login_required
def dashboard_estatisticas(request):
    """Dashboard principal de estatísticas"""
    
    # Obter ou criar configurações
    configuracao, created = ConfiguracaoEstatisticas.objects.get_or_create(
        owner=request.user,
        defaults={
            'titulo_plano': 'Plano de 9 Anos',
            'data_inicio_plano': timezone.now().date(),
            'duracao_ciclo_meses': 3,
            'total_ciclos_plano': 36,
            'ativo': True
        }
    )
    
    # Obter ou criar estatísticas editáveis
    estatisticas_editaveis, created = EstatisticasEditaveis.objects.get_or_create(
        owner=request.user
    )
    
    # Calcular estatísticas do banco de dados
    estatisticas_bd = calcular_estatisticas_bd(request.user)
    
    # Calcular ciclo atual usando o novo método
    ciclo_atual = configuracao.calcular_ciclo_atual()
    
    # Calcular atividades novas do ciclo atual
    atividades_novas_ciclo = calcular_atividades_novas_ciclo(request.user, configuracao)
    
    # Preparar dados comparativos
    dados_comparativos = {
        'grupos_prejovens': {
            'editavel': estatisticas_editaveis.total_grupos_prejovens,
            'banco': estatisticas_bd['grupos_prejovens'],
            'diferenca': estatisticas_editaveis.total_grupos_prejovens - estatisticas_bd['grupos_prejovens']
        },
        'aulas_criancas': {
            'editavel': estatisticas_editaveis.total_aulas_criancas,
            'banco': estatisticas_bd['aulas_criancas'],
            'diferenca': estatisticas_editaveis.total_aulas_criancas - estatisticas_bd['aulas_criancas']
        },
        'circulos_estudo': {
            'editavel': estatisticas_editaveis.total_circulos_estudo,
            'banco': estatisticas_bd['circulos_estudo'],
            'diferenca': estatisticas_editaveis.total_circulos_estudo - estatisticas_bd['circulos_estudo']
        },
        'reunioes_devocionais': {
            'editavel': estatisticas_editaveis.total_reunioes_devocionais,
            'banco': estatisticas_bd['reunioes_devocionais'],
            'diferenca': estatisticas_editaveis.total_reunioes_devocionais - estatisticas_bd['reunioes_devocionais']
        },
        'participantes_total': {
            'editavel': estatisticas_editaveis.total_participantes,
            'banco': estatisticas_bd['participantes_total'],
            'diferenca': estatisticas_editaveis.total_participantes - estatisticas_bd['participantes_total']
        }
    }
    
    # Obter dados de crescimento dos últimos ciclos
    dados_crescimento = obter_dados_crescimento(request.user)
    
    context = {
        'configuracao': configuracao,
        'estatisticas_editaveis': estatisticas_editaveis,
        'estatisticas_bd': estatisticas_bd,
        'dados_comparativos': dados_comparativos,
        'ciclo_atual': ciclo_atual,
        'atividades_novas_ciclo': atividades_novas_ciclo,
        'dados_crescimento': dados_crescimento,
    }
    
    return render(request, 'contact/statistics_dashboard.html', context)


@login_required
def editar_configuracao(request):
    """Configurações dos planos de ciclos com gerenciamento de múltiplos planos"""
    # Buscar plano principal ou criar se não existir
    plano_principal = ConfiguracaoEstatisticas.objects.filter(
        owner=request.user, 
        principal=True
    ).first()
    
    if not plano_principal:
        plano_principal = ConfiguracaoEstatisticas.objects.create(
            owner=request.user,
            titulo_plano='Plano Principal',
            data_inicio_plano=timezone.now().date(),
            duracao_ciclo_meses=3,
            total_ciclos_plano=36,
            ativo=True,
            principal=True
        )
    
    # Buscar todos os planos do usuário
    todos_planos = ConfiguracaoEstatisticas.objects.filter(
        owner=request.user
    ).order_by('-principal', 'titulo_plano')
    
    # Verificar se é uma operação em um plano específico
    plano_id = request.GET.get('plano_id')
    if plano_id:
        try:
            plano_selecionado = ConfiguracaoEstatisticas.objects.get(
                id=plano_id, 
                owner=request.user
            )
        except ConfiguracaoEstatisticas.DoesNotExist:
            plano_selecionado = plano_principal
    else:
        plano_selecionado = plano_principal
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'criar_plano':
            # Criar novo plano
            from ..forms import CyclePlanForm
            form = CyclePlanForm(user=request.user, data=request.POST)
            if form.is_valid():
                novo_plano = form.save(commit=False)
                novo_plano.owner = request.user
                novo_plano.save()
                messages.success(request, f'✅ Plano "{novo_plano.titulo_plano}" criado com sucesso!')
                return redirect('contact:editar_configuracao')
            else:
                messages.error(request, '❌ Erro ao criar plano. Verifique os dados.')
        
        elif action == 'editar_plano':
            # Editar plano existente
            plano_id = request.POST.get('plano_id')
            try:
                plano = ConfiguracaoEstatisticas.objects.get(
                    id=plano_id, 
                    owner=request.user
                )
                plano.titulo_plano = request.POST.get('titulo_plano', plano.titulo_plano)
                plano.descricao = request.POST.get('descricao', plano.descricao)
                plano.data_inicio_plano = request.POST.get('data_inicio_plano', plano.data_inicio_plano)
                plano.duracao_ciclo_meses = int(request.POST.get('duracao_ciclo_meses', 3))
                plano.total_ciclos_plano = int(request.POST.get('total_ciclos_plano', 36))
                plano.ativo = request.POST.get('ativo') == 'on'
                
                # Gerenciar plano principal
                if request.POST.get('principal') == 'on':
                    plano.principal = True
                
                plano.save()
                messages.success(request, f'✅ Plano "{plano.titulo_plano}" atualizado com sucesso!')
                return redirect('contact:editar_configuracao')
            except ConfiguracaoEstatisticas.DoesNotExist:
                messages.error(request, '❌ Plano não encontrado.')
        
        elif action == 'excluir_plano':
            # Excluir plano
            plano_id = request.POST.get('plano_id')
            try:
                plano = ConfiguracaoEstatisticas.objects.get(
                    id=plano_id, 
                    owner=request.user
                )
                if plano.principal:
                    messages.error(request, '❌ Não é possível excluir o plano principal.')
                else:
                    titulo = plano.titulo_plano
                    plano.delete()
                    messages.success(request, f'✅ Plano "{titulo}" excluído com sucesso!')
                return redirect('contact:editar_configuracao')
            except ConfiguracaoEstatisticas.DoesNotExist:
                messages.error(request, '❌ Plano não encontrado.')
        
        elif action == 'definir_principal':
            # Definir como plano principal
            plano_id = request.POST.get('plano_id')
            try:
                # Remover principal de outros planos
                ConfiguracaoEstatisticas.objects.filter(
                    owner=request.user,
                    principal=True
                ).update(principal=False)
                
                # Definir novo principal
                plano = ConfiguracaoEstatisticas.objects.get(
                    id=plano_id, 
                    owner=request.user
                )
                plano.principal = True
                plano.save()
                
                messages.success(request, f'✅ "{plano.titulo_plano}" definido como plano principal!')
                return redirect('contact:editar_configuracao')
            except ConfiguracaoEstatisticas.DoesNotExist:
                messages.error(request, '❌ Plano não encontrado.')
    
    # Preparar formulário para novo plano
    from ..forms import CyclePlanForm
    form_novo_plano = CyclePlanForm(user=request.user)
    
    context = {
        'plano_principal': plano_principal,
        'todos_planos': todos_planos,
        'plano_selecionado': plano_selecionado,
        'form_novo_plano': form_novo_plano,
        'total_planos': todos_planos.count(),
    }
    
    return render(request, 'contact/configuracao_ciclos.html', context)


@login_required
def historico_ciclos(request):
    """Página para visualizar histórico de ciclos anteriores"""
    dados_crescimento = obter_dados_crescimento(request.user)
    
    context = {
        'ciclos_historicos': dados_crescimento['ciclos_historicos'],
        'crescimento_total': dados_crescimento['crescimento_total'],
        'ciclo_atual': dados_crescimento['ciclo_atual'],
        'configuracao': dados_crescimento['configuracao']
    }
    
    return render(request, 'contact/historico_ciclos.html', context)


@login_required
def historico_ciclo_detalhado(request, numero_ciclo):
    """Página detalhada de um ciclo específico, igual ao dashboard"""
    configuracao = ConfiguracaoEstatisticas.objects.filter(
        owner=request.user, ativo=True
    ).first()
    
    if not configuracao:
        messages.error(request, "Configure primeiro o sistema de ciclos.")
        return redirect('contact:editar_configuracao')
    
    # Buscar histórico do ciclo específico
    historico = get_object_or_404(HistoricoCiclo, 
                                 configuracao=configuracao, 
                                 numero_ciclo=numero_ciclo)
    
    # Buscar estatísticas editáveis históricas (se existirem)
    try:
        estatisticas_editaveis_historicas = historico.estatisticas_editaveis
        tem_estatisticas_editaveis = True
    except:
        # Se não existir, usar dados básicos do histórico
        estatisticas_editaveis_historicas = None
        tem_estatisticas_editaveis = False
    
    # Buscar detalhes dos livros para este histórico
    livros_detalhados = historico.detalhes_livros.all().order_by(
        'categoria', 'nome_livro'
    )
    
    # Organizar livros por categoria (igual ao dashboard)
    livros_por_categoria = {}
    total_livros_iniciados = 0
    total_livros_concluidos = 0
    
    # Preparar estatísticas detalhadas por livro individual
    livros_detalhados_organizados = []
    
    # Mapear categorias do modelo para exibição
    categoria_display_map = {
        'sequencia': 'Sequência',
        'abc': 'ABC',
        'prejovens': 'Pré-jovens',
        'outros': 'Outros'
    }
    
    categoria_cor_map = {
        'sequencia': '#007bff',
        'abc': '#28a745',
        'prejovens': '#ffc107',
        'outros': '#6c757d'
    }
    
    for categoria_code in ['sequencia', 'abc', 'prejovens', 'outros']:
        categoria_nome = categoria_display_map[categoria_code]
        
        # Filtrar livros desta categoria
        livros_categoria = livros_detalhados.filter(categoria=categoria_code)
        
        iniciados_categoria = sum(l.quantidade_iniciados for l in livros_categoria)
        concluidos_categoria = sum(l.quantidade_concluidos for l in livros_categoria)
        
        if iniciados_categoria > 0 or concluidos_categoria > 0:
            livros_por_categoria[categoria_nome] = {
                'iniciados': iniciados_categoria,
                'concluidos': concluidos_categoria,
                'total': iniciados_categoria + concluidos_categoria,
                'cor': categoria_cor_map[categoria_code],
                'ordem': list(categoria_display_map.keys()).index(categoria_code)
            }
            
            total_livros_iniciados += iniciados_categoria
            total_livros_concluidos += concluidos_categoria
        
        # Adicionar livros individuais
        for livro in livros_categoria:
            if livro.quantidade_iniciados > 0 or livro.quantidade_concluidos > 0:
                livros_detalhados_organizados.append({
                    'nome': livro.nome_livro,
                    'categoria': categoria_nome,
                    'cor_categoria': categoria_cor_map[categoria_code],
                    'iniciados': livro.quantidade_iniciados,
                    'concluidos': livro.quantidade_concluidos,
                    'total': livro.quantidade_iniciados + livro.quantidade_concluidos,
                    'categoria_ordem': list(categoria_display_map.keys()).index(categoria_code)
                })
    
    # Criar dados separados para estatisticas_editaveis e estatisticas_bd
    # exatamente como na página principal
    
    if tem_estatisticas_editaveis:
        # estatisticas_editaveis: dados editáveis salvos pelo usuário
        estatisticas_editaveis_dict = {
            'total_grupos_prejovens': estatisticas_editaveis_historicas.total_grupos_prejovens,
            'total_aulas_criancas': estatisticas_editaveis_historicas.total_aulas_criancas,
            'total_circulos_estudo': estatisticas_editaveis_historicas.total_circulos_estudo,
            'total_reunioes_devocionais': estatisticas_editaveis_historicas.total_reunioes_devocionais,
            'participantes_prejovens': estatisticas_editaveis_historicas.participantes_prejovens,
            'participantes_criancas': estatisticas_editaveis_historicas.participantes_criancas,
            'participantes_circulos': estatisticas_editaveis_historicas.participantes_circulos,
            'participantes_devocionais': estatisticas_editaveis_historicas.participantes_devocionais,
            'participantes_prejovens_bahais': estatisticas_editaveis_historicas.participantes_prejovens_bahais,
            'participantes_criancas_bahais': estatisticas_editaveis_historicas.participantes_criancas_bahais,
            'participantes_circulos_bahais': estatisticas_editaveis_historicas.participantes_circulos_bahais,
            'participantes_devocionais_bahais': estatisticas_editaveis_historicas.participantes_devocionais_bahais,
            # Calcular totais manualmente já que são propriedades calculadas
            'total_participantes': (estatisticas_editaveis_historicas.participantes_prejovens +
                                   estatisticas_editaveis_historicas.participantes_criancas +
                                   estatisticas_editaveis_historicas.participantes_circulos +
                                   estatisticas_editaveis_historicas.participantes_devocionais),
            'total_participantes_bahais': (estatisticas_editaveis_historicas.participantes_prejovens_bahais +
                                          estatisticas_editaveis_historicas.participantes_criancas_bahais +
                                          estatisticas_editaveis_historicas.participantes_circulos_bahais +
                                          estatisticas_editaveis_historicas.participantes_devocionais_bahais),
            # Detalhamentos das atividades
            'animadores_prejovens': estatisticas_editaveis_historicas.animadores_prejovens,
            'locais_prejovens': estatisticas_editaveis_historicas.locais_prejovens,
            'professores_criancas': estatisticas_editaveis_historicas.professores_criancas,
            'series_criancas': estatisticas_editaveis_historicas.series_criancas,
            'tutores_circulos': estatisticas_editaveis_historicas.tutores_circulos,
            'livros_circulos': estatisticas_editaveis_historicas.livros_circulos,
            'circulos_concluidos': estatisticas_editaveis_historicas.circulos_concluidos,
            'facilitadores_devocionais': estatisticas_editaveis_historicas.facilitadores_devocionais,
            # Demografia editável
            'total_criancas': estatisticas_editaveis_historicas.total_criancas,
            'total_prejovens': estatisticas_editaveis_historicas.total_prejovens,
            'total_jovens': estatisticas_editaveis_historicas.total_jovens,
            'total_adultos': estatisticas_editaveis_historicas.total_adultos,
        }
        
        # estatisticas_bd: dados calculados do sistema (salvos no histórico)
        estatisticas_bd_dict = {
            'grupos_prejovens': historico.sistema_grupos_prejovens,
            'aulas_criancas': historico.sistema_aulas_criancas,
            'circulos_estudo': historico.sistema_circulos_estudo,
            'reunioes_devocionais': historico.sistema_reunioes_devocionais,
            'participantes_prejovens': historico.sistema_participantes_prejovens,
            'participantes_criancas': historico.sistema_participantes_criancas,
            'participantes_circulos': historico.sistema_participantes_circulos,
            'participantes_devocionais': historico.sistema_participantes_devocionais,
            'participantes_prejovens_bahais': historico.sistema_participantes_prejovens_bahais,
            'participantes_criancas_bahais': historico.sistema_participantes_criancas_bahais,
            'participantes_circulos_bahais': historico.sistema_participantes_circulos_bahais,
            'participantes_devocionais_bahais': historico.sistema_participantes_devocionais_bahais,
            'participantes_total': (historico.sistema_participantes_prejovens + 
                                   historico.sistema_participantes_criancas +
                                   historico.sistema_participantes_circulos + 
                                   historico.sistema_participantes_devocionais),
            'participantes_total_bahais': (historico.sistema_participantes_prejovens_bahais + 
                                          historico.sistema_participantes_criancas_bahais +
                                          historico.sistema_participantes_circulos_bahais + 
                                          historico.sistema_participantes_devocionais_bahais),
            'total_familias': historico.sistema_grupos_familias,
            # Demografia do sistema (usar os novos campos)
            'criancas_sistema': historico.sistema_total_criancas,
            'prejovens_sistema': historico.sistema_total_prejovens,
            'jovens_sistema': historico.sistema_total_jovens,
            'adultos_sistema': historico.sistema_total_adultos,
            'total_pessoas_sistema': (historico.sistema_total_criancas + 
                                     historico.sistema_total_prejovens +
                                     historico.sistema_total_jovens + 
                                     historico.sistema_total_adultos),
            # Livros do sistema (dados salvos)
            'estudos_andamento': historico.livros_iniciados,
            'estudos_pausados': 0,  # Não temos dados históricos de pausados
            'total_estudos': historico.total_livros,
            'livros_por_categoria': livros_por_categoria,
            'livros_detalhados': livros_detalhados_organizados,
            'total_livros_iniciados': total_livros_iniciados,
            'total_livros_concluidos': total_livros_concluidos,
            'total_livros_geral': total_livros_iniciados + total_livros_concluidos,
        }
    else:
        # Históricos antigos sem estatísticas editáveis - usar apenas dados básicos
        estatisticas_editaveis_dict = None  # Não há dados editáveis
        
        # Para históricos antigos, usar os dados básicos (que eram misturados)
        # mas agora verificar se temos os novos campos do sistema
        possui_campos_sistema = hasattr(historico, 'sistema_grupos_prejovens')
        
        estatisticas_bd_dict = {
            'grupos_prejovens': historico.sistema_grupos_prejovens if possui_campos_sistema else historico.total_grupos_prejovens,
            'aulas_criancas': historico.sistema_aulas_criancas if possui_campos_sistema else historico.total_aulas_criancas,
            'circulos_estudo': historico.sistema_circulos_estudo if possui_campos_sistema else historico.total_circulos_estudo,
            'reunioes_devocionais': historico.sistema_reunioes_devocionais if possui_campos_sistema else historico.total_reunioes_devocionais,
            'participantes_prejovens': historico.sistema_participantes_prejovens if possui_campos_sistema else historico.participantes_prejovens,
            'participantes_criancas': historico.sistema_participantes_criancas if possui_campos_sistema else historico.participantes_criancas,
            'participantes_circulos': historico.sistema_participantes_circulos if possui_campos_sistema else historico.participantes_circulos,
            'participantes_devocionais': historico.sistema_participantes_devocionais if possui_campos_sistema else historico.participantes_devocionais,
            'participantes_total': historico.total_participantes,
            'total_familias': historico.total_grupos_familias,
            'total_estudos': historico.total_livros,
            'estudos_andamento': historico.livros_iniciados,
            'estudos_pausados': 0,  # Não temos dados históricos de pausados
            'livros_por_categoria': livros_por_categoria,
            'livros_detalhados': livros_detalhados_organizados,
            'total_livros_iniciados': total_livros_iniciados,
            'total_livros_concluidos': total_livros_concluidos,
            'total_livros_geral': total_livros_iniciados + total_livros_concluidos,
            # Demografia (usar campos do sistema se existirem, senão zero)
            'criancas_sistema': historico.sistema_total_criancas if possui_campos_sistema else 0,
            'prejovens_sistema': historico.sistema_total_prejovens if possui_campos_sistema else 0,
            'jovens_sistema': historico.sistema_total_jovens if possui_campos_sistema else 0,
            'adultos_sistema': historico.sistema_total_adultos if possui_campos_sistema else 0,
            'total_pessoas_sistema': (
                (historico.sistema_total_criancas + historico.sistema_total_prejovens +
                 historico.sistema_total_jovens + historico.sistema_total_adultos) 
                if possui_campos_sistema else 0
            ),
        }
    
    # Calcular atividades "novas" para este ciclo histórico
    # ATUALIZADO: Usar os novos campos específicos de atividades novas
    atividades_ciclo_historico = {
        'livros_novos': historico.novos_livros_iniciados if hasattr(historico, 'novos_livros_iniciados') else historico.livros_iniciados,
        'livros_concluidos_ciclo': historico.novos_livros_concluidos if hasattr(historico, 'novos_livros_concluidos') else historico.livros_concluidos,
        'taxa_conclusao': (historico.novos_livros_concluidos * 100 / historico.novos_livros_iniciados) if (hasattr(historico, 'novos_livros_iniciados') and historico.novos_livros_iniciados > 0) else ((historico.livros_concluidos * 100 / historico.livros_iniciados) if historico.livros_iniciados > 0 else 0),
        
        # NOVO: Usar campos específicos de atividades novas
        'grupos_prejovens_novos': historico.novas_grupos_prejovens if hasattr(historico, 'novas_grupos_prejovens') else historico.total_grupos_prejovens,
        'aulas_criancas_novas': historico.novas_aulas_criancas if hasattr(historico, 'novas_aulas_criancas') else historico.total_aulas_criancas,
        'circulos_estudo_novos': historico.novas_circulos_estudo if hasattr(historico, 'novas_circulos_estudo') else historico.total_circulos_estudo,
        'reunioes_devocionais_novas': historico.novas_reunioes_devocionais if hasattr(historico, 'novas_reunioes_devocionais') else historico.total_reunioes_devocionais,
        
        'total_atividades_novas': (
            (historico.novas_grupos_prejovens + historico.novas_aulas_criancas + 
             historico.novas_circulos_estudo + historico.novas_reunioes_devocionais)
            if hasattr(historico, 'novas_grupos_prejovens') 
            else historico.total_atividades
        ),
        
        'data_inicio_ciclo': historico.data_inicio,
        'data_fim_ciclo': historico.data_fim,
        'numero_ciclo': historico.numero_ciclo,
        # Livros por categoria organizados
        'livros_iniciados_por_categoria': {},
        'livros_concluidos_por_categoria': {},
    }
    
    # Organizar livros por categoria para o template de atividades novas
    for categoria_code in ['sequencia', 'abc', 'prejovens', 'outros']:
        categoria_nome = categoria_display_map[categoria_code]
        cor = categoria_cor_map[categoria_code]
        
        livros_categoria = livros_detalhados.filter(categoria=categoria_code)
        
        if livros_categoria:
            # Livros iniciados
            iniciados_dict = {}
            for livro in livros_categoria:
                if livro.quantidade_iniciados > 0:
                    iniciados_dict[livro.nome_livro] = livro.quantidade_iniciados
            
            if iniciados_dict:
                atividades_ciclo_historico['livros_iniciados_por_categoria'][categoria_nome] = {
                    'count': sum(iniciados_dict.values()),
                    'cor': cor,
                    'livros': iniciados_dict
                }
            
            # Livros concluídos
            concluidos_dict = {}
            for livro in livros_categoria:
                if livro.quantidade_concluidos > 0:
                    concluidos_dict[livro.nome_livro] = livro.quantidade_concluidos
            
            if concluidos_dict:
                atividades_ciclo_historico['livros_concluidos_por_categoria'][categoria_nome] = {
                    'count': sum(concluidos_dict.values()),
                    'cor': cor,
                    'livros': concluidos_dict
                }
    
    # Informações do ciclo
    ciclo_info = {
        'numero': historico.numero_ciclo,
        'inicio': historico.data_inicio,
        'fim': historico.data_fim,
        'nome': f"Ciclo {historico.numero_ciclo}",
        'dias_duracao': (historico.data_fim - historico.data_inicio).days + 1,
        'progresso': 100,  # Ciclo já finalizado
        'crescimento_atividades': historico.crescimento_atividades,
        'crescimento_participantes': historico.crescimento_participantes,
        'crescimento_livros': historico.crescimento_livros,
    }
    
    context = {
        'configuracao': configuracao,
        'estatisticas_editaveis': estatisticas_editaveis_dict,  # Dados editáveis históricos ou None
        'estatisticas_bd': estatisticas_bd_dict,  # Dados calculados do sistema histórico
        'ciclo_atual': ciclo_info,
        'historico': historico,
        'eh_historico': True,  # Flag para o template saber que é histórico
        'titulo_pagina': f"Histórico do Ciclo {numero_ciclo}",
        'atividades_novas_ciclo': atividades_ciclo_historico,
        'dados_crescimento': {
            'crescimento_total': {
                'atividades': historico.crescimento_atividades,
                'participantes': historico.crescimento_participantes,
                'livros': historico.crescimento_livros,
            }
        }
    }
    
    return render(request, 'contact/historico_ciclo_detalhado.html', context)


@login_required
def editar_estatisticas(request):
    """Editar estatísticas manuais"""
    estatisticas, created = EstatisticasEditaveis.objects.get_or_create(
        owner=request.user
    )
    
    # Obter dados dos modelos para edição inline
    circulos_estudo = CirculoEstudo.objects.filter(owner=request.user)
    grupos_prejovens = GrupoPreJovens.objects.filter(owner=request.user)
    aulas_criancas = AulaCrianca.objects.filter(owner=request.user)
    reunioes_devocionais = ReuniaoDevocional.objects.filter(owner=request.user)
    
    if request.method == 'POST':
        # Atividades Comunitárias
        estatisticas.total_grupos_prejovens = int(request.POST.get('total_grupos_prejovens', 0))
        estatisticas.participantes_prejovens = int(request.POST.get('participantes_prejovens', 0))
        estatisticas.participantes_prejovens_bahais = int(request.POST.get('participantes_prejovens_bahais', 0))
        
        estatisticas.total_aulas_criancas = int(request.POST.get('total_aulas_criancas', 0))
        estatisticas.participantes_criancas = int(request.POST.get('participantes_criancas', 0))
        estatisticas.participantes_criancas_bahais = int(request.POST.get('participantes_criancas_bahais', 0))
        
        estatisticas.total_circulos_estudo = int(request.POST.get('total_circulos_estudo', 0))
        estatisticas.participantes_circulos = int(request.POST.get('participantes_circulos', 0))
        estatisticas.participantes_circulos_bahais = int(request.POST.get('participantes_circulos_bahais', 0))
        
        estatisticas.total_reunioes_devocionais = int(request.POST.get('total_reunioes_devocionais', 0))
        estatisticas.participantes_devocionais = int(request.POST.get('participantes_devocionais', 0))
        estatisticas.participantes_devocionais_bahais = int(request.POST.get('participantes_devocionais_bahais', 0))
        
        # Detalhamento das Atividades
        # Pré-jovens
        estatisticas.animadores_prejovens = int(request.POST.get('detalhes_prejovens_animadores', 0))
        estatisticas.locais_prejovens = int(request.POST.get('detalhes_prejovens_locais', 0))
        
        # Crianças
        estatisticas.professores_criancas = int(request.POST.get('detalhes_criancas_professores', 0))
        estatisticas.series_criancas = request.POST.get('detalhes_criancas_series', '')
        
        # Círculos
        estatisticas.tutores_circulos = int(request.POST.get('detalhes_circulos_tutores', 0))
        estatisticas.livros_circulos = request.POST.get('detalhes_circulos_livros', '')
        estatisticas.circulos_concluidos = int(request.POST.get('detalhes_circulos_conclusoes', 0))
        
        # Devocionais
        estatisticas.facilitadores_devocionais = int(request.POST.get('detalhes_devocionais_facilitadores', 0))
        
        # Demografia
        estatisticas.total_criancas = int(request.POST.get('total_criancas', 0))
        estatisticas.total_prejovens = int(request.POST.get('total_prejovens', 0))
        estatisticas.total_jovens = int(request.POST.get('total_jovens', 0))
        estatisticas.total_adultos = int(request.POST.get('total_adultos', 0))
        
        estatisticas.save()
        
        # NOTA: Edição inline dos participantes não altera os modelos diretamente
        # Os campos editáveis servem para ajustar os números manualmente
        # enquanto os dados do banco mostram o que está realmente cadastrado
        
        # Salvar mensagem informativa
        inline_updates = []
        for grupo in grupos_prejovens:
            participantes = request.POST.get(f'prejovens_{grupo.id}_participantes')
            if participantes is not None:
                inline_updates.append(f"Grupo {grupo.nome}: {participantes} participantes")
        
        for aula in aulas_criancas:
            participantes = request.POST.get(f'aula_{aula.id}_participantes')
            if participantes is not None:
                inline_updates.append(f"Aula {aula.nome}: {participantes} participantes")
        
        for circulo in circulos_estudo:
            participantes = request.POST.get(f'circulo_{circulo.id}_participantes')
            if participantes is not None:
                inline_updates.append(f"Círculo {circulo.nome}: {participantes} participantes")
        
        for reuniao in reunioes_devocionais:
            participantes = request.POST.get(f'reuniao_{reuniao.id}_participantes')
            if participantes is not None:
                inline_updates.append(f"Reunião {reuniao.nome}: {participantes} participantes")
        
        if inline_updates:
            messages.info(request, f'✅ Dados inline atualizados: {", ".join(inline_updates[:3])}{"..." if len(inline_updates) > 3 else ""}')
        
        messages.success(request, '✅ Estatísticas salvas com sucesso!')
        return redirect('contact:dashboard_estatisticas')
    
    context = {
        'estatisticas': estatisticas,
        'circulos_estudo': circulos_estudo,
        'grupos_prejovens': grupos_prejovens,
        'aulas_criancas': aulas_criancas,
        'reunioes_devocionais': reunioes_devocionais,
        'estatisticas_bd': calcular_estatisticas_bd(request.user),
    }
    
    return render(request, 'contact/editar_estatisticas.html', context)


def calcular_estatisticas_bd(user):
    """Calcula estatísticas baseadas nos dados do banco"""
    
    # Filtrar por usuário
    grupos_prejovens = GrupoPreJovens.objects.filter(owner=user)
    aulas_criancas = AulaCrianca.objects.filter(owner=user)
    circulos_estudo = CirculoEstudo.objects.filter(owner=user)
    reunioes_devocionais = ReuniaoDevocional.objects.filter(owner=user)
    familias = Familia.objects.filter(owner=user)
    estudos_atuais = EstudoAtual.objects.filter(contato__owner=user)
    
    # Contar atividades
    total_grupos_prejovens = grupos_prejovens.count()
    total_aulas_criancas = aulas_criancas.count()
    total_circulos_estudo = circulos_estudo.count()
    
    # NOVO: Contar reuniões devocionais baseado nas famílias que têm reunião_devocional=True
    familias_com_reuniao = familias.filter(reuniao_devocional=True)
    total_reunioes_devocionais = familias_com_reuniao.count()
    
    # Contar participantes usando os relacionamentos Many-to-Many
    participantes_prejovens = sum(grupo.pre_jovens.count() for grupo in grupos_prejovens)
    participantes_criancas = sum(aula.participantes.count() for aula in aulas_criancas)
    participantes_circulos = sum(circulo.participantes.count() for circulo in circulos_estudo)
    
    # Contar participantes Bahá'ís usando o campo is_bahai dos contatos
    participantes_prejovens_bahais = sum(grupo.pre_jovens.filter(is_bahai=True).count() for grupo in grupos_prejovens)
    participantes_criancas_bahais = sum(aula.participantes.filter(is_bahai=True).count() for aula in aulas_criancas)
    participantes_circulos_bahais = sum(circulo.participantes.filter(is_bahai=True).count() for circulo in circulos_estudo)
    
    # Apenas para reuniões devocionais usar o campo real do modelo (quando existir)
    participantes_devocionais_bahais = sum(reuniao.participantes_bahais for reuniao in reunioes_devocionais)
    
    # NOVO: Contar participantes das reuniões devocionais baseado nos membros das famílias
    participantes_devocionais = 0
    participantes_devocionais_bahais_familias = 0
    for familia in familias_com_reuniao:
        # Contar membros da família como participantes da reunião devocional
        membros_familia = familia.membros.count()
        participantes_devocionais += membros_familia
        
        # Contar quantos dos membros da família são Bahá'ís
        membros_bahais = familia.membros.filter(is_bahai=True).count()
        participantes_devocionais_bahais_familias += membros_bahais
    
    # Usar o maior valor entre os dados das reuniões devocionais e os das famílias
    participantes_devocionais_bahais = max(participantes_devocionais_bahais, participantes_devocionais_bahais_familias)
    
    # Contar famílias e estudos
    total_familias = familias.count()
    total_estudos_andamento = estudos_atuais.filter(status='em_andamento').count()
    total_estudos_pausados = estudos_atuais.filter(status='pausado').count()
    
    # Calcular estatísticas detalhadas dos livros por categoria
    
    # Buscar todas as categorias ativas
    categorias = CategoriaLivro.objects.filter(ativo=True).order_by('ordem', 'nome')
    
    # Preparar estatísticas por categoria
    livros_por_categoria = {}
    total_livros_iniciados = 0
    total_livros_concluidos = 0
    
    # Preparar estatísticas detalhadas por livro individual
    livros_detalhados = []
    
    for categoria in categorias:
        # Estudos atuais desta categoria
        estudos_categoria_atual = estudos_atuais.filter(livro__categoria=categoria)
        iniciados_categoria = estudos_categoria_atual.count()
        
        # Estudos concluídos desta categoria
        historicos_categoria = HistoricoEstudo.objects.filter(
            contato__owner=user,
            livro__categoria=categoria,
            status='concluido'
        )
        concluidos_categoria = historicos_categoria.count()
        
        # Somar aos totais
        total_livros_iniciados += iniciados_categoria
        total_livros_concluidos += concluidos_categoria
        
        livros_por_categoria[categoria.nome] = {
            'iniciados': iniciados_categoria,
            'concluidos': concluidos_categoria,
            'total': iniciados_categoria + concluidos_categoria,
            'cor': categoria.cor,
            'ordem': categoria.ordem
        }
        
        # Buscar livros individuais desta categoria
        livros_categoria = categoria.livros.filter(ativo=True).order_by('numero')
        
        for livro in livros_categoria:
            # Contar estudos atuais deste livro
            iniciados_livro = estudos_atuais.filter(livro=livro).count()
            
            # Contar estudos concluídos deste livro
            concluidos_livro = HistoricoEstudo.objects.filter(
                contato__owner=user,
                livro=livro,
                status='concluido'
            ).count()
            
            # Só adicionar se houver algum estudo (atual ou concluído)
            if iniciados_livro > 0 or concluidos_livro > 0:
                livros_detalhados.append({
                    'nome': str(livro),
                    'categoria': categoria.nome,
                    'cor_categoria': categoria.cor,
                    'iniciados': iniciados_livro,
                    'concluidos': concluidos_livro,
                    'total': iniciados_livro + concluidos_livro,
                    'numero': livro.numero,
                    'categoria_ordem': categoria.ordem
                })
    
    # Ordenar livros detalhados por categoria e depois por número
    livros_detalhados.sort(key=lambda x: (x['categoria_ordem'], x['numero']))
    
    # Estudos totais (geral)
    total_livros_geral = total_livros_iniciados + total_livros_concluidos
    
    # Calcular dados demográficos do sistema baseado nos contatos cadastrados
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    contatos = Contact.objects.filter(owner=user)
    hoje = date.today()
    
    # Contar por faixa etária
    criancas_sistema = 0
    prejovens_sistema = 0
    jovens_sistema = 0
    adultos_sistema = 0
    
    for contato in contatos:
        if contato.birth_date:
            idade = relativedelta(hoje, contato.birth_date).years
            if idade <= 11:
                criancas_sistema += 1
            elif idade <= 14:
                prejovens_sistema += 1
            elif idade <= 30:
                jovens_sistema += 1
            else:
                adultos_sistema += 1
    
    total_pessoas_sistema = criancas_sistema + prejovens_sistema + jovens_sistema + adultos_sistema
    
    return {
        'grupos_prejovens': total_grupos_prejovens,
        'aulas_criancas': total_aulas_criancas,
        'circulos_estudo': total_circulos_estudo,
        'reunioes_devocionais': total_reunioes_devocionais,
        'participantes_prejovens': participantes_prejovens,
        'participantes_criancas': participantes_criancas,
        'participantes_circulos': participantes_circulos,
        'participantes_devocionais': participantes_devocionais,
        'participantes_prejovens_bahais': participantes_prejovens_bahais,
        'participantes_criancas_bahais': participantes_criancas_bahais,
        'participantes_circulos_bahais': participantes_circulos_bahais,
        'participantes_devocionais_bahais': participantes_devocionais_bahais,
        'participantes_total': participantes_prejovens + participantes_criancas + participantes_circulos + participantes_devocionais,
        'participantes_total_bahais': participantes_prejovens_bahais + participantes_criancas_bahais + participantes_circulos_bahais + participantes_devocionais_bahais,
        'total_familias': total_familias,
        'estudos_andamento': total_estudos_andamento,
        'estudos_pausados': total_estudos_pausados,
        'total_estudos': total_estudos_andamento + total_estudos_pausados,
        # Dados demográficos do sistema
        'criancas_sistema': criancas_sistema,
        'prejovens_sistema': prejovens_sistema,
        'jovens_sistema': jovens_sistema,
        'adultos_sistema': adultos_sistema,
        'total_pessoas_sistema': total_pessoas_sistema,
        # Estatísticas detalhadas dos livros
        'livros_por_categoria': livros_por_categoria,
        'livros_detalhados': livros_detalhados,
        'total_livros_iniciados': total_livros_iniciados,
        'total_livros_concluidos': total_livros_concluidos,
        'total_livros_geral': total_livros_geral,
    }

def calcular_atividades_novas_ciclo(user, configuracao):
    """Calcula quantas atividades e livros novos foram iniciados no ciclo atual"""
    from datetime import date
    
    # Calcular as datas do ciclo atual
    ciclo_info = configuracao.calcular_ciclo_atual()
    data_inicio_ciclo = ciclo_info['inicio']
    data_fim_ciclo = ciclo_info['fim']
    
    # Verificar se temos datas válidas
    if not data_inicio_ciclo or not data_fim_ciclo:
        return {
            'livros_novos': 0,
            'livros_concluidos_ciclo': 0,
            'livros_iniciados_por_categoria': {},
            'livros_concluidos_por_categoria': {},
            'taxa_conclusao': 0,
            'grupos_prejovens_novos': 0,
            'aulas_criancas_novas': 0,
            'circulos_estudo_novos': 0,
            'reunioes_devocionais_novas': 0,
            'total_atividades_novas': 0,
            'data_inicio_ciclo': None,
            'data_fim_ciclo': None,
            'numero_ciclo': ciclo_info['numero'],
        }
    
    # Contar livros iniciados no ciclo atual
    livros_novos = EstudoAtual.objects.filter(
        contato__owner=user,
        created_at__date__gte=data_inicio_ciclo,
        created_at__date__lte=data_fim_ciclo
    ).count()
    
    # Contar estudos concluídos no ciclo atual
    livros_concluidos_ciclo = HistoricoEstudo.objects.filter(
        contato__owner=user,
        created_at__date__gte=data_inicio_ciclo,
        created_at__date__lte=data_fim_ciclo,
        status='concluido'
    ).count()
    
    # Separar livros iniciados por categoria
    from django.db.models import Count
    from collections import defaultdict
    livros_iniciados_por_categoria = {}
    estudos_novos = EstudoAtual.objects.filter(
        contato__owner=user,
        created_at__date__gte=data_inicio_ciclo,
        created_at__date__lte=data_fim_ciclo
    ).select_related('livro__categoria')
    
    for estudo in estudos_novos:
        livro = estudo.livro
        categoria_nome = livro.categoria.nome if livro.categoria else 'Sem Categoria'
        categoria_cor = livro.categoria.cor if livro.categoria else '#6c757d'
        
        # Determinar nome do livro baseado na categoria
        if livro.categoria and livro.categoria.nome == 'Sequência':
            nome_livro = f"Livro {livro.numero}"
        elif livro.categoria and livro.categoria.nome == 'ABC':
            nome_livro = f"Aulas de Crianças - Série {livro.numero}"
        else:
            nome_livro = str(livro)
        
        if categoria_nome not in livros_iniciados_por_categoria:
            livros_iniciados_por_categoria[categoria_nome] = {
                'count': 0,
                'cor': categoria_cor,
                'livros': defaultdict(int)
            }
        
        livros_iniciados_por_categoria[categoria_nome]['count'] += 1
        livros_iniciados_por_categoria[categoria_nome]['livros'][nome_livro] += 1
    
    # Converter defaultdict para dict normal para o template
    for categoria in livros_iniciados_por_categoria:
        livros_iniciados_por_categoria[categoria]['livros'] = dict(livros_iniciados_por_categoria[categoria]['livros'])
    
    # Separar livros concluídos por categoria
    livros_concluidos_por_categoria = {}
    estudos_concluidos = HistoricoEstudo.objects.filter(
        contato__owner=user,
        created_at__date__gte=data_inicio_ciclo,
        created_at__date__lte=data_fim_ciclo,
        status='concluido'
    ).select_related('livro__categoria')
    
    for historico in estudos_concluidos:
        livro = historico.livro
        categoria_nome = livro.categoria.nome if livro.categoria else 'Sem Categoria'
        categoria_cor = livro.categoria.cor if livro.categoria else '#6c757d'
        
        # Determinar nome do livro baseado na categoria
        if livro.categoria and livro.categoria.nome == 'Sequência':
            nome_livro = f"Livro {livro.numero}"
        elif livro.categoria and livro.categoria.nome == 'ABC':
            nome_livro = f"Aulas de Crianças - Série {livro.numero}"
        else:
            nome_livro = str(livro)
        
        if categoria_nome not in livros_concluidos_por_categoria:
            livros_concluidos_por_categoria[categoria_nome] = {
                'count': 0,
                'cor': categoria_cor,
                'livros': defaultdict(int)
            }
        
        livros_concluidos_por_categoria[categoria_nome]['count'] += 1
        livros_concluidos_por_categoria[categoria_nome]['livros'][nome_livro] += 1
    
    # Converter defaultdict para dict normal para o template
    for categoria in livros_concluidos_por_categoria:
        livros_concluidos_por_categoria[categoria]['livros'] = dict(livros_concluidos_por_categoria[categoria]['livros'])
    
    # Contar atividades criadas especificamente para este ciclo
    numero_ciclo_atual = ciclo_info['numero']
    
    # Contar atividades novas baseado no campo numero_ciclo_criacao
    grupos_prejovens_novos = GrupoPreJovens.objects.filter(
        owner=user,
        numero_ciclo_criacao=numero_ciclo_atual
    ).count()
    
    aulas_criancas_novas = AulaCrianca.objects.filter(
        owner=user,
        numero_ciclo_criacao=numero_ciclo_atual
    ).count()
    
    circulos_estudo_novos = CirculoEstudo.objects.filter(
        owner=user,
        numero_ciclo_criacao=numero_ciclo_atual
    ).count()
    
    reunioes_devocionais_novas = ReuniaoDevocional.objects.filter(
        owner=user,
        numero_ciclo_criacao=numero_ciclo_atual
    ).count()
    
    # Calcular taxa de conclusão
    if livros_novos > 0:
        taxa_conclusao = (livros_concluidos_ciclo * 100) / livros_novos
    else:
        taxa_conclusao = 0
    
    return {
        'livros_novos': livros_novos,
        'livros_concluidos_ciclo': livros_concluidos_ciclo,
        'livros_iniciados_por_categoria': livros_iniciados_por_categoria,
        'livros_concluidos_por_categoria': livros_concluidos_por_categoria,
        'taxa_conclusao': taxa_conclusao,
        'grupos_prejovens_novos': grupos_prejovens_novos,
        'aulas_criancas_novas': aulas_criancas_novas,
        'circulos_estudo_novos': circulos_estudo_novos,
        'reunioes_devocionais_novas': reunioes_devocionais_novas,
        'total_atividades_novas': grupos_prejovens_novos + aulas_criancas_novas + circulos_estudo_novos + reunioes_devocionais_novas,
        'data_inicio_ciclo': data_inicio_ciclo,
        'data_fim_ciclo': data_fim_ciclo,
        'numero_ciclo': ciclo_info['numero'],
    }

@login_required
def salvar_atividades_inline(request):
    """Salvar atividades editadas inline no dashboard"""
    if request.method == 'POST':
        try:
            # Buscar ou criar estatísticas editáveis do usuário
            estatisticas, created = EstatisticasEditaveis.objects.get_or_create(
                owner=request.user
            )
            
            # Atualizar os campos com os dados do formulário
            estatisticas.total_grupos_prejovens = int(request.POST.get('total_grupos_prejovens', 0))
            estatisticas.participantes_prejovens = int(request.POST.get('participantes_prejovens', 0))
            estatisticas.participantes_prejovens_bahais = int(request.POST.get('participantes_prejovens_bahais', 0))
            
            estatisticas.total_aulas_criancas = int(request.POST.get('total_aulas_criancas', 0))
            estatisticas.participantes_criancas = int(request.POST.get('participantes_criancas', 0))
            estatisticas.participantes_criancas_bahais = int(request.POST.get('participantes_criancas_bahais', 0))
            
            estatisticas.total_circulos_estudo = int(request.POST.get('total_circulos_estudo', 0))
            estatisticas.participantes_circulos = int(request.POST.get('participantes_circulos', 0))
            estatisticas.participantes_circulos_bahais = int(request.POST.get('participantes_circulos_bahais', 0))
            
            estatisticas.total_reunioes_devocionais = int(request.POST.get('total_reunioes_devocionais', 0))
            estatisticas.participantes_devocionais = int(request.POST.get('participantes_devocionais', 0))
            estatisticas.participantes_devocionais_bahais = int(request.POST.get('participantes_devocionais_bahais', 0))
            
            # Salvar as alterações (total_participantes é calculado automaticamente pela propriedade)
            estatisticas.save()
            
            messages.success(request, '✅ Atividades atualizadas com sucesso!')
            
        except (ValueError, TypeError) as e:
            messages.error(request, f'❌ Erro ao processar os dados: {str(e)}')
    
    return redirect('contact:dashboard_estatisticas')


def calcular_dados_ciclo(user, data_inicio, data_fim, numero_ciclo=None):
    """Calcula dados de atividades, participantes e livros para um período específico ou ciclo"""
    
    if numero_ciclo:
        # Filtrar por número do ciclo de criação (método preferido)
        circulos = CirculoEstudo.objects.filter(
            owner=user,
            numero_ciclo_criacao=numero_ciclo
        )
        
        grupos_prejovens = GrupoPreJovens.objects.filter(
            owner=user,
            numero_ciclo_criacao=numero_ciclo
        )
        
        aulas_criancas = AulaCrianca.objects.filter(
            owner=user,
            numero_ciclo_criacao=numero_ciclo
        )
        
        reunioes_devocionais = ReuniaoDevocional.objects.filter(
            owner=user,
            numero_ciclo_criacao=numero_ciclo
        )
        
        # Para grupos de famílias, usar datas como fallback
        grupos_familias = GrupoFamilias.objects.filter(
            owner=user,
            data_ultima_reuniao_reflexao__range=[data_inicio, data_fim]
        )
    else:
        # Fallback: filtrar por data quando não temos numero_ciclo_criacao
        circulos = CirculoEstudo.objects.filter(owner=user)
        grupos_prejovens = GrupoPreJovens.objects.filter(owner=user)
        aulas_criancas = AulaCrianca.objects.filter(owner=user)
        reunioes_devocionais = ReuniaoDevocional.objects.filter(owner=user)
        grupos_familias = GrupoFamilias.objects.filter(owner=user)
    
    # Contar estudos de livros iniciados e concluídos no período
    estudos_iniciados = EstudoAtual.objects.filter(
        contato__owner=user,
        data_inicio__range=[data_inicio, data_fim]
    ).count()
    
    estudos_concluidos = HistoricoEstudo.objects.filter(
        contato__owner=user,
        data_conclusao__range=[data_inicio, data_fim],
        concluido=True
    ).count()
    
    total_livros = EstudoAtual.objects.filter(contato__owner=user).count()
    
    return {
        'total_circulos_estudo': circulos.count(),
        'total_grupos_prejovens': grupos_prejovens.count(),
        'total_aulas_criancas': aulas_criancas.count(),
        'total_reunioes_devocionais': reunioes_devocionais.count(),
        'total_grupos_familias': grupos_familias.count(),
        'participantes_circulos': sum(c.participantes.count() for c in circulos),
        'participantes_prejovens': sum(g.participantes.count() for g in grupos_prejovens),
        'participantes_criancas': sum(a.participantes.count() for a in aulas_criancas),
        'participantes_devocionais': sum(r.participantes.count() for r in reunioes_devocionais),
        'participantes_grupos_familias': sum(f.membros.count() for f in grupos_familias),
        'total_livros': total_livros,
        'livros_iniciados': estudos_iniciados,
        'livros_concluidos': estudos_concluidos,
    }


def registrar_historico_ciclo(configuracao, numero_ciclo, data_inicio, data_fim):
    """Registra dados históricos de um ciclo"""
    
    # Calcular dados do ciclo usando numero_ciclo_criacao quando possível
    dados = calcular_dados_ciclo(
        configuracao.owner, 
        data_inicio, 
        data_fim, 
        numero_ciclo=numero_ciclo
    )
    
    # Buscar ciclo anterior para calcular crescimento
    ciclo_anterior = HistoricoCiclo.objects.filter(
        configuracao=configuracao,
        numero_ciclo=numero_ciclo-1
    ).first()
    
    crescimento_atividades = 0.0
    crescimento_participantes = 0.0
    crescimento_livros = 0.0
    
    if ciclo_anterior:
        # Calcular crescimento percentual
        total_atividades_atual = dados['total_circulos_estudo'] + dados['total_grupos_prejovens'] + dados['total_aulas_criancas'] + dados['total_reunioes_devocionais'] + dados['total_grupos_familias']
        total_participantes_atual = dados['participantes_circulos'] + dados['participantes_prejovens'] + dados['participantes_criancas'] + dados['participantes_devocionais'] + dados['participantes_grupos_familias']
        
        if ciclo_anterior.total_atividades > 0:
            crescimento_atividades = ((total_atividades_atual - ciclo_anterior.total_atividades) / ciclo_anterior.total_atividades) * 100
            
        if ciclo_anterior.total_participantes > 0:
            crescimento_participantes = ((total_participantes_atual - ciclo_anterior.total_participantes) / ciclo_anterior.total_participantes) * 100
            
        if ciclo_anterior.total_livros > 0:
            crescimento_livros = ((dados['total_livros'] - ciclo_anterior.total_livros) / ciclo_anterior.total_livros) * 100
    
    # Criar ou atualizar histórico
    historico, created = HistoricoCiclo.objects.update_or_create(
        configuracao=configuracao,
        numero_ciclo=numero_ciclo,
        defaults={
            'owner': configuracao.owner,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'crescimento_atividades': crescimento_atividades,
            'crescimento_participantes': crescimento_participantes,
            'crescimento_livros': crescimento_livros,
            **dados
        }
    )
    
    return historico


@login_required
def encerrar_ciclo_atual(request):
    """Encerrar o ciclo atual e avançar para o próximo"""
    if request.method != 'POST':
        messages.error(request, "Método não permitido.")
        return redirect('contact:dashboard_estatisticas')
    
    configuracao = ConfiguracaoEstatisticas.objects.filter(owner=request.user, ativo=True).first()
    
    if not configuracao:
        messages.error(request, "Configure primeiro o sistema de ciclos.")
        return redirect('contact:editar_configuracao')
    
    # Calcular ciclo atual
    ciclo_atual = configuracao.calcular_ciclo_atual()
    
    if not ciclo_atual.get('numero'):
        messages.error(request, "Não há ciclo ativo para encerrar.")
        return redirect('contact:dashboard_estatisticas')
    
    # Verificar se já existe histórico para este ciclo
    historico_existente = HistoricoCiclo.objects.filter(
        configuracao=configuracao,
        numero_ciclo=ciclo_atual['numero']
    ).first()
    
    if historico_existente:
        messages.warning(request, f"O Ciclo {ciclo_atual['numero']} já foi encerrado anteriormente.")
        return redirect('contact:dashboard_estatisticas')
    
    # Coletar estatísticas atuais automaticamente
    estatisticas_editaveis = EstatisticasEditaveis.objects.filter(owner=request.user).first()
    estatisticas_bd = calcular_estatisticas_bd(request.user)
    
    # NOVO: Calcular atividades novas criadas especificamente neste ciclo
    atividades_novas_ciclo = calcular_atividades_novas_ciclo(request.user, configuracao)
    
    if not estatisticas_editaveis:
        messages.error(request, "Não há estatísticas para registrar. Configure primeiro suas atividades.")
        return redirect('contact:editar_estatisticas')
    
    # Criar histórico do ciclo salvando AMBOS os dados editáveis E os dados do sistema
    # para reproduzir fielmente o que era exibido no dashboard
    historico = HistoricoCiclo.objects.create(
        configuracao=configuracao,
        numero_ciclo=ciclo_atual['numero'],
        data_inicio=ciclo_atual['inicio'],
        data_fim=ciclo_atual['fim'],
        
        # DADOS EDITÁVEIS (seção "Completo" do dashboard)
        total_circulos_estudo=estatisticas_editaveis.total_circulos_estudo,
        total_grupos_prejovens=estatisticas_editaveis.total_grupos_prejovens,
        total_aulas_criancas=estatisticas_editaveis.total_aulas_criancas,
        total_reunioes_devocionais=estatisticas_editaveis.total_reunioes_devocionais,
        total_grupos_familias=0,  # Não há campo editável para isso
        
        participantes_circulos=estatisticas_editaveis.participantes_circulos,
        participantes_prejovens=estatisticas_editaveis.participantes_prejovens,
        participantes_criancas=estatisticas_editaveis.participantes_criancas,
        participantes_devocionais=estatisticas_editaveis.participantes_devocionais,
        participantes_grupos_familias=0,  # Não há campo editável
        
        participantes_circulos_bahais=estatisticas_editaveis.participantes_circulos_bahais,
        participantes_prejovens_bahais=estatisticas_editaveis.participantes_prejovens_bahais,
        participantes_criancas_bahais=estatisticas_editaveis.participantes_criancas_bahais,
        participantes_devocionais_bahais=estatisticas_editaveis.participantes_devocionais_bahais,
        participantes_grupos_familias_bahais=0,
        
        # DADOS DO SISTEMA (seção "Sistema" do dashboard)
        sistema_circulos_estudo=estatisticas_bd['circulos_estudo'],
        sistema_grupos_prejovens=estatisticas_bd['grupos_prejovens'],
        sistema_aulas_criancas=estatisticas_bd['aulas_criancas'],
        sistema_reunioes_devocionais=estatisticas_bd['reunioes_devocionais'],
        sistema_grupos_familias=estatisticas_bd['total_familias'],
        
        sistema_participantes_circulos=estatisticas_bd['participantes_circulos'],
        sistema_participantes_prejovens=estatisticas_bd['participantes_prejovens'],
        sistema_participantes_criancas=estatisticas_bd['participantes_criancas'],
        sistema_participantes_devocionais=estatisticas_bd['participantes_devocionais'],
        sistema_participantes_familias=0,  # Pode ser calculado se necessário
        
        sistema_participantes_circulos_bahais=estatisticas_bd['participantes_circulos_bahais'],
        sistema_participantes_prejovens_bahais=estatisticas_bd['participantes_prejovens_bahais'],
        sistema_participantes_criancas_bahais=estatisticas_bd['participantes_criancas_bahais'],
        sistema_participantes_devocionais_bahais=estatisticas_bd['participantes_devocionais_bahais'],
        sistema_participantes_familias_bahais=0,
        
        # DEMOGRAFIA DO SISTEMA
        sistema_total_criancas=estatisticas_bd['criancas_sistema'],
        sistema_total_prejovens=estatisticas_bd['prejovens_sistema'],
        sistema_total_jovens=estatisticas_bd['jovens_sistema'],
        sistema_total_adultos=estatisticas_bd['adultos_sistema'],
        
        # LIVROS (dados do sistema como estavam sendo exibidos)
        total_livros=estatisticas_bd['total_livros_geral'],
        livros_iniciados=estatisticas_bd['total_livros_iniciados'],
        livros_concluidos=estatisticas_bd['total_livros_concluidos'],
        
        # LIVROS POR CATEGORIA (dados do sistema)
        livros_sequencia_iniciados=estatisticas_bd['livros_por_categoria'].get('Sequência', {}).get('iniciados', 0),
        livros_sequencia_concluidos=estatisticas_bd['livros_por_categoria'].get('Sequência', {}).get('concluidos', 0),
        livros_abc_iniciados=estatisticas_bd['livros_por_categoria'].get('ABC', {}).get('iniciados', 0),
        livros_abc_concluidos=estatisticas_bd['livros_por_categoria'].get('ABC', {}).get('concluidos', 0),
        livros_prejovens_iniciados=estatisticas_bd['livros_por_categoria'].get('Pré-jovens', {}).get('iniciados', 0),
        livros_prejovens_concluidos=estatisticas_bd['livros_por_categoria'].get('Pré-jovens', {}).get('concluidos', 0),
        livros_outros_iniciados=sum(stats.get('iniciados', 0) for nome, stats in estatisticas_bd['livros_por_categoria'].items() if nome not in ['Sequência', 'ABC', 'Pré-jovens']),
        livros_outros_concluidos=sum(stats.get('concluidos', 0) for nome, stats in estatisticas_bd['livros_por_categoria'].items() if nome not in ['Sequência', 'ABC', 'Pré-jovens']),
        
        # NOVO: Atividades criadas especificamente neste ciclo
        novas_circulos_estudo=atividades_novas_ciclo['circulos_estudo_novos'],
        novas_grupos_prejovens=atividades_novas_ciclo['grupos_prejovens_novos'],
        novas_aulas_criancas=atividades_novas_ciclo['aulas_criancas_novas'],
        novas_reunioes_devocionais=atividades_novas_ciclo['reunioes_devocionais_novas'],
        
        # NOVO: Livros iniciados especificamente neste ciclo
        novos_livros_iniciados=atividades_novas_ciclo['livros_novos'],
        novos_livros_concluidos=atividades_novas_ciclo['livros_concluidos_ciclo'],
        
        # NOVO: Detalhamento de livros novos por categoria
        novos_livros_sequencia=atividades_novas_ciclo['livros_iniciados_por_categoria'].get('Sequência', {}).get('count', 0),
        novos_livros_abc=atividades_novas_ciclo['livros_iniciados_por_categoria'].get('ABC', {}).get('count', 0),
        novos_livros_prejovens=atividades_novas_ciclo['livros_iniciados_por_categoria'].get('Pré-jovens', {}).get('count', 0),
        novos_livros_outros=sum(cat.get('count', 0) for nome, cat in atividades_novas_ciclo['livros_iniciados_por_categoria'].items() if nome not in ['Sequência', 'ABC', 'Pré-jovens']),
        
        owner=request.user
    )
    
    # Salvar detalhes específicos de cada livro
    from ..models import DetalheLivroHistorico, EstatisticasEditaveisHistorico
    for livro in estatisticas_bd['livros_detalhados']:
        # Mapear categoria para o formato do modelo
        categoria_map = {
            'Sequência': 'sequencia',
            'ABC': 'abc',
            'Pré-jovens': 'prejovens'
        }
        categoria = categoria_map.get(livro['categoria'], 'outros')
        
        DetalheLivroHistorico.objects.create(
            historico_ciclo=historico,
            categoria=categoria,
            nome_livro=livro['nome'],
            quantidade_iniciados=livro['iniciados'],
            quantidade_concluidos=livro['concluidos']
        )
    
    # Salvar cópia completa das estatísticas editáveis
    EstatisticasEditaveisHistorico.objects.create(
        historico_ciclo=historico,
        # Atividades
        total_grupos_prejovens=estatisticas_editaveis.total_grupos_prejovens,
        participantes_prejovens=estatisticas_editaveis.participantes_prejovens,
        participantes_prejovens_bahais=estatisticas_editaveis.participantes_prejovens_bahais,
        
        total_aulas_criancas=estatisticas_editaveis.total_aulas_criancas,
        participantes_criancas=estatisticas_editaveis.participantes_criancas,
        participantes_criancas_bahais=estatisticas_editaveis.participantes_criancas_bahais,
        
        total_circulos_estudo=estatisticas_editaveis.total_circulos_estudo,
        participantes_circulos=estatisticas_editaveis.participantes_circulos,
        participantes_circulos_bahais=estatisticas_editaveis.participantes_circulos_bahais,
        
        total_reunioes_devocionais=estatisticas_editaveis.total_reunioes_devocionais,
        participantes_devocionais=estatisticas_editaveis.participantes_devocionais,
        participantes_devocionais_bahais=estatisticas_editaveis.participantes_devocionais_bahais,
        
        # Detalhamentos
        animadores_prejovens=estatisticas_editaveis.animadores_prejovens,
        locais_prejovens=estatisticas_editaveis.locais_prejovens,
        professores_criancas=estatisticas_editaveis.professores_criancas,
        series_criancas=estatisticas_editaveis.series_criancas,
        tutores_circulos=estatisticas_editaveis.tutores_circulos,
        livros_circulos=estatisticas_editaveis.livros_circulos,
        circulos_concluidos=estatisticas_editaveis.circulos_concluidos,
        facilitadores_devocionais=estatisticas_editaveis.facilitadores_devocionais,
        
        # Demografia
        total_criancas=estatisticas_editaveis.total_criancas,
        total_prejovens=estatisticas_editaveis.total_prejovens,
        total_jovens=estatisticas_editaveis.total_jovens,
        total_adultos=estatisticas_editaveis.total_adultos,
    )
    
    # Calcular crescimento
    from .historico_views import calcular_crescimento
    calcular_crescimento(historico)
    
    messages.success(request, f"🎉 Ciclo {ciclo_atual['numero']} encerrado com sucesso! Todas as informações foram salvas no histórico. Bem-vindo ao Ciclo {ciclo_atual['numero'] + 1}!")
    return redirect('contact:dashboard_estatisticas')


def obter_dados_crescimento(user):
    """Obtém dados de crescimento dos últimos ciclos"""
    configuracao = ConfiguracaoEstatisticas.objects.filter(owner=user, ativo=True).first()
    
    if not configuracao:
        return {
            'ciclos_historicos': [],
            'crescimento_total': {'atividades': 0, 'participantes': 0, 'livros': 0},
            'ciclo_atual': None
        }
    
    # Buscar históricos dos últimos 5 ciclos
    historicos = HistoricoCiclo.objects.filter(
        configuracao=configuracao
    ).order_by('-numero_ciclo')[:5]
    
    # Adicionar livros detalhados para cada histórico
    from ..models import DetalheLivroHistorico
    for historico in historicos:
        historico.livros_detalhados = DetalheLivroHistorico.objects.filter(
            historico_ciclo=historico
        ).order_by('categoria', 'nome_livro')
    
    # Calcular crescimento total
    crescimento_total = {
        'atividades': sum(h.crescimento_atividades for h in historicos) / len(historicos) if historicos else 0,
        'participantes': sum(h.crescimento_participantes for h in historicos) / len(historicos) if historicos else 0,
        'livros': sum(h.crescimento_livros for h in historicos) / len(historicos) if historicos else 0,
    }
    
    # Dados do ciclo atual
    ciclo_atual_info = configuracao.calcular_ciclo_atual()
    
    return {
        'ciclos_historicos': list(historicos),
        'crescimento_total': crescimento_total,
        'ciclo_atual': ciclo_atual_info,
        'configuracao': configuracao
    }