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
    show = models.BooleanField(default=True)
    bairro =  models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)  # Adicionado

    def __str__(self):
        return self.nome

    @property
    def familias_conectadas(self):
        return self.familias.all()
    @property
    def grupos_pre_jovens_conectados(self):
        return self.grupos_pre_jovens.all()
    @property
    def aulas_crianca_conectadas(self):
        return self.aulas_crianca.all()
    @property
    def grupos_familias_conectados(self):
        return self.grupos_familias.all()

class Familia(models.Model):
    nome = models.CharField(max_length=100)
    rua = models.ForeignKey('Rua', on_delete=models.SET_NULL, null=True, related_name='familias')
    endereco = models.CharField(max_length=255, blank=True)
    reuniao_devocional = models.BooleanField(default=False)
    data_ultima_reuniao = models.DateField(null=True, blank=True)
    nivel_envolvimento = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    @property
    def membros(self):
        return self.contact_set.all()
    @property
    def grupos_familias_conectados(self):
        return self.grupos_familias.all()

class Contact(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    familia = models.ForeignKey(Familia, on_delete=models.SET_NULL, null=True, blank=True, related_name='membros')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)
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

class GrupoPreJovens(models.Model):
    nome = models.CharField(max_length=100)
    rua = models.ForeignKey(Rua, on_delete=models.SET_NULL, null=True, related_name='grupos_pre_jovens')
    livro = models.CharField(max_length=100, blank=True)
    licoes = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)  # Corrigido
    pre_jovens = models.ManyToManyField('Contact', related_name='grupos_pre_jovens')
    animador = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='grupos_pre_jovens_como_animador')  # <-- Adicione esta linha
    data_ultimo_encontro = models.DateField(null=True, blank=True)
    dia_semana = models.CharField(max_length=30, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class AulaCrianca(models.Model):
    nome = models.CharField(max_length=100)
    rua = models.ForeignKey(Rua, on_delete=models.SET_NULL, null=True, related_name='aulas_crianca', blank=True)
    participantes = models.ManyToManyField('Contact', related_name='aulas_crianca')
    serie = models.CharField(max_length=100, blank=True)
    licao = models.CharField(max_length=100, blank=True)
    dia_semana = models.CharField(max_length=30, blank=True)
    data_ultima_aula = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)  # Corrigido
    professor = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='aulas_como_professor')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class GrupoFamilias(models.Model):
    nome = models.CharField(max_length=100)
    participantes = models.ManyToManyField(Contact, blank=True)
    familias = models.ManyToManyField(Familia, blank=True)
    ruas = models.ManyToManyField(Rua, blank=True)
    description = models.TextField(blank=True)
    data_ultima_reuniao_reflexao = models.DateField("Data da última reunião de reflexão", null=True, blank=True)  # <-- Adicione esta linha
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class CirculoEstudo(models.Model):
    nome = models.CharField(max_length=100)
    tutor = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='circulos_como_tutor')
    participantes = models.ManyToManyField('Contact', related_name='circulos_estudo')
    rua = models.ForeignKey('Rua', on_delete=models.SET_NULL, null=True, blank=True, related_name='circulos_estudo')  # <-- Adicione esta linha
    dia_semana = models.CharField(max_length=30, blank=True)
    data_ultimo_encontro = models.DateField(null=True, blank=True)
    livro = models.CharField(max_length=100, blank=True)
    unidade = models.CharField(max_length=100, blank=True)
    secao = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['familias'].queryset = Familia.objects.filter(owner=user)
