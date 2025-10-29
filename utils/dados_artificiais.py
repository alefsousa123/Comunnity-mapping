"""
Utilitários para criar dados artificiais de teste no sistema
"""

import sys
import os
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import ConfiguracaoEstatisticas, HistoricoCiclo
from django.utils import timezone
from dateutil.relativedelta import relativedelta


def criar_dados_historico_ciclos(username='alef'):
    """
    Cria dados artificiais de histórico de ciclos para demonstração
    
    Args:
        username (str): Nome do usuário para criar os dados
    
    Returns:
        dict: Resultado da operação com sucesso/erro e detalhes
    """
    
    try:
        # Buscar usuário
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.first()
            
        if not user:
            return {
                'sucesso': False,
                'erro': 'Nenhum usuário encontrado',
                'detalhes': []
            }

        # Buscar ou criar configuração
        configuracao, created = ConfiguracaoEstatisticas.objects.get_or_create(
            owner=user,
            defaults={
                'titulo_plano': 'Plano de 9 Anos',
                'data_inicio_plano': timezone.now().date() - relativedelta(months=15),
                'duracao_ciclo_meses': 3,
                'total_ciclos_plano': 36,
                'ativo': True
            }
        )

        # Dados dos 5 ciclos históricos
        ciclos_dados = [
            {
                'numero_ciclo': 1,
                'meses_atras': 15,
                'atividades': {'circulos': 2, 'prejovens': 1, 'criancas': 3, 'devocionais': 4, 'familias': 8},
                'participantes': {'circulos': 12, 'prejovens': 8, 'criancas': 25, 'devocionais': 35, 'familias': 40},
                'livros': {'total': 15, 'iniciados': 8, 'concluidos': 3}
            },
            {
                'numero_ciclo': 2,
                'meses_atras': 12,
                'atividades': {'circulos': 3, 'prejovens': 2, 'criancas': 4, 'devocionais': 5, 'familias': 10},
                'participantes': {'circulos': 18, 'prejovens': 12, 'criancas': 32, 'devocionais': 42, 'familias': 50},
                'livros': {'total': 20, 'iniciados': 12, 'concluidos': 6}
            },
            {
                'numero_ciclo': 3,
                'meses_atras': 9,
                'atividades': {'circulos': 4, 'prejovens': 2, 'criancas': 5, 'devocionais': 6, 'familias': 12},
                'participantes': {'circulos': 24, 'prejovens': 15, 'criancas': 40, 'devocionais': 50, 'familias': 60},
                'livros': {'total': 28, 'iniciados': 15, 'concluidos': 10}
            },
            {
                'numero_ciclo': 4,
                'meses_atras': 6,
                'atividades': {'circulos': 5, 'prejovens': 3, 'criancas': 6, 'devocionais': 7, 'familias': 15},
                'participantes': {'circulos': 30, 'prejovens': 20, 'criancas': 48, 'devocionais': 58, 'familias': 75},
                'livros': {'total': 35, 'iniciados': 18, 'concluidos': 14}
            },
            {
                'numero_ciclo': 5,
                'meses_atras': 3,
                'atividades': {'circulos': 6, 'prejovens': 4, 'criancas': 7, 'devocionais': 8, 'familias': 18},
                'participantes': {'circulos': 36, 'prejovens': 25, 'criancas': 56, 'devocionais': 65, 'familias': 90},
                'livros': {'total': 42, 'iniciados': 22, 'concluidos': 18}
            }
        ]

        detalhes = []
        
        for ciclo_data in ciclos_dados:
            # Calcular datas do ciclo (forçar no passado)
            data_inicio = timezone.now().date() - relativedelta(months=ciclo_data['meses_atras'])
            data_fim = data_inicio + relativedelta(months=3) - relativedelta(days=1)
            
            # Calcular crescimento em relação ao ciclo anterior
            crescimento_atividades = 0.0
            crescimento_participantes = 0.0
            crescimento_livros = 0.0
            
            if ciclo_data['numero_ciclo'] > 1:
                # Buscar ciclo anterior
                ciclo_anterior = next((c for c in ciclos_dados if c['numero_ciclo'] == ciclo_data['numero_ciclo'] - 1), None)
                if ciclo_anterior:
                    # Calcular totais
                    total_atividades_atual = sum(ciclo_data['atividades'].values())
                    total_atividades_anterior = sum(ciclo_anterior['atividades'].values())
                    
                    total_participantes_atual = sum(ciclo_data['participantes'].values())
                    total_participantes_anterior = sum(ciclo_anterior['participantes'].values())
                    
                    # Calcular crescimento percentual
                    if total_atividades_anterior > 0:
                        crescimento_atividades = ((total_atividades_atual - total_atividades_anterior) / total_atividades_anterior) * 100
                    
                    if total_participantes_anterior > 0:
                        crescimento_participantes = ((total_participantes_atual - total_participantes_anterior) / total_participantes_anterior) * 100
                    
                    if ciclo_anterior['livros']['total'] > 0:
                        crescimento_livros = ((ciclo_data['livros']['total'] - ciclo_anterior['livros']['total']) / ciclo_anterior['livros']['total']) * 100

            # Criar ou atualizar histórico
            historico, created = HistoricoCiclo.objects.update_or_create(
                configuracao=configuracao,
                numero_ciclo=ciclo_data['numero_ciclo'],
                defaults={
                    'owner': user,
                    'data_inicio': data_inicio,
                    'data_fim': data_fim,
                    'total_circulos_estudo': ciclo_data['atividades']['circulos'],
                    'total_grupos_prejovens': ciclo_data['atividades']['prejovens'],
                    'total_aulas_criancas': ciclo_data['atividades']['criancas'],
                    'total_reunioes_devocionais': ciclo_data['atividades']['devocionais'],
                    'total_grupos_familias': ciclo_data['atividades']['familias'],
                    'participantes_circulos': ciclo_data['participantes']['circulos'],
                    'participantes_prejovens': ciclo_data['participantes']['prejovens'],
                    'participantes_criancas': ciclo_data['participantes']['criancas'],
                    'participantes_devocionais': ciclo_data['participantes']['devocionais'],
                    'participantes_grupos_familias': ciclo_data['participantes']['familias'],
                    'total_livros': ciclo_data['livros']['total'],
                    'livros_iniciados': ciclo_data['livros']['iniciados'],
                    'livros_concluidos': ciclo_data['livros']['concluidos'],
                    'crescimento_atividades': crescimento_atividades,
                    'crescimento_participantes': crescimento_participantes,
                    'crescimento_livros': crescimento_livros,
                }
            )
            
            action = "Criado" if created else "Atualizado"
            detalhes.append(f'{action} histórico do Ciclo {ciclo_data["numero_ciclo"]} - {data_inicio} a {data_fim}')

        return {
            'sucesso': True,
            'usuario': user.username,
            'ciclos_criados': len(ciclos_dados),
            'detalhes': detalhes
        }
        
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e),
            'detalhes': []
        }


def limpar_dados_historico_ciclos(username='alef'):
    """
    Remove todos os dados de histórico de ciclos de um usuário
    
    Args:
        username (str): Nome do usuário para limpar os dados
    
    Returns:
        dict: Resultado da operação
    """
    
    try:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.first()
            
        if not user:
            return {
                'sucesso': False,
                'erro': 'Nenhum usuário encontrado'
            }

        # Remover históricos
        count = HistoricoCiclo.objects.filter(owner=user).count()
        HistoricoCiclo.objects.filter(owner=user).delete()
        
        return {
            'sucesso': True,
            'usuario': user.username,
            'ciclos_removidos': count
        }
        
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e)
        }


if __name__ == "__main__":
    resultado = criar_dados_historico_ciclos()
    print("📊 RESULTADO:", resultado)