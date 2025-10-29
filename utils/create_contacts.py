import os
import sys
from datetime import datetime, date
from pathlib import Path
from random import choice, randint

import django
from django.conf import settings

DJANGO_BASE_DIR = Path(__file__).parent.parent
NUMBER_OF_CONTACTS = 50  # Reduzido para facilitar testes
NUMBER_OF_FAMILIAS = 15  # Reduzido para facilitar testes
NUMBER_OF_RUAS = 8       # Reduzido para facilitar testes

sys.path.append(str(DJANGO_BASE_DIR))
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
settings.USE_TZ = False

django.setup()

if __name__ == '__main__':
    import faker

    from contact.models import Contact, Familia, Rua, GrupoFamilias, GrupoPreJovens, AulaCrianca, CirculoEstudo, Livro
    from django.contrib.auth import get_user_model

    User = get_user_model()
    
    # Tenta pegar o primeiro usuário disponível ou cria um usuário de teste
    try:
        owner = User.objects.first()
        if not owner:
            print("Criando usuário de teste...")
            owner = User.objects.create_user(
                username='teste_user',
                first_name='Usuário',
                last_name='Teste',
                email='teste@email.com',
                password='senha123'
            )
            print(f"Usuário criado: {owner.username}")
    except Exception as e:
        print(f"Erro ao obter usuário: {e}")
        sys.exit(1)

    print(f"Usando usuário: {owner.username}")

    # Limpar dados existentes
    print("Limpando dados existentes...")
    Contact.objects.filter(owner=owner).delete()
    Familia.objects.filter(owner=owner).delete()
    Rua.objects.filter(owner=owner).delete()
    GrupoFamilias.objects.filter(owner=owner).delete()
    GrupoPreJovens.objects.filter(owner=owner).delete()
    AulaCrianca.objects.filter(owner=owner).delete()
    CirculoEstudo.objects.filter(owner=owner).delete()
    # Limpar estudos existentes (agora direto nos contatos)
    Contact.objects.filter(owner=owner).update(
        livro_estudando=None,
        status_estudo='nao_iniciado',
        data_inicio_estudo=None,
        data_termino_estudo=None,
        observacoes_estudo=''
    )

    fake = faker.Faker('pt_BR')

    # Criar ruas com nomes mais realistas
    print("Criando ruas...")
    nomes_ruas = [
        "Rua das Flores", "Av. Principal", "Rua do Comércio", "Rua da Igreja",
        "Av. Central", "Rua Nova", "Rua da Escola", "Rua do Mercado"
    ]
    bairros = [
        "Centro", "Vila Nova", "Jardim das Flores", "Bairro Alto",
        "Cidade Nova", "Vila Esperança", "Jardim América", "Setor Central"
    ]
    
    django_ruas = []
    for i in range(NUMBER_OF_RUAS):
        rua = Rua(
            nome=nomes_ruas[i] if i < len(nomes_ruas) else fake.street_name(),
            bairro=choice(bairros),
            description=f"Descrição da {nomes_ruas[i] if i < len(nomes_ruas) else 'rua'}",
            owner=owner,
            show=True
        )
        django_ruas.append(rua)
    
    Rua.objects.bulk_create(django_ruas)
    ruas = list(Rua.objects.filter(owner=owner))
    print(f"Criadas {len(ruas)} ruas")

    # Criar famílias com nomes mais realistas
    print("Criando famílias...")
    sobrenomes = [
        "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Ferreira",
        "Rodrigues", "Almeida", "Nascimento", "Araújo", "Ribeiro", "Carvalho", "Gomes"
    ]
    
    django_familias = []
    for i in range(NUMBER_OF_FAMILIAS):
        familia = Familia(
            nome=f"Família {choice(sobrenomes)}",
            rua=choice(ruas),
            endereco=f"{fake.street_address()}, {randint(1, 999)}",
            reuniao_devocional=choice([True, False, False]),  # Mais famílias sem reunião
            data_ultima_reuniao=fake.date_between(start_date='-6m', end_date='today') if choice([True, False]) else None,
            nivel_envolvimento=choice(['Baixo', 'Médio', 'Alto']),
            description=choice([
                "Família muito receptiva e interessada",
                "Participam regularmente das atividades",
                "Família nova na comunidade",
                "Necessita de mais acompanhamento",
                ""
            ]),
            owner=owner,
            show=True
        )
        django_familias.append(familia)
    
    Familia.objects.bulk_create(django_familias)
    familias = list(Familia.objects.filter(owner=owner))
    print(f"Criadas {len(familias)} famílias")

    # Criar contatos com idades variadas e distribuídos pelas famílias
    print("Criando contatos...")
    nomes_masculinos = ["João", "Pedro", "Carlos", "José", "Paulo", "Lucas", "Marco", "André", "Rafael", "Daniel"]
    nomes_femininos = ["Maria", "Ana", "Carla", "Fernanda", "Juliana", "Patricia", "Sandra", "Claudia", "Beatriz", "Camila"]
    
    django_contacts = []
    contatos_sem_familia = []  # Para testar seleção de contatos sem família
    
    for i in range(NUMBER_OF_CONTACTS):
        # Definir se é masculino ou feminino
        is_male = choice([True, False])
        first_name = choice(nomes_masculinos if is_male else nomes_femininos)
        last_name = choice(sobrenomes)
        
        # Definir idade com distribuição realista
        idade_grupo = choice(['crianca', 'pre_jovem', 'jovem', 'adulto'])
        if idade_grupo == 'crianca':
            age = randint(3, 11)
        elif idade_grupo == 'pre_jovem':
            age = randint(12, 14)
        elif idade_grupo == 'jovem':
            age = randint(15, 30)
        else:
            age = randint(31, 70)
        
        birth_date = date(date.today().year - age, randint(1, 12), randint(1, 28))
        
        # Decidir se vai ter família ou não (alguns sem família para testar)
        if i < 5:  # Primeiros 5 contatos sem família
            familia = None
            rua = choice(ruas)
            contatos_sem_familia.append(i)
        else:
            familia = choice(familias)
            rua = familia.rua
        
        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            description=choice([
                f"Pessoa muito ativa na comunidade",
                f"Demonstra interesse nas atividades",
                f"Membro da família {familia.nome if familia else 'sem família'}",
                "",
                f"Participante regular"
            ]),
            familia=familia,
            rua=rua,
            owner=owner,
            show=True,
        )
        django_contacts.append(contact)

    Contact.objects.bulk_create(django_contacts)
    contatos = list(Contact.objects.filter(owner=owner))
    print(f"Criados {len(contatos)} contatos")
    print(f"Contatos sem família: {len(contatos_sem_familia)}")

    # Estatísticas por idade
    criancas = [c for c in contatos if c.age_group == "Criança"]
    pre_jovens = [c for c in contatos if c.age_group == "Pré jovem"]
    jovens = [c for c in contatos if c.age_group == "Jovem"]
    adultos = [c for c in contatos if c.age_group == "Adulto"]
    
    print(f"\nEstatísticas por idade:")
    print(f"Crianças: {len(criancas)}")
    print(f"Pré-jovens: {len(pre_jovens)}")
    print(f"Jovens: {len(jovens)}")
    print(f"Adultos: {len(adultos)}")

    # Criar livros do Instituto Ruhi
    print("\nCriando livros do Instituto Ruhi...")
    livros_info = [
        (1, "Reflexões sobre a Vida do Espírito"),
        (2, "Surgindo para Servir"),
        (3, "Caminhando numa Senda de Serviço"),
        (4, "Os Gêmeos da Luz"),
        (5, "Liberando Poderes"),
        (6, "Ensinando Crianças - Grau 1"),
        (7, "Caminhando com Deus"),
        (8, "O Convênio de Bahá'u'lláh"),
        (9, "Ganhando uma Perspectiva Histórica"),
        (10, "Construindo Comunidades Vibrantes"),
        (11, "Materiais para Ações Devocionais"),
        (12, "A Realidade da Natureza Humana"),
        (13, "Promovendo o Bem-estar dos Jovens"),
        (14, "Servindo como Tutor"),
    ]
    
    livros_criados = []
    for numero, titulo in livros_info:
        livro, created = Livro.objects.get_or_create(
            numero=numero,
            defaults={
                'titulo': titulo,
                'descricao': f'Livro {numero} do Instituto Ruhi',
                'ativo': True
            }
        )
        if created:
            livros_criados.append(livro)
    
    all_livros = list(Livro.objects.all())
    print(f"Criados {len(livros_criados)} livros novos do Instituto Ruhi")
    print(f"Total de livros existentes: {len(all_livros)}")
    
    # Criar alguns estudos de exemplo
    print("Criando estudos de exemplo...")
    if contatos and all_livros:
        estudos_exemplo = [
            {
                'livro_numero': 1,
                'status': 'concluido',
                'data_inicio': fake.date_between(start_date='-1y', end_date='-6m'),
                'data_termino': fake.date_between(start_date='-6m', end_date='-3m'),
                'observacoes': 'Primeiro livro do Instituto Ruhi. Muito inspirador!'
            },
            {
                'livro_numero': 2,
                'status': 'concluido',
                'data_inicio': fake.date_between(start_date='-6m', end_date='-3m'),
                'data_termino': fake.date_between(start_date='-3m', end_date='-1m'),
                'observacoes': 'Aprendi muito sobre servir à comunidade.'
            },
            {
                'livro_numero': 3,
                'status': 'em_andamento',
                'data_inicio': fake.date_between(start_date='-2m', end_date='today'),
                'data_termino': None,
                'observacoes': 'Estudando atualmente. Muito interessante!'
            },
            {
                'livro_numero': 7,
                'status': 'nao_iniciado',
                'data_inicio': None,
                'data_termino': None,
                'observacoes': 'Pretendo começar em breve.'
            },
            {
                'livro_numero': 4,
                'status': 'pausado',
                'data_inicio': fake.date_between(start_date='-3m', end_date='-1m'),
                'data_termino': None,
                'observacoes': 'Pausei temporariamente por falta de tempo.'
            }
        ]
        
        estudos_criados = []
        # Atribuir estudos para alguns contatos aleatórios
        contatos_sample = fake.random.sample(contatos, min(len(contatos), 8))
        
        for contato in contatos_sample:
            # Escolher um livro aleatório dos estudos exemplo
            estudo_data = fake.random.choice(estudos_exemplo)
            try:
                livro = Livro.objects.get(numero=estudo_data['livro_numero'])
                
                # Atualizar o contato com o estudo
                contato.livro_estudando = livro
                contato.status_estudo = estudo_data['status']
                contato.data_inicio_estudo = estudo_data['data_inicio']
                contato.data_termino_estudo = estudo_data['data_termino']
                contato.observacoes_estudo = estudo_data['observacoes']
                contato.save()
                
                estudos_criados.append(contato)
            except Exception as e:
                print(f"Erro ao atribuir estudo para {contato.first_name}: {e}")
        
        print(f"Atribuídos {len(estudos_criados)} estudos de exemplo")

    print(f"\nDados criados com sucesso!")
    print(f"- {len(ruas)} ruas")
    print(f"- {len(familias)} famílias")
    print(f"- {len(contatos)} contatos")
    print(f"- {len(all_livros)} livros Ruhi")
    print(f"\nPara testar:")
    print(f"1. Acesse /familia/create/ para criar nova família")
    print(f"2. Teste adicionar contatos existentes")
    print(f"3. Teste criar novos contatos")
    print(f"4. Teste criar novas ruas")
    print(f"5. Acesse /livros-ruhi/ para ver seus livros do Instituto Ruhi")