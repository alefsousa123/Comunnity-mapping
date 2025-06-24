from os import name
from venv import create
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

# id (primary key - automático)
# first_name (string), last_name (string), phone (string)
# email (email), created_date (date), description (te
class Rua(models.Model):
    nome = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)  # Adicionado
    bairro =  models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.nome

    @property
    def familias_conectadas(self):
        return self.familias.all()

class Familia(models.Model):
    nome = models.CharField(max_length=100)
    rua = models.ForeignKey('Rua', on_delete=models.SET_NULL, null=True, related_name='familias')
    endereco = models.CharField(max_length=255, blank=True)
    reuniao_devocional = models.BooleanField(default=False)
    data_ultima_reuniao = models.DateField(null=True, blank=True)
    nivel_envolvimento = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)  # Adicionado

    def __str__(self):
        return self.nome

    @property
    def membros(self):
        return self.contact_set.all()

class Contact(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    familia = models.ForeignKey(Familia, on_delete=models.SET_NULL, null=True, blank=True, related_name='membros')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)  # Adicionado
    rua = models.ForeignKey(Rua, on_delete=models.SET_NULL, null=True, blank=True, related_name='contatos')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def age_group(self):
        age = self.age
        if age is None:
            return "Idade desconhecida"
        if age <= 11:
            return "Criança"
        elif 12 <= age <= 14:
            return "Pré jovem"
        elif 15 <= age <= 30:
            return "Jovem"
        else:
            return "Adulto"
