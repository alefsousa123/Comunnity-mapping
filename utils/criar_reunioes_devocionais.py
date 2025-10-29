#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import ReuniaoDevocional, Rua
from datetime import datetime, time

# Buscar o usuário
try:
    user = User.objects.get(username='alefsousa123')
    print(f"✅ Usuário encontrado: {user.username}")
except User.DoesNotExist:
    print("❌ Usuário 'alefsousa123' não encontrado!")
    exit()

# Buscar uma rua do usuário (ou criar uma padrão)
rua = Rua.objects.filter(owner=user).first()
if not rua:
    rua = Rua.objects.create(
        nome="Rua Principal",
        owner=user
    )
    print(f"✅ Rua criada: {rua.nome}")

# Criar reuniões devocionais de exemplo
reunioes_exemplo = [
    {
        'nome': 'Reunião Devocional - Domingo',
        'descricao': 'Reunião devocional dominical com orações e reflexões',
        'numero_participantes': 12,
        'participantes_bahais': 4,
        'dia_semana': 'Domingo',
        'horario': time(18, 0),  # 18:00
        'frequencia': 'Semanal',
        'local_detalhes': 'Casa da família Silva'
    },
    {
        'nome': 'Reunião Devocional - Quinta',
        'descricao': 'Reunião devocional de quinta-feira',
        'numero_participantes': 8,
        'participantes_bahais': 3,
        'dia_semana': 'Quinta-feira',
        'horario': time(19, 30),  # 19:30
        'frequencia': 'Semanal',
        'local_detalhes': 'Centro comunitário'
    },
    {
        'nome': 'Reunião Devocional - Mensal',
        'descricao': 'Grande reunião devocional mensal',
        'numero_participantes': 25,
        'participantes_bahais': 8,
        'dia_semana': 'Sábado',
        'horario': time(16, 0),  # 16:00
        'frequencia': 'Mensal',
        'local_detalhes': 'Praça central'
    }
]

# Deletar reuniões existentes do usuário para evitar duplicatas
ReuniaoDevocional.objects.filter(owner=user).delete()
print("🗑️  Reuniões antigas removidas")

# Criar as novas reuniões
reunioes_criadas = 0
for reuniao_data in reunioes_exemplo:
    reuniao = ReuniaoDevocional.objects.create(
        owner=user,
        rua=rua,
        **reuniao_data
    )
    reunioes_criadas += 1
    print(f"✅ Reunião criada: {reuniao.nome} - {reuniao.numero_participantes} participantes")

print(f"\n🎉 {reunioes_criadas} reuniões devocionais criadas com sucesso!")
print(f"👥 Total de participantes: {sum(r['numero_participantes'] for r in reunioes_exemplo)}")
print(f"🕯️ Total de Bahá'ís participantes: {sum(r['participantes_bahais'] for r in reunioes_exemplo)}")