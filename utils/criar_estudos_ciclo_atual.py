"""
Script para criar estudos atuais no ciclo atual para demonstração
"""

import sys
import os
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from contact.models import (
    Contact, EstudoAtual, HistoricoEstudo, Livro, CategoriaLivro,
    ConfiguracaoEstatisticas
)
from django.utils import timezone
from datetime import datetime, timedelta
import random


def criar_estudos_ciclo_atual(username='alef'):
    """
    Cria estudos atuais no ciclo atual para demonstrar as novas funcionalidades
    """
    try:
        # Buscar usuário
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.first()
            
        if not user:
            print("❌ Nenhum usuário encontrado")
            return
            
        print(f"🔍 Trabalhando com usuário: {user.username}")
        
        # Buscar configuração para calcular período do ciclo atual
        configuracao = ConfiguracaoEstatisticas.objects.filter(owner=user).first()
        if not configuracao:
            print("❌ Configuração não encontrada")
            return
            
        # Calcular datas do ciclo atual
        ciclo_info = configuracao.calcular_ciclo_atual()
        data_inicio_ciclo = ciclo_info['inicio']
        data_fim_ciclo = ciclo_info['fim']
        
        print(f"📅 Ciclo atual: {ciclo_info['numero']} ({data_inicio_ciclo} até {data_fim_ciclo})")
        
        # Verificar se temos datas válidas
        if not data_inicio_ciclo or not data_fim_ciclo:
            print("❌ Datas do ciclo não são válidas")
            return
        
        # Buscar contatos e livros disponíveis
        contatos = Contact.objects.filter(owner=user)[:10]  # Pegar até 10 contatos
        livros = Livro.objects.filter(ativo=True)[:5]  # Pegar até 5 livros
        
        if not contatos.exists():
            print("❌ Nenhum contato encontrado")
            return
            
        if not livros.exists():
            print("❌ Nenhum livro encontrado")
            return
            
        print(f"👥 Contatos disponíveis: {contatos.count()}")
        print(f"📚 Livros disponíveis: {livros.count()}")
        
        estudos_criados = 0
        estudos_concluidos = 0
        
        # Criar estudos atuais no período do ciclo atual
        for i in range(8):  # Criar 8 estudos no ciclo atual
            contato = random.choice(contatos)
            livro = random.choice(livros)
            
            # Verificar se já existe estudo deste livro para este contato
            if EstudoAtual.objects.filter(contato=contato, livro=livro).exists():
                continue
                
            # Criar data dentro do período do ciclo atual
            dias_ciclo = (data_fim_ciclo - data_inicio_ciclo).days
            dias_random = random.randint(0, dias_ciclo)
            data_criacao = data_inicio_ciclo + timedelta(days=dias_random)
            
            # Criar estudo atual
            estudo = EstudoAtual.objects.create(
                contato=contato,
                livro=livro,
                status='em_andamento',
                data_inicio=data_criacao,
                observacoes=f'Estudo criado para demonstração no ciclo {ciclo_info["numero"]}'
            )
            
            # Ajustar a data de criação para o período do ciclo
            estudo.created_at = timezone.make_aware(
                datetime.combine(data_criacao, datetime.min.time())
            )
            estudo.save()
            
            estudos_criados += 1
            print(f"✅ Criado estudo: {contato.first_name} - {livro}")
        
        # Criar alguns estudos concluídos no ciclo atual
        for i in range(3):  # Criar 3 estudos concluídos
            contato = random.choice(contatos)
            livro = random.choice(livros)
            
            # Verificar se já existe histórico deste livro para este contato
            if HistoricoEstudo.objects.filter(contato=contato, livro=livro).exists():
                continue
                
            # Criar data dentro do período do ciclo atual
            dias_ciclo = (data_fim_ciclo - data_inicio_ciclo).days
            dias_random = random.randint(0, dias_ciclo)
            data_criacao = data_inicio_ciclo + timedelta(days=dias_random)
            
            # Criar histórico de estudo concluído
            historico = HistoricoEstudo.objects.create(
                contato=contato,
                livro=livro,
                status='concluido',
                data_inicio=data_criacao,
                data_termino=data_criacao + timedelta(days=random.randint(30, 90)),
                observacoes=f'Estudo concluído no ciclo {ciclo_info["numero"]}'
            )
            
            # Ajustar a data de criação para o período do ciclo
            historico.created_at = timezone.make_aware(
                datetime.combine(data_criacao, datetime.min.time())
            )
            historico.save()
            
            estudos_concluidos += 1
            print(f"✅ Criado estudo concluído: {contato.first_name} - {livro}")
        
        print(f"""
📊 RESUMO:
   • Estudos atuais criados: {estudos_criados}
   • Estudos concluídos criados: {estudos_concluidos}
   • Total de atividades no ciclo: {estudos_criados + estudos_concluidos}
   
🎯 Agora você pode acessar o dashboard para ver as atividades novas do ciclo atual!
        """)
        
    except Exception as e:
        print(f"❌ Erro ao criar estudos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    criar_estudos_ciclo_atual()