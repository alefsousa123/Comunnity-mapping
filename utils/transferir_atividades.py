#!/usr/bin/env python
"""
Script para transferir atividades do admin para alefsousa123
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import GrupoPreJovens, AulaCrianca, CirculoEstudo, ReuniaoDevocional

def transferir_atividades():
    # Obter usuários
    admin_user = User.objects.get(username='admin')
    target_user = User.objects.get(username='alefsousa123')
    
    print(f"🔄 Transferindo atividades de {admin_user.username} para {target_user.username}...")
    
    # Transferir Grupos de Pré-jovens
    grupos = GrupoPreJovens.objects.filter(owner=admin_user)
    grupos_count = grupos.count()
    grupos.update(owner=target_user)
    print(f"✅ {grupos_count} Grupos de Pré-jovens transferidos")
    
    # Transferir Aulas para Crianças
    aulas = AulaCrianca.objects.filter(owner=admin_user)
    aulas_count = aulas.count()
    aulas.update(owner=target_user)
    print(f"✅ {aulas_count} Aulas para Crianças transferidas")
    
    # Transferir Círculos de Estudo
    circulos = CirculoEstudo.objects.filter(owner=admin_user)
    circulos_count = circulos.count()
    circulos.update(owner=target_user)
    print(f"✅ {circulos_count} Círculos de Estudo transferidos")
    
    # Transferir Reuniões Devocionais
    reunioes = ReuniaoDevocional.objects.filter(owner=admin_user)
    reunioes_count = reunioes.count()
    reunioes.update(owner=target_user)
    print(f"✅ {reunioes_count} Reuniões Devocionais transferidas")
    
    print(f"\n🎉 Transferência concluída!")
    print(f"📊 Agora {target_user.username} tem todas as atividades")
    print(f"🔗 Acesse: http://127.0.0.1:8000/estatisticas/editar/")

if __name__ == '__main__':
    transferir_atividades()