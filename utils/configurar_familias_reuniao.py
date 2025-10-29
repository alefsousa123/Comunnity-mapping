#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import Familia

# Buscar o usuário
try:
    user = User.objects.get(username='alefsousa123')
    print(f"✅ Usuário encontrado: {user.username}")
except User.DoesNotExist:
    print("❌ Usuário 'alefsousa123' não encontrado!")
    exit()

# Buscar famílias do usuário
familias = Familia.objects.filter(owner=user)
print(f"📋 Total de famílias: {familias.count()}")

if familias.count() == 0:
    print("⚠️ Nenhuma família encontrada! Criando famílias de exemplo...")
    
    # Criar famílias de exemplo
    from contact.models import Rua, Contact
    
    # Buscar ou criar uma rua
    rua = Rua.objects.filter(owner=user).first()
    if not rua:
        rua = Rua.objects.create(nome="Rua Principal", owner=user)
    
    familias_exemplo = [
        {"nome": "Família Silva", "reuniao_devocional": True},
        {"nome": "Família Santos", "reuniao_devocional": True}, 
        {"nome": "Família Oliveira", "reuniao_devocional": False},
        {"nome": "Família Costa", "reuniao_devocional": True},
        {"nome": "Família Pereira", "reuniao_devocional": False}
    ]
    
    for familia_data in familias_exemplo:
        familia = Familia.objects.create(
            nome=familia_data["nome"],
            owner=user,
            rua=rua,
            reuniao_devocional=familia_data["reuniao_devocional"]
        )
        
        # Criar alguns membros para cada família
        for i in range(3):  # 3 membros por família
            Contact.objects.create(
                first_name=f"Membro{i+1}",
                last_name=familia_data["nome"].split()[1],
                familia=familia,
                owner=user
            )
        
        status = "🕯️ COM reunião" if familia_data["reuniao_devocional"] else "❌ SEM reunião"
        print(f"✅ {familia.nome} criada - {status} - 3 membros")

else:
    # Marcar algumas famílias existentes como tendo reunião devocional
    print("\n🔄 Atualizando famílias existentes...")
    
    familias_para_marcar = familias[:3]  # Primeiras 3 famílias
    for familia in familias_para_marcar:
        familia.reuniao_devocional = True
        familia.save()
        membros = familia.membros.count()
        print(f"✅ {familia.nome} - MARCADA com reunião devocional - {membros} membros")

# Mostrar estatísticas finais
familias_com_reuniao = Familia.objects.filter(owner=user, reuniao_devocional=True)
total_participantes = sum(familia.membros.count() for familia in familias_com_reuniao)

print(f"\n📊 ESTATÍSTICAS FINAIS:")
print(f"🏠 Total de famílias: {Familia.objects.filter(owner=user).count()}")
print(f"🕯️ Famílias com reunião devocional: {familias_com_reuniao.count()}")
print(f"👥 Total de participantes em reuniões: {total_participantes}")

print(f"\n🎯 Agora o sistema contará:")
print(f"   📈 {familias_com_reuniao.count()} reuniões devocionais")
print(f"   👥 {total_participantes} participantes devocionais")