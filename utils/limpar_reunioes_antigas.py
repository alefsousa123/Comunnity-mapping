#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import ReuniaoDevocional

# Buscar o usuário
try:
    user = User.objects.get(username='alefsousa123')
    print(f"✅ Usuário encontrado: {user.username}")
except User.DoesNotExist:
    print("❌ Usuário 'alefsousa123' não encontrado!")
    exit()

# Remover reuniões devocionais antigas do modelo para testar contagem baseada em famílias
reunioes_antigas = ReuniaoDevocional.objects.filter(owner=user)
print(f"🗑️ Removendo {reunioes_antigas.count()} reuniões devocionais antigas...")

reunioes_antigas.delete()
print("✅ Reuniões antigas removidas!")

print("\n🎯 Agora a contagem será baseada apenas nas famílias com reunião_devocional=True")
print("📋 Recarregue o dashboard de estatísticas para ver a mudança!")