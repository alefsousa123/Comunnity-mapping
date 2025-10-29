#!/usr/bin/env python
"""
Script para criar atividades de exemplo e demonstrar o detalhamento editável
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import (
    GrupoPreJovens, AulaCrianca, CirculoEstudo, ReuniaoDevocional,
    Rua, ConfiguracaoEstatisticas, EstatisticasEditaveis
)

def criar_dados_exemplo():
    # Criar ou obter usuário
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ Usuário criado: {user.username}")
    else:
        print(f"✅ Usuário encontrado: {user.username}")

    # Criar ruas de exemplo
    ruas_exemplo = [
        "Rua das Flores, 123",
        "Avenida Central, 456", 
        "Rua da Paz, 789",
        "Praça da Harmonia, 101",
        "Rua do Progresso, 202"
    ]
    
    ruas_criadas = []
    for nome_rua in ruas_exemplo:
        rua, created = Rua.objects.get_or_create(
            description=nome_rua,
            owner=user,
            defaults={'bairro': 'Centro'}
        )
        ruas_criadas.append(rua)
        if created:
            print(f"✅ Rua criada: {nome_rua}")

    # Criar Grupos de Pré-jovens
    grupos_data = [
        {"nome": "Grupo Pré-jovens Norte", "livro": "Caminhando Juntos"},
        {"nome": "Grupo Pré-jovens Sul", "livro": "Pensamento Espiritual"},
        {"nome": "Grupo Pré-jovens Centro", "livro": "O Poder da Palavra"},
    ]
    
    for i, data in enumerate(grupos_data):
        grupo, created = GrupoPreJovens.objects.get_or_create(
            nome=data['nome'],
            owner=user,
            defaults={
                'rua': ruas_criadas[i % len(ruas_criadas)],
                'livro': data['livro'],
                'description': f'Grupo de pré-jovens na região {data["nome"].split()[-1]}',
                'show': True
            }
        )
        if created:
            print(f"✅ Grupo de Pré-jovens criado: {data['nome']} - {data['livro']}")

    # Criar Aulas para Crianças
    aulas_data = [
        {"nome": "Aula Crianças Matutina", "serie": "Série 1"},
        {"nome": "Aula Crianças Vespertina", "serie": "Série 2"},
        {"nome": "Aula Crianças Especial", "serie": "Série 3"},
    ]
    
    for i, data in enumerate(aulas_data):
        aula, created = AulaCrianca.objects.get_or_create(
            nome=data['nome'],
            owner=user,
            defaults={
                'rua': ruas_criadas[i % len(ruas_criadas)],
                'serie': data['serie'],
                'description': f'Aula para crianças - {data["serie"]}',
                'show': True
            }
        )
        if created:
            print(f"✅ Aula para Crianças criada: {data['nome']} - {data['serie']}")

    # Criar Círculos de Estudo
    circulos_data = [
        {"nome": "Círculo Central", "livro": "Livro 1 - Reflexões sobre a Vida do Espírito"},
        {"nome": "Círculo Comunitário", "livro": "Livro 2 - Caminhando Juntos"},
        {"nome": "Círculo Avançado", "livro": "Livro 3 - Ensinando Classes para Crianças"},
    ]
    
    for i, data in enumerate(circulos_data):
        circulo, created = CirculoEstudo.objects.get_or_create(
            nome=data['nome'],
            owner=user,
            defaults={
                'rua': ruas_criadas[i % len(ruas_criadas)],
                'livro': data['livro'],
                'description': f'Círculo de estudo - {data["livro"]}',
                'show': True
            }
        )
        if created:
            print(f"✅ Círculo de Estudo criado: {data['nome']} - {data['livro']}")

    # Criar Reuniões Devocionais
    reunioes_data = [
        {"nome": "Reunião Devocional Central", "frequencia": "Semanal"},
        {"nome": "Reunião da Comunidade Norte", "frequencia": "Quinzenal"},
        {"nome": "Reunião do Bairro Sul", "frequencia": "Semanal"},
    ]
    
    for i, data in enumerate(reunioes_data):
        reuniao, created = ReuniaoDevocional.objects.get_or_create(
            nome=data['nome'],
            owner=user,
            defaults={
                'rua': ruas_criadas[i % len(ruas_criadas)],
                'frequencia': data['frequencia'],
                'dia_semana': 'Domingo',
                'numero_participantes': 10 + i * 5,  # 10, 15, 20 participantes
                'ativa': True
            }
        )
        if created:
            print(f"✅ Reunião Devocional criada: {data['nome']} - {data['frequencia']}")

    # Criar configuração de estatísticas
    config, created = ConfiguracaoEstatisticas.objects.get_or_create(
        owner=user,
        defaults={
            'titulo_plano': 'Plano de Crescimento da Comunidade',
            'data_inicio_plano': '2024-01-01',
            'duracao_ciclo_meses': 3,
            'total_ciclos_plano': 36,
            'ativo': True
        }
    )
    if created:
        print(f"✅ Configuração de estatísticas criada")

    print("\n🎉 Dados de exemplo criados com sucesso!")
    print("📊 Agora você pode ver o detalhamento das atividades na página de estatísticas!")
    print("🔗 Acesse: http://127.0.0.1:8000/estatisticas/editar/")
    
    # Resumo
    print(f"\n📈 Resumo dos dados criados:")
    print(f"👥 Grupos de Pré-jovens: {GrupoPreJovens.objects.filter(owner=user).count()}")
    print(f"🎨 Aulas para Crianças: {AulaCrianca.objects.filter(owner=user).count()}")
    print(f"📚 Círculos de Estudo: {CirculoEstudo.objects.filter(owner=user).count()}")
    print(f"🕯️ Reuniões Devocionais: {ReuniaoDevocional.objects.filter(owner=user).count()}")

if __name__ == '__main__':
    criar_dados_exemplo()