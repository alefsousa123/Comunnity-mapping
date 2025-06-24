import os
import sys
from datetime import datetime
from pathlib import Path
from random import choice

import django
from django.conf import settings

DJANGO_BASE_DIR = Path(__file__).parent.parent
NUMBER_OF_OBJECTS = 1000
NUMBER_OF_FAMILIAS = 100
NUMBER_OF_RUAS = 15

sys.path.append(str(DJANGO_BASE_DIR))
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
settings.USE_TZ = False

django.setup()

if __name__ == '__main__':
    import faker

    from contact.models import Contact, Familia, Rua
    from django.contrib.auth import get_user_model

    User = get_user_model()
    owner = User.objects.get(username="alef_azevedo")

    Contact.objects.all().delete()
    Familia.objects.all().delete()
    Rua.objects.all().delete()

    fake = faker.Faker('pt_BR')

    # Criar ruas
    django_ruas = []
    for _ in range(NUMBER_OF_RUAS):
        rua = Rua(
            nome=fake.street_name(),
            bairro=fake.city(),
            owner=owner,
            show=True
        )
        django_ruas.append(rua)
    Rua.objects.bulk_create(django_ruas)
    ruas = list(Rua.objects.all())

    # Criar famílias
    django_familias = []
    for _ in range(NUMBER_OF_FAMILIAS):
        familia = Familia(
            nome=fake.last_name() + " Family",
            rua=choice(ruas),
            endereco=fake.address(),
            reuniao_devocional=fake.boolean(),
            data_ultima_reuniao=fake.date_this_year(),
            nivel_envolvimento=choice(['Baixo', 'Médio', 'Alto']),
            description=fake.text(max_nb_chars=100),
            owner=owner,
            show=True
        )
        django_familias.append(familia)
    Familia.objects.bulk_create(django_familias)
    familias = list(Familia.objects.all())

    # Criar contatos
    django_contacts = []
    for _ in range(NUMBER_OF_OBJECTS):
        profile = fake.profile()
        name_parts = profile['name'].split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        description = fake.text(max_nb_chars=100)
        familia = choice(familias)
        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            birth_date=fake.date_of_birth(minimum_age=1, maximum_age=90),
            description=description,
            familia=familia,
            owner=owner,
            show=True,
        )
        django_contacts.append(contact)

    if django_contacts:
        Contact.objects.bulk_create(django_contacts)