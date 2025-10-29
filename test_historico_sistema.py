#!/usr/bin/env python
"""
Script para testar a funcionalidade de atualização de dados do sistema nos históricos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from contact.models import HistoricoCiclo, ConfiguracaoEstatisticas
from django.contrib.auth.models import User

def test_atualizar_dados_sistema():
    """Testa a funcionalidade de atualizar dados do sistema"""
    
    # Buscar um usuário para teste
    user = User.objects.first()
    if not user:
        print("❌ Nenhum usuário encontrado")
        return
    
    print(f"👤 Testando com usuário: {user.username}")
    
    # Buscar históricos do usuário
    historicos = HistoricoCiclo.objects.filter(owner=user)
    
    if not historicos.exists():
        print("❌ Nenhum histórico encontrado")
        return
    
    print(f"📊 Encontrados {historicos.count()} histórico(s)")
    
    # Testar atualização de dados do sistema para cada histórico
    for historico in historicos:
        print(f"\n🔄 Testando Ciclo {historico.numero_ciclo}...")
        
        # Mostrar dados antes
        print(f"   Antes - Atividades: CE={historico.sistema_circulos_estudo}, PJ={historico.sistema_grupos_prejovens}, AC={historico.sistema_aulas_criancas}, RD={historico.sistema_reunioes_devocionais}")
        
        # Atualizar dados do sistema
        try:
            historico.calcular_dados_sistema()
            print(f"   ✅ Dados atualizados com sucesso!")
            
            # Recarregar do banco
            historico.refresh_from_db()
            
            # Mostrar dados depois
            print(f"   Depois - Atividades: CE={historico.sistema_circulos_estudo}, PJ={historico.sistema_grupos_prejovens}, AC={historico.sistema_aulas_criancas}, RD={historico.sistema_reunioes_devocionais}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_atualizar_dados_sistema()