#!/usr/bin/env python
"""
Script de teste para verificar a funcionalidade de associação automática de atividades a ciclos
"""
import os
import sys
import django

# Configure Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import (
    ConfiguracaoEstatisticas, EstatisticasEditaveis, HistoricoCiclo, 
    GrupoPreJovens, AulaCrianca, CirculoEstudo, ReuniaoDevocional, Rua
)
from contact.mixins import HistoricoAutomaticoMixin
from django.utils import timezone
from datetime import date

def test_cycle_functionality():
    """Testa a funcionalidade de associação automática de ciclos"""
    print("🧪 Iniciando teste de funcionalidade de ciclos...")
    
    # 1. Buscar ou criar usuário de teste
    try:
        user = User.objects.get(username='admin')
        print(f"✅ Usuário encontrado: {user.username}")
    except User.DoesNotExist:
        print("❌ Usuário admin não encontrado. Criando usuário de teste...")
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Usuário criado: {user.username}")
    
    # 2. Configurar plano de ciclos
    print("\n📅 Configurando plano de ciclos...")
    plano, created = ConfiguracaoEstatisticas.objects.get_or_create(
        owner=user,
        principal=True,
        defaults={
            'titulo_plano': 'Plano de Teste',
            'data_inicio_plano': date(2024, 1, 1),
            'duracao_ciclo_meses': 3,
            'total_ciclos_plano': 12,
            'ativo': True
        }
    )
    if created:
        print(f"✅ Plano criado: {plano.titulo_plano}")
    else:
        print(f"✅ Plano encontrado: {plano.titulo_plano}")
    
    # 3. Verificar ciclo atual
    ciclo_info = plano.calcular_ciclo_atual()
    print(f"📊 Ciclo atual: {ciclo_info['numero']} ({ciclo_info['nome']})")
    
    # 4. Criar ou buscar uma rua para testes
    rua, created = Rua.objects.get_or_create(
        owner=user,
        nome='Rua de Teste',
        defaults={'bairro': 'Bairro de Teste'}
    )
    if created:
        print(f"✅ Rua criada: {rua.nome}")
    else:
        print(f"✅ Rua encontrada: {rua.nome}")
    
    # 5. Testar criação automática de histórico para ciclo anterior
    print("\n🔄 Testando criação automática de histórico...")
    ciclo_anterior = max(1, ciclo_info['numero'] - 1)
    
    # Criar um grupo de pré-jovens para ciclo anterior
    grupo = GrupoPreJovens.objects.create(
        nome='Grupo de Teste',
        owner=user,
        rua=rua,
        plano_ciclo=plano,
        numero_ciclo_criacao=ciclo_anterior
    )
    print(f"✅ Grupo criado: {grupo.nome} (Ciclo {ciclo_anterior})")
    
    # 6. Usar o mixin para salvar no histórico
    mixin = HistoricoAutomaticoMixin()
    resultado = mixin.salvar_no_historico_se_necessario(grupo, ciclo_anterior)
    
    if resultado:
        print(f"✅ Histórico criado/atualizado para ciclo {ciclo_anterior}")
        
        # Verificar se HistoricoCiclo foi criado
        try:
            historico_ciclo = HistoricoCiclo.objects.get(
                owner=user,
                configuracao=plano,
                numero_ciclo=ciclo_anterior
            )
            print(f"� HistoricoCiclo encontrado: {historico_ciclo.data_inicio} - {historico_ciclo.data_fim}")
            print(f"� Grupos de pré-jovens no histórico: {historico_ciclo.total_grupos_prejovens}")
        except HistoricoCiclo.DoesNotExist:
            print("❌ HistoricoCiclo não foi criado")
    else:
        print(f"ℹ️  Grupo não adicionado ao histórico (ciclo atual: {ciclo_info['numero']})")
    
    # 7. Testar com outros tipos de atividades
    print("\n🎯 Testando outros tipos de atividades...")
    
    # Aula de criança
    aula = AulaCrianca.objects.create(
        nome='Aula de Teste',
        owner=user,
        rua=rua,
        plano_ciclo=plano,
        numero_ciclo_criacao=ciclo_anterior
    )
    resultado_aula = mixin.salvar_no_historico_se_necessario(aula, ciclo_anterior)
    if resultado_aula:
        print(f"✅ Aula de criança adicionada ao histórico ciclo {ciclo_anterior}")
    
    # Reunião devocional
    reuniao = ReuniaoDevocional.objects.create(
        nome='Reunião de Teste',
        owner=user,
        rua=rua,
        plano_ciclo=plano,
        numero_ciclo_criacao=ciclo_anterior
    )
    resultado_reuniao = mixin.salvar_no_historico_se_necessario(reuniao, ciclo_anterior)
    if resultado_reuniao:
        print(f"✅ Reunião devocional adicionada ao histórico ciclo {ciclo_anterior}")
    
    # 8. Verificar estatísticas finais
    print("\n📊 Estatísticas finais do ciclo:")
    try:
        historico_final = HistoricoCiclo.objects.get(
            owner=user,
            configuracao=plano,
            numero_ciclo=ciclo_anterior
        )
        print(f"   Grupos de pré-jovens: {historico_final.total_grupos_prejovens}")
        print(f"   Aulas de crianças: {historico_final.total_aulas_criancas}")
        print(f"   Reuniões devocionais: {historico_final.total_reunioes_devocionais}")
        print(f"   Período: {historico_final.data_inicio} - {historico_final.data_fim}")
    except HistoricoCiclo.DoesNotExist:
        print("❌ Histórico do ciclo não encontrado")
    
    print("\n🎉 Teste concluído!")


if __name__ == '__main__':
    test_cycle_functionality()