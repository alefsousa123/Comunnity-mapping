from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..models import ConfiguracaoEstatisticas, HistoricoCiclo, DetalheLivroHistorico
from datetime import date, timedelta


@login_required
def gerenciar_historico(request):
    """Página principal para gerenciar dados históricos de ciclos"""
    configuracao = ConfiguracaoEstatisticas.objects.filter(owner=request.user).first()
    
    if not configuracao:
        messages.error(request, "Configure primeiro o sistema de ciclos nas Configurações.")
        return redirect('contact:editar_configuracao')
    
    # Buscar todos os históricos existentes com seus livros detalhados
    historicos = HistoricoCiclo.objects.filter(owner=request.user).order_by('-numero_ciclo')
    
    # Adicionar livros específicos para cada histórico
    for historico in historicos:
        historico.livros_detalhados = DetalheLivroHistorico.objects.filter(
            historico_ciclo=historico
        ).order_by('categoria', 'nome_livro')
    
    # Calcular ciclo atual
    ciclo_atual = configuracao.calcular_ciclo_atual()
    
    # Sugerir ciclos que podem ser criados (últimos 5 ciclos antes do atual)
    ciclos_sugeridos = []
    for i in range(1, 6):  # Últimos 5 ciclos
        numero_ciclo = ciclo_atual['numero'] - i
        if numero_ciclo > 0 and not historicos.filter(numero_ciclo=numero_ciclo).exists():
            # Calcular datas do ciclo sugerido usando duração em meses
            from dateutil.relativedelta import relativedelta
            meses_para_tras = i * configuracao.duracao_ciclo_meses
            inicio_sugerido = configuracao.data_inicio_plano + relativedelta(months=(numero_ciclo - 1) * configuracao.duracao_ciclo_meses)
            fim_sugerido = inicio_sugerido + relativedelta(months=configuracao.duracao_ciclo_meses) - timedelta(days=1)
            
            ciclos_sugeridos.append({
                'numero': numero_ciclo,
                'inicio': inicio_sugerido,
                'fim': fim_sugerido
            })
    
    context = {
        'configuracao': configuracao,
        'historicos': historicos,
        'ciclo_atual': ciclo_atual,
        'ciclos_sugeridos': ciclos_sugeridos
    }
    
    return render(request, 'contact/gerenciar_historico.html', context)


@login_required
def criar_historico(request, numero_ciclo):
    """Criar ou editar dados históricos de um ciclo específico"""
    configuracao = ConfiguracaoEstatisticas.objects.filter(owner=request.user).first()
    
    if not configuracao:
        messages.error(request, "Configure primeiro o sistema de ciclos.")
        return redirect('contact:editar_configuracao')
    
    # Calcular as datas do ciclo
    ciclo_atual = configuracao.calcular_ciclo_atual()
    diferenca_ciclos = ciclo_atual['numero'] - numero_ciclo
    
    if diferenca_ciclos <= 0:
        messages.error(request, "Não é possível criar dados para o ciclo atual ou futuro.")
        return redirect('contact:gerenciar_historico')
    
    # Calcular datas do ciclo específico usando duração em meses
    from dateutil.relativedelta import relativedelta
    inicio_ciclo = configuracao.data_inicio_plano + relativedelta(months=(numero_ciclo - 1) * configuracao.duracao_ciclo_meses)
    fim_ciclo = inicio_ciclo + relativedelta(months=configuracao.duracao_ciclo_meses) - timedelta(days=1)
    
    # Buscar ou criar histórico
    historico, created = HistoricoCiclo.objects.get_or_create(
        owner=request.user,
        configuracao=configuracao,
        numero_ciclo=numero_ciclo,
        defaults={
            'data_inicio': inicio_ciclo,
            'data_fim': fim_ciclo,
        }
    )
    
    if request.method == 'POST':
        # Processar formulário
        try:
            # Atividades
            historico.total_circulos_estudo = int(request.POST.get('total_circulos_estudo', 0))
            historico.total_grupos_prejovens = int(request.POST.get('total_grupos_prejovens', 0))
            historico.total_aulas_criancas = int(request.POST.get('total_aulas_criancas', 0))
            historico.total_reunioes_devocionais = int(request.POST.get('total_reunioes_devocionais', 0))
            historico.total_grupos_familias = int(request.POST.get('total_grupos_familias', 0))
            
            # Participantes
            historico.participantes_circulos = int(request.POST.get('participantes_circulos', 0))
            historico.participantes_prejovens = int(request.POST.get('participantes_prejovens', 0))
            historico.participantes_criancas = int(request.POST.get('participantes_criancas', 0))
            historico.participantes_devocionais = int(request.POST.get('participantes_devocionais', 0))
            historico.participantes_grupos_familias = int(request.POST.get('participantes_grupos_familias', 0))
            
            # Participantes Bahá'ís
            historico.participantes_circulos_bahais = int(request.POST.get('participantes_circulos_bahais', 0))
            historico.participantes_prejovens_bahais = int(request.POST.get('participantes_prejovens_bahais', 0))
            historico.participantes_criancas_bahais = int(request.POST.get('participantes_criancas_bahais', 0))
            historico.participantes_devocionais_bahais = int(request.POST.get('participantes_devocionais_bahais', 0))
            historico.participantes_grupos_familias_bahais = int(request.POST.get('participantes_grupos_familias_bahais', 0))
            
            # Livros
            historico.total_livros = int(request.POST.get('total_livros', 0))
            historico.livros_iniciados = int(request.POST.get('livros_iniciados', 0))
            historico.livros_concluidos = int(request.POST.get('livros_concluidos', 0))
            
            # Livros por categoria - Sequência
            historico.livros_sequencia_iniciados = int(request.POST.get('livros_sequencia_iniciados', 0))
            historico.livros_sequencia_concluidos = int(request.POST.get('livros_sequencia_concluidos', 0))
            
            # Livros por categoria - ABC
            historico.livros_abc_iniciados = int(request.POST.get('livros_abc_iniciados', 0))
            historico.livros_abc_concluidos = int(request.POST.get('livros_abc_concluidos', 0))
            
            # Livros por categoria - Pré-jovens
            historico.livros_prejovens_iniciados = int(request.POST.get('livros_prejovens_iniciados', 0))
            historico.livros_prejovens_concluidos = int(request.POST.get('livros_prejovens_concluidos', 0))
            
            # Livros por categoria - Outros
            historico.livros_outros_iniciados = int(request.POST.get('livros_outros_iniciados', 0))
            historico.livros_outros_concluidos = int(request.POST.get('livros_outros_concluidos', 0))
            
            # Calcular crescimento em relação ao ciclo anterior
            calcular_crescimento(historico)
            
            historico.save()
            
            # Limpar livros existentes se estiver editando
            if not created:
                DetalheLivroHistorico.objects.filter(historico_ciclo=historico).delete()
            
            # Processar livros específicos por categoria
            for categoria_choice, categoria_nome in DetalheLivroHistorico.CATEGORIA_CHOICES:
                # Buscar TODOS os campos desta categoria, não apenas sequenciais
                for key in request.POST.keys():
                    if key.startswith(f'livro_{categoria_choice}_') and key.endswith('_nome'):
                        # Extrair número do contador do nome do campo
                        contador = key.replace(f'livro_{categoria_choice}_', '').replace('_nome', '')
                        
                        nome_livro = request.POST.get(key, '').strip()
                        iniciados = request.POST.get(f'livro_{categoria_choice}_{contador}_iniciados', 0)
                        concluidos = request.POST.get(f'livro_{categoria_choice}_{contador}_concluidos', 0)
                        observacoes = request.POST.get(f'livro_{categoria_choice}_{contador}_observacoes', '')
                        
                        if nome_livro:
                            DetalheLivroHistorico.objects.create(
                                historico_ciclo=historico,
                                categoria=categoria_choice,
                                nome_livro=nome_livro,
                                quantidade_iniciados=int(iniciados or 0),
                                quantidade_concluidos=int(concluidos or 0),
                                observacoes=observacoes.strip()
                            )
            
            action = "criado" if created else "atualizado"
            messages.success(request, f"Histórico do Ciclo {numero_ciclo} {action} com sucesso!")
            return redirect('contact:gerenciar_historico')
            
        except ValueError as e:
            messages.error(request, f"Erro nos dados fornecidos: {e}")
    
    # Buscar livros existentes se estiver editando
    livros_existentes = {}
    if not created:
        for livro in DetalheLivroHistorico.objects.filter(historico_ciclo=historico):
            # Mapear categoria do banco para nome do template
            categoria_map = {
                'sequencia': 'Sequência',
                'abc': 'ABC', 
                'prejovens': 'Pré-jovens',
                'outros': 'Outros'
            }
            categoria_template = categoria_map.get(livro.categoria, livro.categoria.title())
            
            if categoria_template not in livros_existentes:
                livros_existentes[categoria_template] = []
            livros_existentes[categoria_template].append({
                'nome': livro.nome_livro,
                'iniciados': livro.quantidade_iniciados,
                'concluidos': livro.quantidade_concluidos,
                'observacoes': livro.observacoes
            })

    context = {
        'historico': historico,
        'numero_ciclo': numero_ciclo,
        'inicio_ciclo': inicio_ciclo,
        'fim_ciclo': fim_ciclo,
        'created': created,
        'livros_existentes': livros_existentes
    }
    
    return render(request, 'contact/criar_historico.html', context)


@login_required
def excluir_historico(request, historico_id):
    """Excluir um histórico de ciclo"""
    historico = get_object_or_404(HistoricoCiclo, id=historico_id, owner=request.user)
    
    if request.method == 'POST':
        numero_ciclo = historico.numero_ciclo
        historico.delete()
        messages.success(request, f"Histórico do Ciclo {numero_ciclo} excluído com sucesso!")
        return redirect('contact:gerenciar_historico')
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def detalhes_historico(request, historico_id):
    """Retornar detalhes do histórico em formato JSON"""
    try:
        historico = get_object_or_404(HistoricoCiclo, id=historico_id, owner=request.user)
        
        # Buscar livros específicos
        livros_detalhes = DetalheLivroHistorico.objects.filter(historico_ciclo=historico).values(
            'categoria', 'nome_livro', 'quantidade_iniciados', 'quantidade_concluidos', 'observacoes'
        )
        
        data = {
            'historico': {
                'numero_ciclo': historico.numero_ciclo,
                'total_atividades': historico.total_atividades,
                'total_participantes': historico.total_participantes,
                'total_participantes_bahais': historico.total_participantes_bahais,
                
                # Atividades
                'total_circulos_estudo': historico.total_circulos_estudo,
                'total_grupos_prejovens': historico.total_grupos_prejovens,
                'total_aulas_criancas': historico.total_aulas_criancas,
                'total_reunioes_devocionais': historico.total_reunioes_devocionais,
                'total_grupos_familias': historico.total_grupos_familias,
                
                # Participantes
                'participantes_circulos': historico.participantes_circulos,
                'participantes_prejovens': historico.participantes_prejovens,
                'participantes_criancas': historico.participantes_criancas,
                'participantes_devocionais': historico.participantes_devocionais,
                'participantes_grupos_familias': historico.participantes_grupos_familias,
                
                # Participantes Bahá'ís
                'participantes_circulos_bahais': historico.participantes_circulos_bahais,
                'participantes_prejovens_bahais': historico.participantes_prejovens_bahais,
                'participantes_criancas_bahais': historico.participantes_criancas_bahais,
                'participantes_devocionais_bahais': historico.participantes_devocionais_bahais,
                'participantes_grupos_familias_bahais': historico.participantes_grupos_familias_bahais,
                
                # Livros
                'livros_iniciados': historico.livros_iniciados,
                'livros_concluidos': historico.livros_concluidos,
                'livros_sequencia_iniciados': historico.livros_sequencia_iniciados,
                'livros_sequencia_concluidos': historico.livros_sequencia_concluidos,
                'livros_abc_iniciados': historico.livros_abc_iniciados,
                'livros_abc_concluidos': historico.livros_abc_concluidos,
                'livros_prejovens_iniciados': historico.livros_prejovens_iniciados,
                'livros_prejovens_concluidos': historico.livros_prejovens_concluidos,
                'livros_outros_iniciados': historico.livros_outros_iniciados,
                'livros_outros_concluidos': historico.livros_outros_concluidos,
            },
            'livros_detalhes': list(livros_detalhes)
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        print(f"Erro em detalhes_historico: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def atualizar_dados_sistema_historico(request, historico_id):
    """Atualizar dados do sistema de um histórico específico"""
    historico = get_object_or_404(HistoricoCiclo, id=historico_id, owner=request.user)
    
    try:
        historico.calcular_dados_sistema()
        messages.success(request, f"Dados do sistema atualizados para o Ciclo {historico.numero_ciclo}!")
    except Exception as e:
        messages.error(request, f"Erro ao atualizar dados do sistema: {e}")
    
    return redirect('contact:gerenciar_historico')


@login_required
def atualizar_todos_dados_sistema(request):
    """Atualizar dados do sistema de todos os históricos do usuário"""
    if request.method == 'POST':
        try:
            historicos = HistoricoCiclo.objects.filter(owner=request.user)
            count = 0
            
            for historico in historicos:
                historico.calcular_dados_sistema()
                count += 1
            
            messages.success(request, f"Dados do sistema atualizados para {count} histórico(s)!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar dados do sistema: {e}")
    
    return redirect('contact:gerenciar_historico')


def calcular_crescimento(historico):
    """Calcular crescimento em relação ao ciclo anterior"""
    try:
        ciclo_anterior = HistoricoCiclo.objects.filter(
            owner=historico.owner,
            numero_ciclo=historico.numero_ciclo - 1
        ).first()
        
        if ciclo_anterior:
            # Calcular totais do ciclo atual
            total_atividades_atual = (historico.total_circulos_estudo + 
                                    historico.total_grupos_prejovens + 
                                    historico.total_aulas_criancas + 
                                    historico.total_reunioes_devocionais + 
                                    historico.total_grupos_familias)
            
            total_participantes_atual = (historico.participantes_circulos + 
                                       historico.participantes_prejovens + 
                                       historico.participantes_criancas + 
                                       historico.participantes_devocionais + 
                                       historico.participantes_grupos_familias)
            
            # Calcular totais do ciclo anterior
            total_atividades_anterior = (ciclo_anterior.total_circulos_estudo + 
                                       ciclo_anterior.total_grupos_prejovens + 
                                       ciclo_anterior.total_aulas_criancas + 
                                       ciclo_anterior.total_reunioes_devocionais + 
                                       ciclo_anterior.total_grupos_familias)
            
            total_participantes_anterior = (ciclo_anterior.participantes_circulos + 
                                          ciclo_anterior.participantes_prejovens + 
                                          ciclo_anterior.participantes_criancas + 
                                          ciclo_anterior.participantes_devocionais + 
                                          ciclo_anterior.participantes_grupos_familias)
            
            # Calcular percentuais de crescimento
            if total_atividades_anterior > 0:
                historico.crescimento_atividades = ((total_atividades_atual - total_atividades_anterior) / total_atividades_anterior) * 100
            else:
                historico.crescimento_atividades = 100.0 if total_atividades_atual > 0 else 0.0
            
            if total_participantes_anterior > 0:
                historico.crescimento_participantes = ((total_participantes_atual - total_participantes_anterior) / total_participantes_anterior) * 100
            else:
                historico.crescimento_participantes = 100.0 if total_participantes_atual > 0 else 0.0
            
            if ciclo_anterior.total_livros > 0:
                historico.crescimento_livros = ((historico.total_livros - ciclo_anterior.total_livros) / ciclo_anterior.total_livros) * 100
            else:
                historico.crescimento_livros = 100.0 if historico.total_livros > 0 else 0.0
        
        else:
            # Primeiro ciclo, sem crescimento a calcular
            historico.crescimento_atividades = 0.0
            historico.crescimento_participantes = 0.0
            historico.crescimento_livros = 0.0
    
    except Exception:
        # Em caso de erro, zerar os crescimentos
        historico.crescimento_atividades = 0.0
        historico.crescimento_participantes = 0.0
        historico.crescimento_livros = 0.0