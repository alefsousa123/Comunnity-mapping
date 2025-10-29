#!/usr/bin/env python
"""
Script para fazer login automático como admin
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def verificar_usuario():
    print("🔍 Verificando usuários do sistema...")
    
    users = User.objects.all()
    print(f"📊 Total de usuários: {users.count()}")
    
    for user in users:
        print(f"👤 Usuário: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Superuser: {user.is_superuser}")
        print(f"   - Ativo: {user.is_active}")
        
        # Verificar se tem estatísticas
        from contact.models import EstatisticasEditaveis, GrupoPreJovens, AulaCrianca, CirculoEstudo, ReuniaoDevocional
        
        stats = EstatisticasEditaveis.objects.filter(owner=user)
        grupos = GrupoPreJovens.objects.filter(owner=user)
        aulas = AulaCrianca.objects.filter(owner=user)
        circulos = CirculoEstudo.objects.filter(owner=user)
        reunioes = ReuniaoDevocional.objects.filter(owner=user)
        
        print(f"   - Estatísticas: {stats.count()}")
        print(f"   - Grupos Pré-jovens: {grupos.count()}")
        print(f"   - Aulas Crianças: {aulas.count()}")
        print(f"   - Círculos Estudo: {circulos.count()}")
        print(f"   - Reuniões Devocionais: {reunioes.count()}")
        print("-" * 40)
    
    # Verificar login
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"🔑 Testando login do admin...")
        print(f"   - Username: admin")
        print(f"   - Tem senha definida: {admin_user.has_usable_password()}")
        
        # Tentar autenticar
        user = authenticate(username='admin', password='admin123')
        if user:
            print(f"   ✅ Login funcionando")
        else:
            print(f"   ❌ Login não funcionando")
    
    print(f"\n💡 Instruções:")
    print(f"1. Acesse: http://127.0.0.1:8000/user/login")
    print(f"2. Username: admin")
    print(f"3. Password: admin123")
    print(f"4. Depois acesse: http://127.0.0.1:8000/estatisticas/editar/")

if __name__ == '__main__':
    verificar_usuario()