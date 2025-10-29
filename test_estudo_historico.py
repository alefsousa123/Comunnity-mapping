#!/usr/bin/env python
"""
Script para testar a funcionalidade de histórico automático com estudos
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
    ConfiguracaoEstatisticas, HistoricoCiclo, Contact, Livro, EstudoAtual
)
from datetime import date

def test_estudo_historico():
    """Testa a criação de histórico automático para estudos"""
    print("🧪 Testando criação de histórico para estudos...")
    
    # 1. Buscar usuário
    try:
        user = User.objects.get(username='admin')
        print(f"✅ Usuário encontrado: {user.username}")
    except User.DoesNotExist:
        print("❌ Usuário admin não encontrado")
        return
    
    # 2. Buscar plano principal
    plano = ConfiguracaoEstatisticas.objects.filter(
        owner=user, principal=True
    ).first()
    
    if not plano:
        print("❌ Plano principal não encontrado")
        return
    
    print(f"✅ Plano encontrado: {plano.titulo_plano}")
    
    # 3. Verificar ciclo atual
    ciclo_info = plano.calcular_ciclo_atual()
    ciclo_atual = ciclo_info['numero']
    print(f"📊 Ciclo atual: {ciclo_atual}")
    
    # 4. Buscar ou criar um contato
    contato = Contact.objects.filter(owner=user).first()
    if not contato:
        # Criar um contato temporário para teste
        contato = Contact.objects.create(
            first_name='Teste',
            last_name='Histórico',
            owner=user
        )
        print(f"✅ Contato criado para teste: {contato.first_name}")
    else:
        print(f"✅ Contato encontrado: {contato.first_name}")
    
    # 5. Buscar um livro
    livro = Livro.objects.filter(ativo=True).first()
    if not livro:
        print("❌ Nenhum livro encontrado")
        return
    
    print(f"✅ Livro encontrado: {livro.titulo}")
    
    # 6. Testar criação de estudo para ciclo futuro (14)
    ciclo_teste = 14
    print(f"\n🔄 Testando criação de estudo para ciclo {ciclo_teste}...")
    
    # Remover estudos existentes para evitar conflitos
    EstudoAtual.objects.filter(contato=contato, livro=livro).delete()
    
    try:
        estudo, mensagem = contato.adicionar_estudo(
            livro=livro,
            plano=plano,
            ciclo_criacao=ciclo_teste,
            observacoes=f'Estudo de teste para ciclo {ciclo_teste}'
        )
        
        if estudo:
            print(f"✅ Estudo criado: {estudo}")
            
            # 7. Verificar se foi criado histórico
            try:
                historico = HistoricoCiclo.objects.get(
                    owner=user,
                    configuracao=plano,
                    numero_ciclo=ciclo_teste
                )
                print(f"✅ HistoricoCiclo criado para ciclo {ciclo_teste}")
                print(f"📈 Livros iniciados: {historico.livros_iniciados}")
                print(f"📅 Período: {historico.data_inicio} - {historico.data_fim}")
                
            except HistoricoCiclo.DoesNotExist:
                print(f"❌ HistoricoCiclo não foi criado para ciclo {ciclo_teste}")
                
        else:
            print(f"❌ Erro ao criar estudo: {mensagem}")
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
    
    print("\n🎉 Teste concluído!")

if __name__ == '__main__':
    test_estudo_historico()