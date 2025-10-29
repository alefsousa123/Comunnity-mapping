from django.core.management.base import BaseCommand
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from utils.dados_artificiais import criar_dados_historico_ciclos


class Command(BaseCommand):
    help = 'Cria dados artificiais de histórico de ciclos para demonstração'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nome do usuário para criar os dados (padrão: alef)',
            default='alef'
        )

    def handle(self, *args, **options):
        username = options['username']
        
        self.stdout.write(f'Criando dados artificiais para o usuário: {username}')
        
        resultado = criar_dados_historico_ciclos(username)
        
        if resultado['sucesso']:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Dados artificiais criados com sucesso!')
            )
            self.stdout.write(f'Usuário: {resultado["usuario"]}')
            self.stdout.write(f'Ciclos criados: {resultado["ciclos_criados"]}')
            
            for detalhe in resultado['detalhes']:
                self.stdout.write(self.style.SUCCESS(detalhe))
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar dados: {resultado["erro"]}')
            )