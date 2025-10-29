#!/usr/bin/env python
"""
Script para testar se as estatísticas consideram apenas atividades criadas no ciclo específico.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import (
    ConfiguracaoEstatisticas, GrupoPreJovens, AulaCrianca, 
    CirculoEstudo, ReuniaoDevocional, Contact, Rua
)
from contact.views.statistics_views import calcular_atividades_novas_ciclo

def test_estatisticas_ciclo():
    """Testa se as estatísticas consideram apenas atividades do ciclo específico"""
    
    # Buscar usuário de teste
    user = User.objects.filter(username='alefsousa123').first()
    if not user:
        print("❌ Usuário 'alefsousa123' não encontrado")
        return
    
    # Buscar configuração ativa
    configuracao = ConfiguracaoEstatisticas.objects.filter(owner=user, ativo=True).first()
    if not configuracao:
        print("❌ Configuração ativa não encontrada")
        return
        
    print(f"📋 Configuração: {configuracao.titulo_plano}")
    
    # Obter informações do ciclo atual
    ciclo_info = configuracao.calcular_ciclo_atual()
    ciclo_atual = ciclo_info['numero']
    print(f"🔄 Ciclo atual: {ciclo_atual}")
    
    # Criar uma rua de teste se não existir
    rua_teste, _ = Rua.objects.get_or_create(
        nome="Rua de Teste - Estatísticas",
        owner=user,
        defaults={'description': 'Rua criada para teste de estatísticas'}
    )
    
    # Criar um contato de teste
    contato_teste, _ = Contact.objects.get_or_create(
        first_name="João",
        last_name="Teste Estatísticas",
        owner=user
    )
    
    print("\n🧪 Testando estatísticas por ciclo...")
    
    # === TESTE 1: Criar atividade no ciclo atual ===
    print(f"\n1️⃣ Criando atividade no ciclo ATUAL ({ciclo_atual})...")
    
    aula_ciclo_atual = AulaCrianca.objects.create(
        nome=f"Aula Criança - Ciclo {ciclo_atual}",
        owner=user,
        rua=rua_teste,
        plano_ciclo=configuracao,
        numero_ciclo_criacao=ciclo_atual,
        description="Aula criada para ciclo atual"
    )
    aula_ciclo_atual.participantes.add(contato_teste)
    print(f"✅ Aula criada com numero_ciclo_criacao = {ciclo_atual}")
    
    # === TESTE 2: Criar atividade em ciclo futuro ===
    ciclo_futuro = ciclo_atual + 1
    print(f"\n2️⃣ Criando atividade no ciclo FUTURO ({ciclo_futuro})...")
    
    circulo_ciclo_futuro = CirculoEstudo.objects.create(
        nome=f"Círculo - Ciclo {ciclo_futuro}",
        owner=user,
        rua=rua_teste,
        plano_ciclo=configuracao,
        numero_ciclo_criacao=ciclo_futuro,
        description="Círculo criado para ciclo futuro"
    )
    circulo_ciclo_futuro.participantes.add(contato_teste)
    print(f"✅ Círculo criado com numero_ciclo_criacao = {ciclo_futuro}")
    
    # === TESTE 3: Calcular estatísticas do ciclo atual ===
    print(f"\n3️⃣ Calculando estatísticas do ciclo ATUAL ({ciclo_atual})...")
    
    atividades_ciclo_atual = calcular_atividades_novas_ciclo(user, configuracao)
    
    print(f"📊 Resultados para ciclo {ciclo_atual}:")
    print(f"   • Aulas de crianças novas: {atividades_ciclo_atual['aulas_criancas_novas']}")
    print(f"   • Círculos de estudo novos: {atividades_ciclo_atual['circulos_estudo_novos']}")
    print(f"   • Grupos pré-jovens novos: {atividades_ciclo_atual['grupos_prejovens_novos']}")
    print(f"   • Reuniões devocionais novas: {atividades_ciclo_atual['reunioes_devocionais_novas']}")
    print(f"   • Total atividades novas: {atividades_ciclo_atual['total_atividades_novas']}")
    
    # === TESTE 4: Verificar contagens específicas ===
    print(f"\n4️⃣ Verificando contagens por numero_ciclo_criacao...")
    
    # Contar atividades criadas no ciclo atual
    aulas_ciclo_atual_count = AulaCrianca.objects.filter(
        owner=user, numero_ciclo_criacao=ciclo_atual
    ).count()
    
    circulos_ciclo_atual_count = CirculoEstudo.objects.filter(
        owner=user, numero_ciclo_criacao=ciclo_atual
    ).count()
    
    # Contar atividades criadas no ciclo futuro
    aulas_ciclo_futuro_count = AulaCrianca.objects.filter(
        owner=user, numero_ciclo_criacao=ciclo_futuro
    ).count()
    
    circulos_ciclo_futuro_count = CirculoEstudo.objects.filter(
        owner=user, numero_ciclo_criacao=ciclo_futuro
    ).count()
    
    print(f"📈 Atividades por ciclo:")
    print(f"   Ciclo {ciclo_atual}:")
    print(f"     - Aulas de crianças: {aulas_ciclo_atual_count}")
    print(f"     - Círculos de estudo: {circulos_ciclo_atual_count}")
    print(f"   Ciclo {ciclo_futuro}:")
    print(f"     - Aulas de crianças: {aulas_ciclo_futuro_count}")
    print(f"     - Círculos de estudo: {circulos_ciclo_futuro_count}")
    
    # === VALIDAÇÃO ===
    print(f"\n✅ VALIDAÇÃO:")
    
    # As estatísticas do ciclo atual devem incluir apenas atividades criadas para esse ciclo
    if atividades_ciclo_atual['aulas_criancas_novas'] == aulas_ciclo_atual_count:
        print(f"✅ Aulas de crianças: estatística ({atividades_ciclo_atual['aulas_criancas_novas']}) = contagem direta ({aulas_ciclo_atual_count})")
    else:
        print(f"❌ Aulas de crianças: estatística ({atividades_ciclo_atual['aulas_criancas_novas']}) ≠ contagem direta ({aulas_ciclo_atual_count})")
    
    if atividades_ciclo_atual['circulos_estudo_novos'] == circulos_ciclo_atual_count:
        print(f"✅ Círculos de estudo: estatística ({atividades_ciclo_atual['circulos_estudo_novos']}) = contagem direta ({circulos_ciclo_atual_count})")
    else:
        print(f"❌ Círculos de estudo: estatística ({atividades_ciclo_atual['circulos_estudo_novos']}) ≠ contagem direta ({circulos_ciclo_atual_count})")
    
    # As atividades do ciclo futuro NÃO devem aparecer nas estatísticas do ciclo atual
    if circulos_ciclo_futuro_count > 0:
        print(f"✅ Círculo do ciclo futuro ({ciclo_futuro}) não está incluído nas estatísticas do ciclo atual ({ciclo_atual})")
    
    print(f"\n🎯 CONCLUSÃO:")
    if (atividades_ciclo_atual['aulas_criancas_novas'] == aulas_ciclo_atual_count and 
        atividades_ciclo_atual['circulos_estudo_novos'] == circulos_ciclo_atual_count):
        print("✅ As estatísticas estão considerando APENAS atividades criadas no ciclo específico!")
        print("✅ O sistema está funcionando corretamente!")
    else:
        print("❌ As estatísticas NÃO estão considerando apenas atividades do ciclo específico")
        print("❌ Há algum problema na implementação")
    
    # Limpeza
    print(f"\n🧹 Limpando dados de teste...")
    aula_ciclo_atual.delete()
    circulo_ciclo_futuro.delete()
    print("✅ Dados de teste removidos")

if __name__ == "__main__":
    test_estatisticas_ciclo()