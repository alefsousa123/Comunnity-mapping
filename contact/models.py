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
    rua = models.ForeignKey('Rua', on_delete=models.SET_NULL, null=True, 
                           related_name='familias')
    endereco = models.CharField(max_length=255, blank=True)
    reuniao_devocional = models.BooleanField(default=False)
    data_ultima_reuniao = models.DateField(null=True, blank=True)
    nivel_envolvimento = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                             blank=True)
    show = models.BooleanField(default=True)
    
    # Campos para RD (Reunião Devocional) - quando reuniao_devocional=True
    plano_ciclo = models.ForeignKey('ConfiguracaoEstatisticas', 
                                   on_delete=models.SET_NULL, null=True, 
                                   blank=True, 
                                   help_text="Plano de ciclos da RD")
    numero_ciclo_criacao = models.IntegerField(null=True, blank=True, 
                                              help_text="Número do ciclo em que a RD foi criada")

    def __str__(self):
        return self.nome

    @property
    def membros(self):
        return self.contact_set.all()
    @property
    def grupos_familias_conectados(self):
        return self.grupos_familias.all()

class Contact(models.Model):
    STATUS_ESTUDO_CHOICES = [
        ('nao_iniciado', 'Não Iniciado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('pausado', 'Pausado'),
    ]
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_bahai = models.BooleanField(default=False, help_text="Marque se a pessoa é Bahá'í")
    familia = models.ForeignKey(Familia, on_delete=models.SET_NULL, null=True, blank=True, related_name='membros')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)
    rua = models.ForeignKey(Rua, on_delete=models.SET_NULL, null=True, blank=True, related_name='contatos')
    
    # Campos relacionados ao estudo de livros
    livro_estudando = models.ForeignKey('Livro', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='estudantes', 
                                       help_text='Livro que está estudando atualmente')
    status_estudo = models.CharField(max_length=20, choices=STATUS_ESTUDO_CHOICES, 
                                   default='nao_iniciado',
                                   help_text='Status do estudo atual')
    data_inicio_estudo = models.DateField(null=True, blank=True, 
                                        help_text='Data que começou a estudar o livro atual')
    data_termino_estudo = models.DateField(null=True, blank=True, 
                                         help_text='Data que terminou o livro atual')
    observacoes_estudo = models.TextField(blank=True, 
                                        help_text='Observações sobre o estudo atual')
    
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
    
    @property
    def tem_estudo_ativo(self):
        """Verifica se tem um estudo em andamento"""
        return self.livro_estudando is not None and self.status_estudo in ['em_andamento', 'pausado']
    
    @property
    def duracao_estudo_atual(self):
        """Retorna a duração do estudo atual em dias"""
        if self.data_inicio_estudo and self.data_termino_estudo:
            return (self.data_termino_estudo - self.data_inicio_estudo).days
        return None
    
    @property
    def dias_estudando_atual(self):
        """Retorna quantos dias está estudando o livro atual"""
        if self.data_inicio_estudo and not self.data_termino_estudo:
            from datetime import date
            return (date.today() - self.data_inicio_estudo).days
        return None
    
    def iniciar_estudo(self, livro):
        """Inicia o estudo de um novo livro"""
        from datetime import date
        self.livro_estudando = livro
        self.status_estudo = 'em_andamento'
        self.data_inicio_estudo = date.today()
        self.data_termino_estudo = None
        self.save()
    
    def concluir_estudo(self):
        """Marca o estudo atual como concluído"""
        if self.livro_estudando:
            from datetime import date
            self.status_estudo = 'concluido'
            self.data_termino_estudo = date.today()
            self.save()
    
    def pausar_estudo(self):
        """Pausa o estudo atual"""
        if self.livro_estudando:
            self.status_estudo = 'pausado'
            self.save()
    
    def retomar_estudo(self):
        """Retoma o estudo pausado"""
        if self.livro_estudando and self.status_estudo == 'pausado':
            self.status_estudo = 'em_andamento'
            self.save()
    
    def concluir_estudo_e_adicionar_historico(self):
        """Conclui o estudo atual e adiciona ao histórico"""
        if self.livro_estudando and self.status_estudo in ['em_andamento', 'pausado']:
            from datetime import date
            
            # Criar entrada no histórico
            HistoricoEstudo.objects.get_or_create(
                contato=self,
                livro=self.livro_estudando,
                defaults={
                    'status': 'concluido',
                    'data_inicio': self.data_inicio_estudo,
                    'data_termino': date.today(),
                    'observacoes': self.observacoes_estudo or ''
                }
            )
            
            # Limpar estudo atual
            self.livro_estudando = None
            self.status_estudo = 'nao_iniciado'
            self.data_inicio_estudo = None
            self.data_termino_estudo = None
            self.observacoes_estudo = ''
            self.save()
    
    @property
    def livros_concluidos(self):
        """Retorna todos os livros que este contato já concluiu"""
        return self.historico_estudos.filter(status='concluido').order_by('-data_termino')
    
    @property
    def tem_estudos_ativos(self):
        """Verifica se tem estudos em andamento"""
        return self.estudos_atuais.filter(status='em_andamento').exists()
    
    @property
    def todos_estudos_atuais(self):
        """Retorna todos os estudos atuais (em andamento e pausados)"""
        return self.estudos_atuais.all()
    
    @property
    def estudos_em_andamento(self):
        """Retorna apenas estudos em andamento"""
        return self.estudos_atuais.filter(status='em_andamento')
    
    @property
    def estudos_pausados(self):
        """Retorna apenas estudos pausados"""
        return self.estudos_atuais.filter(status='pausado')
    
    def adicionar_estudo(self, livro, data_inicio=None, observacoes='', plano=None, ciclo_criacao=None):
        """Adiciona um novo livro aos estudos atuais"""
        from datetime import date
        
        # Verificar se já não está estudando este livro
        if self.estudos_atuais.filter(livro=livro).exists():
            return None, "Já está estudando este livro"
        
        # Verificar se já não concluiu este livro
        if self.historico_estudos.filter(livro=livro, status='concluido').exists():
            return None, "Já concluiu este livro"
        
        # Se não especificado plano ou ciclo, usar o plano principal e ciclo atual
        if not plano:
            from .models import ConfiguracaoEstatisticas
            plano = ConfiguracaoEstatisticas.objects.filter(
                owner=self.owner, principal=True
            ).first()
        
        if not ciclo_criacao and plano:
            ciclo_info = plano.calcular_ciclo_atual()
            ciclo_criacao = ciclo_info['numero'] if ciclo_info else None
        
        estudo = EstudoAtual.objects.create(
            contato=self,
            livro=livro,
            status='em_andamento',
            data_inicio=data_inicio or date.today(),
            observacoes=observacoes,
            plano_ciclo=plano,
            numero_ciclo_criacao=ciclo_criacao
        )
        
        # Verificar se deve salvar no histórico usando o mixin
        if plano and ciclo_criacao:
            from .mixins import HistoricoAutomaticoMixin
            mixin = HistoricoAutomaticoMixin()
            mixin.salvar_no_historico_se_necessario(estudo, ciclo_criacao)
        
        return estudo, "Estudo adicionado com sucesso"
    
    def remover_estudo(self, livro):
        """Remove um livro dos estudos atuais"""
        try:
            estudo = self.estudos_atuais.get(livro=livro)
            estudo.delete()
            return True, "Estudo removido com sucesso"
        except EstudoAtual.DoesNotExist:
            return False, "Estudo não encontrado"

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
    
    # Campos para rastreamento de ciclo de criação
    plano_ciclo = models.ForeignKey('ConfiguracaoEstatisticas', on_delete=models.SET_NULL, null=True, blank=True, help_text="Plano de ciclos em que foi criado")
    numero_ciclo_criacao = models.IntegerField(null=True, blank=True, help_text="Número do ciclo em que foi criado")
    data_criacao_definida = models.DateField(null=True, blank=True, help_text="Data específica de criação (para dados históricos)")
    
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    @property
    def ciclo_info(self):
        """Retorna informações do ciclo de criação"""
        if self.plano_ciclo and self.numero_ciclo_criacao:
            return f"{self.plano_ciclo.titulo_plano} - Ciclo {self.numero_ciclo_criacao}"
        return "Não definido"

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
    
    # Campos para rastreamento de ciclo de criação
    plano_ciclo = models.ForeignKey('ConfiguracaoEstatisticas', on_delete=models.SET_NULL, null=True, blank=True, help_text="Plano de ciclos")
    numero_ciclo_criacao = models.IntegerField(null=True, blank=True, help_text="Número do ciclo de criação")
    data_criacao_definida = models.DateField(null=True, blank=True, help_text="Data de criação para histórico")
    
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    @property
    def ciclo_info(self):
        """Retorna informações do ciclo de criação"""
        if self.plano_ciclo and self.numero_ciclo_criacao:
            return f"{self.plano_ciclo.titulo_plano} - Ciclo {self.numero_ciclo_criacao}"
        return "Não definido"

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
    livro_ruhi = models.ForeignKey('Livro', on_delete=models.SET_NULL, null=True, blank=True, related_name='circulos_estudo', help_text='Livro do Instituto Ruhi que está sendo estudado')
    livro = models.CharField(max_length=100, blank=True, help_text='Campo antigo - será removido em migração futura')
    unidade = models.CharField(max_length=100, blank=True)
    secao = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    show = models.BooleanField(default=True)
    # Campos para rastreamento de ciclos
    plano_ciclo = models.ForeignKey('ConfiguracaoEstatisticas', on_delete=models.SET_NULL, null=True, blank=True, 
                                   help_text='Plano de ciclos ao qual pertence')
    numero_ciclo_criacao = models.IntegerField(null=True, blank=True,
                                             help_text='Ciclo em que foi criado')
    data_criacao_definida = models.DateField(null=True, blank=True,
                                           help_text='Data específica de criação')

    def __str__(self):
        return self.nome

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['familias'].queryset = Familia.objects.filter(owner=user)


class CategoriaLivro(models.Model):
    """Modelo para categorizar livros do Instituto Ruhi e outros materiais"""
    nome = models.CharField(max_length=200, help_text='Nome da categoria (ex: Instituto Ruhi, Aulas Bahá\'ís para Crianças)')
    descricao = models.TextField(blank=True, help_text='Descrição da categoria')
    cor = models.CharField(max_length=7, default='#007bff', help_text='Cor da categoria em hexadecimal')
    ordem = models.PositiveIntegerField(default=0, help_text='Ordem de exibição')
    ativo = models.BooleanField(default=True, help_text='Se a categoria está ativa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Categoria de Livro'
        verbose_name_plural = 'Categorias de Livros'
    
    def __str__(self):
        return self.nome
    
    @property
    def total_livros(self):
        """Total de livros nesta categoria"""
        return self.livros.filter(ativo=True).count()
    
    @property
    def livros_ordenados(self):
        """Livros desta categoria ordenados por número"""
        return self.livros.filter(ativo=True).order_by('numero')


class Livro(models.Model):
    """Modelo para representar os livros do Instituto Ruhi e outros materiais"""
    categoria = models.ForeignKey('CategoriaLivro', on_delete=models.CASCADE, related_name='livros', 
                                 null=True, blank=True, help_text='Categoria do livro')
    numero = models.PositiveIntegerField(help_text='Número do livro/série (1, 2, 3, etc.)')
    titulo = models.CharField(max_length=200, help_text='Título completo do livro')
    descricao = models.TextField(blank=True, help_text='Descrição do conteúdo do livro')
    ativo = models.BooleanField(default=True, help_text='Se o livro está disponível para estudo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['categoria__ordem', 'categoria__nome', 'numero']
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        # Removido unique_together temporariamente para migração
    
    def __str__(self):
        if self.categoria and self.categoria.nome == 'Instituto Ruhi':
            return f"Livro {self.numero} - {self.titulo}"
        elif self.categoria:
            return f"{self.categoria.nome} {self.numero} - {self.titulo}"
        else:
            return f"Livro {self.numero} - {self.titulo}"
    
    @property
    def estudantes_atuais(self):
        """Retorna contatos que estão estudando este livro atualmente"""
        return Contact.objects.filter(
            livro_estudando=self,
            status_estudo='em_andamento'
        )
    
    @property
    def estudantes_concluidos(self):
        """Retorna contatos que concluíram este livro (usando histórico)"""
        return Contact.objects.filter(
            historico_estudos__livro=self,
            historico_estudos__status='concluido'
        ).distinct()
    
    @property
    def estudantes_pausados(self):
        """Retorna contatos que pausaram este livro"""
        return Contact.objects.filter(
            livro_estudando=self,
            status_estudo='pausado'
        )
    
    @property
    def total_estudantes_atual(self):
        """Total de pessoas estudando este livro atualmente"""
        return self.estudantes_atuais.count()
    
    @property
    def total_estudantes_concluidos(self):
        """Total de pessoas que concluíram este livro (usando histórico)"""
        return self.estudantes_concluidos.count()
    
    @property
    def total_estudantes_geral(self):
        """Total geral de pessoas que já estudaram este livro"""
        return Contact.objects.filter(livro_estudando=self).count()


class HistoricoEstudo(models.Model):
    """Modelo para armazenar o histórico de estudos concluídos de cada contato"""
    STATUS_CHOICES = [
        ('concluido', 'Concluído'),
        ('interrompido', 'Interrompido'),
    ]
    
    contato = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='historico_estudos')
    livro = models.ForeignKey('Livro', on_delete=models.CASCADE, related_name='historico_estudos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='concluido')
    data_inicio = models.DateField(null=True, blank=True, help_text='Data de início do estudo')
    data_termino = models.DateField(null=True, blank=True, help_text='Data de conclusão ou interrupção')
    observacoes = models.TextField(blank=True, help_text='Observações sobre o estudo')
    created_at = models.DateTimeField(auto_now_add=True)
    # Campos para rastreamento de ciclos
    plano_ciclo = models.ForeignKey('ConfiguracaoEstatisticas', on_delete=models.SET_NULL, 
                                   null=True, blank=True, 
                                   help_text='Plano de ciclos ao qual pertence')
    numero_ciclo_criacao = models.IntegerField(null=True, blank=True,
                                             help_text='Ciclo em que foi criado')
    data_criacao_definida = models.DateField(null=True, blank=True,
                                           help_text='Data específica de criação')
    
    class Meta:
        ordering = ['-data_termino', '-created_at']
        verbose_name = 'Histórico de Estudo'
        verbose_name_plural = 'Histórico de Estudos'
        unique_together = ['contato', 'livro']  # Um contato pode concluir o mesmo livro apenas uma vez
    
    def __str__(self):
        return f"{self.contato.first_name} - {self.livro} ({self.get_status_display()})"
    
    @property
    def duracao_estudo(self):
        """Retorna a duração do estudo em dias"""
        if self.data_inicio and self.data_termino:
            return (self.data_termino - self.data_inicio).days
        return None


class EstudoAtual(models.Model):
    """Modelo para representar estudos atuais (permite múltiplos livros por contato)"""
    STATUS_CHOICES = [
        ('em_andamento', 'Em Andamento'),
        ('pausado', 'Pausado'),
    ]
    
    contato = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='estudos_atuais')
    livro = models.ForeignKey('Livro', on_delete=models.CASCADE, related_name='estudos_atuais')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    data_inicio = models.DateField(null=True, blank=True, help_text='Data de início do estudo')
    observacoes = models.TextField(blank=True, help_text='Observações sobre o estudo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Campos para rastreamento de ciclos
    plano_ciclo = models.ForeignKey('ConfiguracaoEstatisticas', on_delete=models.SET_NULL, 
                                   null=True, blank=True, 
                                   help_text='Plano de ciclos ao qual pertence')
    numero_ciclo_criacao = models.IntegerField(null=True, blank=True,
                                             help_text='Ciclo em que foi criado')
    data_criacao_definida = models.DateField(null=True, blank=True,
                                           help_text='Data específica de criação')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Estudo Atual'
        verbose_name_plural = 'Estudos Atuais'
        unique_together = ['contato', 'livro']  # Um contato não pode estudar o mesmo livro múltiplas vezes simultaneamente
    
    def __str__(self):
        return f"{self.contato.first_name} - {self.livro} ({self.get_status_display()})"
    
    @property
    def dias_estudando(self):
        """Retorna quantos dias está estudando este livro"""
        if self.data_inicio:
            from datetime import date
            return (date.today() - self.data_inicio).days
        return None
    
    def concluir(self, observacoes_conclusao=''):
        """Conclui este estudo e adiciona ao histórico"""
        from datetime import date
        
        # Criar entrada no histórico
        HistoricoEstudo.objects.get_or_create(
            contato=self.contato,
            livro=self.livro,
            defaults={
                'status': 'concluido',
                'data_inicio': self.data_inicio,
                'data_termino': date.today(),
                'observacoes': observacoes_conclusao or self.observacoes
            }
        )
        
        # Remover estudo atual
        self.delete()
    
    def pausar(self):
        """Pausa este estudo"""
        self.status = 'pausado'
        self.save()
    
    def retomar(self):
        """Retoma este estudo"""
        self.status = 'em_andamento'
        self.save()


class ReuniaoDevocional(models.Model):
    """Modelo para reuniões devocionais"""
    nome = models.CharField(max_length=100, blank=True, help_text="Nome ou identificação da reunião devocional")
    descricao = models.TextField(blank=True, help_text="Descrição da reunião devocional")
    rua = models.ForeignKey(Rua, on_delete=models.SET_NULL, null=True, blank=True, help_text="Local onde acontece a reunião")
    local_detalhes = models.CharField(max_length=200, blank=True, help_text="Detalhes do local (casa, centro comunitário, etc.)")
    
    # Informações sobre participantes
    numero_participantes = models.IntegerField(default=0, help_text="Número de participantes na reunião")
    participantes_bahais = models.IntegerField(default=0, help_text="Quantos participantes são Bahá'ís")
    
    # Informações sobre frequência
    dia_semana = models.CharField(max_length=20, blank=True, help_text="Dia da semana que acontece")
    horario = models.TimeField(null=True, blank=True, help_text="Horário da reunião")
    frequencia = models.CharField(max_length=50, default="Semanal", 
                                choices=[
                                    ('Semanal', 'Semanal'),
                                    ('Quinzenal', 'Quinzenal'),
                                    ('Mensal', 'Mensal'),
                                    ('Esporádica', 'Esporádica'),
                                ])
    
    # Status
    ativa = models.BooleanField(default=True, help_text="Se a reunião está ativa")
    
    # Campos de ciclo - para associação com planos
    plano_ciclo = models.ForeignKey('ConfiguracaoEstatisticas', on_delete=models.SET_NULL, null=True, blank=True, help_text="Plano de ciclos ao qual esta reunião está associada")
    numero_ciclo_criacao = models.IntegerField(null=True, blank=True, help_text="Número do ciclo em que foi criada")
    
    # Metadados
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reunião Devocional"
        verbose_name_plural = "Reuniões Devocionais"
        ordering = ['-ativa', 'dia_semana', 'horario']
    
    def __str__(self):
        nome_exibicao = self.nome if self.nome else f"Reunião {self.id}"
        local = f" - {self.rua}" if self.rua else ""
        return f"{nome_exibicao}{local}"


class ConfiguracaoEstatisticas(models.Model):
    """Configurações gerais para estatísticas - permite múltiplos planos"""
    # Configuração de Ciclos
    titulo_plano = models.CharField(max_length=100, default="Plano de 9 Anos")
    descricao = models.TextField(blank=True, help_text="Descrição opcional do plano")
    data_inicio_plano = models.DateField(default='2022-01-01', help_text="Data de início do primeiro ciclo do plano")
    duracao_ciclo_meses = models.IntegerField(default=3, help_text="Duração de cada ciclo em meses")
    total_ciclos_plano = models.IntegerField(default=36, help_text="Total de ciclos no plano completo")
    ativo = models.BooleanField(default=True, help_text="Se o plano está ativo")
    principal = models.BooleanField(default=True, help_text="Se é o plano principal (usado no dashboard)")
    
    # Campos de configuração de datas antigas mantidos para compatibilidade
    ciclo1_inicio = models.CharField(max_length=5, default="01-21", help_text="Formato: MM-DD")
    ciclo1_fim = models.CharField(max_length=5, default="04-20", help_text="Formato: MM-DD")
    ciclo2_inicio = models.CharField(max_length=5, default="04-21", help_text="Formato: MM-DD")
    ciclo2_fim = models.CharField(max_length=5, default="07-20", help_text="Formato: MM-DD")
    ciclo3_inicio = models.CharField(max_length=5, default="07-21", help_text="Formato: MM-DD")
    ciclo3_fim = models.CharField(max_length=5, default="10-20", help_text="Formato: MM-DD")
    ciclo4_inicio = models.CharField(max_length=5, default="10-21", help_text="Formato: MM-DD")
    ciclo4_fim = models.CharField(max_length=5, default="01-20", help_text="Formato: MM-DD")
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Estatísticas"
        verbose_name_plural = "Configurações de Estatísticas"
        unique_together = ['owner', 'titulo_plano']  # Evita planos duplicados
    
    def __str__(self):
        status = "Principal" if self.principal else "Secundário"
        return f"{self.titulo_plano} ({status}) - {self.owner.username}"
    
    def save(self, *args, **kwargs):
        """Garante que apenas um plano seja principal por usuário"""
        if self.principal:
            # Desmarcar outros como principal
            ConfiguracaoEstatisticas.objects.filter(
                owner=self.owner, principal=True
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)
    
    def obter_ciclos_disponiveis(self):
        """Retorna lista de ciclos disponíveis para seleção"""
        ciclos = []
        for i in range(1, self.total_ciclos_plano + 1):
            ciclo_info = self.calcular_ciclo_especifico(i)
            ciclos.append({
                'numero': i,
                'nome': f"Ciclo {i}",
                'inicio': ciclo_info['inicio'],
                'fim': ciclo_info['fim'],
                'plano': self
            })
        return ciclos
    
    def calcular_ciclo_especifico(self, numero_ciclo):
        """Calcula datas de um ciclo específico"""
        from dateutil.relativedelta import relativedelta
        
        if numero_ciclo < 1 or numero_ciclo > self.total_ciclos_plano:
            return None
        
        # Calcular datas do ciclo específico
        ciclo_inicio = self.data_inicio_plano + relativedelta(
            months=(numero_ciclo - 1) * self.duracao_ciclo_meses
        )
        ciclo_fim = ciclo_inicio + relativedelta(
            months=self.duracao_ciclo_meses
        ) - relativedelta(days=1)
        
        return {
            'numero': numero_ciclo,
            'inicio': ciclo_inicio,
            'fim': ciclo_fim,
            'nome': f"Ciclo {numero_ciclo}",
            'plano': self
        }
    
    def calcular_ciclo_atual(self):
        """Calcula o ciclo atual baseado na data de início e duração"""
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        if not self.ativo:
            return {
                'numero': None,
                'inicio': None,
                'fim': None,
                'nome': "Plano encerrado",
                'progresso': 100
            }
        
        hoje = timezone.now().date()
        
        if hoje < self.data_inicio_plano:
            return {
                'numero': 0,
                'inicio': None,
                'fim': self.data_inicio_plano,
                'nome': "Antes do início do plano",
                'progresso': 0
            }
        
        # Calcular quantos meses se passaram desde o início
        meses_passados = (hoje.year - self.data_inicio_plano.year) * 12 + (hoje.month - self.data_inicio_plano.month)
        
        # Calcular o ciclo atual
        ciclo_numero = (meses_passados // self.duracao_ciclo_meses) + 1
        
        # Verificar se ainda estamos dentro do plano
        if ciclo_numero > self.total_ciclos_plano:
            return {
                'numero': self.total_ciclos_plano,
                'inicio': None,
                'fim': None,
                'nome': f"Plano concluído (Ciclo {self.total_ciclos_plano})",
                'progresso': 100
            }
        
        # Calcular datas do ciclo atual
        ciclo_inicio = self.data_inicio_plano + relativedelta(months=(ciclo_numero - 1) * self.duracao_ciclo_meses)
        ciclo_fim = ciclo_inicio + relativedelta(months=self.duracao_ciclo_meses) - relativedelta(days=1)
        
        # Calcular progresso dentro do ciclo atual
        dias_ciclo = (ciclo_fim - ciclo_inicio).days + 1
        dias_passados = (hoje - ciclo_inicio).days + 1
        progresso_ciclo = min(100, (dias_passados / dias_ciclo) * 100)
        
        return {
            'numero': ciclo_numero,
            'inicio': ciclo_inicio,
            'fim': ciclo_fim,
            'nome': f"Ciclo {ciclo_numero}",
            'progresso': progresso_ciclo,
            'dias_restantes': max(0, (ciclo_fim - hoje).days)
        }
    
    def encerrar_plano(self):
        """Encerra o plano atual"""
        self.ativo = False
        self.save()
    
    def reiniciar_plano(self, nova_data_inicio=None):
        """Reinicia o plano com uma nova data de início"""
        from django.utils import timezone
        self.ativo = True
        if nova_data_inicio:
            self.data_inicio_plano = nova_data_inicio
        else:
            self.data_inicio_plano = timezone.now().date()
        self.save()
    
    def calcular_data_inicio_ciclo(self, numero_ciclo):
        """Calcula a data de início de um ciclo específico"""
        from dateutil.relativedelta import relativedelta
        return self.data_inicio_plano + relativedelta(months=(numero_ciclo - 1) * self.duracao_ciclo_meses)
    
    def calcular_data_fim_ciclo(self, numero_ciclo):
        """Calcula a data de fim de um ciclo específico"""
        from dateutil.relativedelta import relativedelta
        data_inicio = self.calcular_data_inicio_ciclo(numero_ciclo)
        return data_inicio + relativedelta(months=self.duracao_ciclo_meses) - relativedelta(days=1)


class EstatisticasEditaveis(models.Model):


    """Configurações gerais para estatísticas"""
    # Configuração de Ciclos
    titulo_plano = models.CharField(max_length=100, default="Plano de 9 Anos")
    data_inicio_plano = models.DateField(default='2022-01-01', help_text="Data de início do primeiro ciclo do plano")
    duracao_ciclo_meses = models.IntegerField(default=3, help_text="Duração de cada ciclo em meses")
    total_ciclos_plano = models.IntegerField(default=36, help_text="Total de ciclos no plano completo")
    ativo = models.BooleanField(default=True, help_text="Se o plano está ativo ou encerrado")
    
    # Campos de configuração de datas antigas mantidos para compatibilidade
    ciclo1_inicio = models.CharField(max_length=5, default="01-21", help_text="Formato: MM-DD")
    ciclo1_fim = models.CharField(max_length=5, default="04-20", help_text="Formato: MM-DD")
    ciclo2_inicio = models.CharField(max_length=5, default="04-21", help_text="Formato: MM-DD")
    ciclo2_fim = models.CharField(max_length=5, default="07-20", help_text="Formato: MM-DD")
    ciclo3_inicio = models.CharField(max_length=5, default="07-21", help_text="Formato: MM-DD")
    ciclo3_fim = models.CharField(max_length=5, default="10-20", help_text="Formato: MM-DD")
    ciclo4_inicio = models.CharField(max_length=5, default="10-21", help_text="Formato: MM-DD")
    ciclo4_fim = models.CharField(max_length=5, default="01-20", help_text="Formato: MM-DD")
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Estatísticas"
        verbose_name_plural = "Configurações de Estatísticas"
    
    def __str__(self):
        return f"{self.titulo_plano} - {self.owner.username}"
    
    def calcular_ciclo_atual(self):
        """Calcula o ciclo atual baseado na data de início e duração"""
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        if not self.ativo:
            return {
                'numero': None,
                'inicio': None,
                'fim': None,
                'nome': "Plano encerrado",
                'progresso': 100
            }
        
        hoje = timezone.now().date()
        
        if hoje < self.data_inicio_plano:
            return {
                'numero': 0,
                'inicio': None,
                'fim': self.data_inicio_plano,
                'nome': "Antes do início do plano",
                'progresso': 0
            }
        
        # Calcular quantos meses se passaram desde o início
        meses_passados = (hoje.year - self.data_inicio_plano.year) * 12 + (hoje.month - self.data_inicio_plano.month)
        
        # Calcular o ciclo atual
        ciclo_numero = (meses_passados // self.duracao_ciclo_meses) + 1
        
        # Verificar se ainda estamos dentro do plano
        if ciclo_numero > self.total_ciclos_plano:
            return {
                'numero': self.total_ciclos_plano,
                'inicio': None,
                'fim': None,
                'nome': f"Plano concluído (Ciclo {self.total_ciclos_plano})",
                'progresso': 100
            }
        
        # Calcular datas do ciclo atual
        ciclo_inicio = self.data_inicio_plano + relativedelta(months=(ciclo_numero - 1) * self.duracao_ciclo_meses)
        ciclo_fim = ciclo_inicio + relativedelta(months=self.duracao_ciclo_meses) - relativedelta(days=1)
        
        # Calcular progresso dentro do ciclo atual
        dias_ciclo = (ciclo_fim - ciclo_inicio).days + 1
        dias_passados = (hoje - ciclo_inicio).days + 1
        progresso_ciclo = min(100, (dias_passados / dias_ciclo) * 100)
        
        return {
            'numero': ciclo_numero,
            'inicio': ciclo_inicio,
            'fim': ciclo_fim,
            'nome': f"Ciclo {ciclo_numero}",
            'progresso': progresso_ciclo,
            'dias_restantes': max(0, (ciclo_fim - hoje).days)
        }
    
    def encerrar_plano(self):
        """Encerra o plano atual"""
        self.ativo = False
        self.save()
    
    def reiniciar_plano(self, nova_data_inicio=None):
        """Reinicia o plano com uma nova data de início"""
        from django.utils import timezone
        self.ativo = True
        if nova_data_inicio:
            self.data_inicio_plano = nova_data_inicio
        else:
            self.data_inicio_plano = timezone.now().date()
        self.save()


class EstatisticasEditaveis(models.Model):
    """Estatísticas editáveis pelo usuário para comparação"""
    # Atividades Comunitárias
    total_grupos_prejovens = models.IntegerField(default=0, help_text="Número total de grupos de pré-jovens")
    participantes_prejovens = models.IntegerField(default=0)
    participantes_prejovens_bahais = models.IntegerField(default=0)
    
    total_aulas_criancas = models.IntegerField(default=0, help_text="Número total de aulas bahá'ís para crianças")
    participantes_criancas = models.IntegerField(default=0)
    participantes_criancas_bahais = models.IntegerField(default=0)
    
    total_circulos_estudo = models.IntegerField(default=0, help_text="Número total de círculos de estudo")
    participantes_circulos = models.IntegerField(default=0)
    participantes_circulos_bahais = models.IntegerField(default=0)
    
    total_reunioes_devocionais = models.IntegerField(default=0, help_text="Número total de reuniões devocionais")
    participantes_devocionais = models.IntegerField(default=0)
    participantes_devocionais_bahais = models.IntegerField(default=0)
    
    # Detalhamento das Atividades - Grupos de Pré-jovens
    animadores_prejovens = models.IntegerField(default=0, help_text="Número de animadores de pré-jovens")
    locais_prejovens = models.IntegerField(default=0, help_text="Número de locais onde grupos se reúnem")
    
    # Detalhamento das Atividades - Aulas para Crianças
    professores_criancas = models.IntegerField(default=0, help_text="Número de professores de aulas para crianças")
    series_criancas = models.CharField(max_length=200, blank=True, help_text="Séries sendo estudadas")
    
    # Detalhamento das Atividades - Círculos de Estudo
    tutores_circulos = models.IntegerField(default=0, help_text="Número de tutores de círculos")
    livros_circulos = models.CharField(max_length=200, blank=True, help_text="Livros sendo estudados")
    circulos_concluidos = models.IntegerField(default=0, help_text="Círculos concluídos no último ciclo")
    
    # Detalhamento das Atividades - Reuniões Devocionais
    facilitadores_devocionais = models.IntegerField(default=0, help_text="Número de facilitadores de reuniões devocionais")
    
    # Demografia
    total_criancas = models.IntegerField(default=0, help_text="Total de crianças (até 11 anos)")
    total_prejovens = models.IntegerField(default=0, help_text="Total de pré-jovens (12-14 anos)")
    total_jovens = models.IntegerField(default=0, help_text="Total de jovens (15-30 anos)")
    total_adultos = models.IntegerField(default=0, help_text="Total de adultos (30+ anos)")
    
    # Metadados
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estatísticas Editáveis"
        verbose_name_plural = "Estatísticas Editáveis"
    
    def __str__(self):
        return f"Estatísticas de {self.owner.username}"
    
    @property
    def total_participantes(self):
        return (self.participantes_prejovens + 
                self.participantes_criancas + 
                self.participantes_circulos +
                self.participantes_devocionais)
    
    @property
    def total_participantes_bahais(self):
        return (self.participantes_prejovens_bahais + 
                self.participantes_criancas_bahais + 
                self.participantes_circulos_bahais +
                self.participantes_devocionais_bahais)


class HistoricoCiclo(models.Model):
    """Modelo para armazenar dados históricos de cada ciclo"""
    configuracao = models.ForeignKey(ConfiguracaoEstatisticas, on_delete=models.CASCADE, related_name='historicos')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    numero_ciclo = models.IntegerField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    # Dados de atividades no final do ciclo (DADOS EDITÁVEIS)
    total_circulos_estudo = models.IntegerField(default=0)
    total_grupos_prejovens = models.IntegerField(default=0)
    total_aulas_criancas = models.IntegerField(default=0)
    total_reunioes_devocionais = models.IntegerField(default=0)
    total_grupos_familias = models.IntegerField(default=0)
    
    # Dados de participantes no final do ciclo (DADOS EDITÁVEIS)
    participantes_circulos = models.IntegerField(default=0)
    participantes_prejovens = models.IntegerField(default=0)
    participantes_criancas = models.IntegerField(default=0)
    participantes_devocionais = models.IntegerField(default=0)
    participantes_grupos_familias = models.IntegerField(default=0)
    
    # Dados de participantes Bahá'ís no final do ciclo (DADOS EDITÁVEIS)
    participantes_circulos_bahais = models.IntegerField(default=0, help_text="Bahá'ís nos círculos de estudo")
    participantes_prejovens_bahais = models.IntegerField(default=0, help_text="Bahá'ís nos grupos de pré-jovens")
    participantes_criancas_bahais = models.IntegerField(default=0, help_text="Bahá'ís nas aulas de crianças")
    participantes_devocionais_bahais = models.IntegerField(default=0, help_text="Bahá'ís nas reuniões devocionais")
    participantes_grupos_familias_bahais = models.IntegerField(default=0, help_text="Bahá'ís nos grupos de famílias")
    
    # ======= NOVOS CAMPOS: DADOS DO SISTEMA (calculados automaticamente) =======
    # Dados de atividades calculados pelo sistema
    sistema_circulos_estudo = models.IntegerField(default=0, help_text="Círculos de estudo contados pelo sistema")
    sistema_grupos_prejovens = models.IntegerField(default=0, help_text="Grupos de pré-jovens contados pelo sistema")
    sistema_aulas_criancas = models.IntegerField(default=0, help_text="Aulas de crianças contadas pelo sistema")
    sistema_reunioes_devocionais = models.IntegerField(default=0, help_text="Reuniões devocionais contadas pelo sistema")
    sistema_grupos_familias = models.IntegerField(default=0, help_text="Grupos de famílias contados pelo sistema")
    
    # Dados de participantes calculados pelo sistema
    sistema_participantes_circulos = models.IntegerField(default=0, help_text="Participantes em círculos contados pelo sistema")
    sistema_participantes_prejovens = models.IntegerField(default=0, help_text="Participantes em grupos de pré-jovens contados pelo sistema")
    sistema_participantes_criancas = models.IntegerField(default=0, help_text="Participantes em aulas de crianças contados pelo sistema")
    sistema_participantes_devocionais = models.IntegerField(default=0, help_text="Participantes em reuniões devocionais contados pelo sistema")
    sistema_participantes_familias = models.IntegerField(default=0, help_text="Participantes em grupos de famílias contados pelo sistema")
    
    # Dados de participantes Bahá'ís calculados pelo sistema
    sistema_participantes_circulos_bahais = models.IntegerField(default=0, help_text="Bahá'ís em círculos contados pelo sistema")
    sistema_participantes_prejovens_bahais = models.IntegerField(default=0, help_text="Bahá'ís em grupos de pré-jovens contados pelo sistema")
    sistema_participantes_criancas_bahais = models.IntegerField(default=0, help_text="Bahá'ís em aulas de crianças contados pelo sistema")
    sistema_participantes_devocionais_bahais = models.IntegerField(default=0, help_text="Bahá'ís em reuniões devocionais contados pelo sistema")
    sistema_participantes_familias_bahais = models.IntegerField(default=0, help_text="Bahá'ís em grupos de famílias contados pelo sistema")
    
    # Demografia calculada pelo sistema
    sistema_total_criancas = models.IntegerField(default=0, help_text="Total de crianças calculado pelo sistema")
    sistema_total_prejovens = models.IntegerField(default=0, help_text="Total de pré-jovens calculado pelo sistema")
    sistema_total_jovens = models.IntegerField(default=0, help_text="Total de jovens calculado pelo sistema")
    sistema_total_adultos = models.IntegerField(default=0, help_text="Total de adultos calculado pelo sistema")
    # ======= FIM DOS NOVOS CAMPOS =======
    
    # Dados de livros no final do ciclo
    total_livros = models.IntegerField(default=0)
    livros_iniciados = models.IntegerField(default=0)
    livros_concluidos = models.IntegerField(default=0)
    
    # Detalhamento de livros por categoria - Sequência (Ruhi)
    livros_sequencia_iniciados = models.IntegerField(default=0, help_text="Livros da Sequência iniciados no ciclo")
    livros_sequencia_concluidos = models.IntegerField(default=0, help_text="Livros da Sequência concluídos no ciclo")
    
    # Detalhamento de livros por categoria - ABC (Aulas de Crianças)
    livros_abc_iniciados = models.IntegerField(default=0, help_text="Livros de ABC iniciados no ciclo")
    livros_abc_concluidos = models.IntegerField(default=0, help_text="Livros de ABC concluídos no ciclo")
    
    # Detalhamento de livros por categoria - Pré-jovens
    livros_prejovens_iniciados = models.IntegerField(default=0, help_text="Livros de Pré-jovens iniciados no ciclo")
    livros_prejovens_concluidos = models.IntegerField(default=0, help_text="Livros de Pré-jovens concluídos no ciclo")
    
    # Detalhamento de livros por categoria - Outros
    livros_outros_iniciados = models.IntegerField(default=0, help_text="Outros livros iniciados no ciclo")
    livros_outros_concluidos = models.IntegerField(default=0, help_text="Outros livros concluídos no ciclo")
    
    # Crescimento em relação ao ciclo anterior
    crescimento_atividades = models.FloatField(default=0.0)  # Percentual
    crescimento_participantes = models.FloatField(default=0.0)  # Percentual
    crescimento_livros = models.FloatField(default=0.0)  # Percentual
    
    # ======= CAMPOS PARA ATIVIDADES NOVAS DO CICLO =======
    # Atividades criadas especificamente neste ciclo (baseado em numero_ciclo_criacao)
    novas_circulos_estudo = models.IntegerField(default=0, help_text="Círculos de estudo criados especificamente neste ciclo")
    novas_grupos_prejovens = models.IntegerField(default=0, help_text="Grupos de pré-jovens criados especificamente neste ciclo")
    novas_aulas_criancas = models.IntegerField(default=0, help_text="Aulas de crianças criadas especificamente neste ciclo")
    novas_reunioes_devocionais = models.IntegerField(default=0, help_text="Reuniões devocionais criadas especificamente neste ciclo")
    novas_familias_rds = models.IntegerField(default=0, help_text="Famílias com RDs criadas especificamente neste ciclo")
    
    # Livros iniciados especificamente neste ciclo (baseado em numero_ciclo_criacao)
    novos_livros_iniciados = models.IntegerField(default=0, help_text="Livros iniciados especificamente neste ciclo")
    novos_livros_concluidos = models.IntegerField(default=0, help_text="Livros concluídos especificamente neste ciclo")
    
    # Detalhamento de livros novos por categoria
    novos_livros_sequencia = models.IntegerField(default=0, help_text="Livros da Sequência iniciados especificamente neste ciclo")
    novos_livros_abc = models.IntegerField(default=0, help_text="Livros de ABC iniciados especificamente neste ciclo")
    novos_livros_prejovens = models.IntegerField(default=0, help_text="Livros de Pré-jovens iniciados especificamente neste ciclo")
    novos_livros_outros = models.IntegerField(default=0, help_text="Outros livros iniciados especificamente neste ciclo")
    # ======= FIM DOS CAMPOS PARA ATIVIDADES NOVAS =======
    
    data_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['configuracao', 'numero_ciclo']
        ordering = ['-numero_ciclo']
        verbose_name = "Histórico de Ciclo"
        verbose_name_plural = "Históricos de Ciclos"
    
    def __str__(self):
        return f"Histórico - {self.configuracao.titulo_plano} - Ciclo {self.numero_ciclo}"
    
    @property
    def total_atividades(self):
        return (self.total_circulos_estudo + self.total_grupos_prejovens + 
                self.total_aulas_criancas + self.total_reunioes_devocionais + 
                self.total_grupos_familias)
    
    @property
    def total_participantes(self):
        return (self.participantes_circulos + self.participantes_prejovens + 
                self.participantes_criancas + self.participantes_devocionais + 
                self.participantes_grupos_familias)
    
    @property
    def total_participantes_bahais(self):
        return (self.participantes_circulos_bahais + self.participantes_prejovens_bahais + 
                self.participantes_criancas_bahais + self.participantes_devocionais_bahais + 
                self.participantes_grupos_familias_bahais)

    def calcular_dados_sistema(self):
        """Calcula e atualiza os dados do sistema baseado nas atividades reais"""
        from datetime import datetime
        
        owner = self.owner
        
        # Para modelos que existiam no período do histórico, vamos contar todos
        # que pertencem ao usuário (simplificação)
        
        # Contar atividades do usuário
        grupos_prejovens = GrupoPreJovens.objects.filter(owner=owner)
        aulas_criancas = AulaCrianca.objects.filter(owner=owner)
        circulos_estudo = CirculoEstudo.objects.filter(owner=owner)
        reunioes_devocionais = ReuniaoDevocional.objects.filter(owner=owner)
        grupos_familias = GrupoFamilias.objects.filter(owner=owner)
        
        # Contar famílias com RD ativas
        familias_com_rd = Familia.objects.filter(
            owner=owner,
            reuniao_devocional=True
        )
        
        # Atualizar contadores de atividades do sistema
        self.sistema_circulos_estudo = circulos_estudo.count()
        self.sistema_grupos_prejovens = grupos_prejovens.count()
        self.sistema_aulas_criancas = aulas_criancas.count()
        self.sistema_reunioes_devocionais = (reunioes_devocionais.count() + 
                                           familias_com_rd.count())
        self.sistema_grupos_familias = grupos_familias.count()
        
        # Calcular participantes do sistema
        self.sistema_participantes_prejovens = sum(
            g.pre_jovens.count() for g in grupos_prejovens)
        self.sistema_participantes_criancas = sum(
            a.participantes.count() for a in aulas_criancas)
        self.sistema_participantes_circulos = sum(
            c.participantes.count() for c in circulos_estudo)
        self.sistema_participantes_devocionais = (
            sum(r.numero_participantes for r in reunioes_devocionais) +
            sum(f.membros.count() for f in familias_com_rd)
        )
        self.sistema_participantes_familias = sum(
            g.participantes.count() for g in grupos_familias)
        
        # Calcular participantes Bahá'ís do sistema
        self.sistema_participantes_prejovens_bahais = sum(
            g.pre_jovens.filter(is_bahai=True).count() for g in grupos_prejovens)
        self.sistema_participantes_criancas_bahais = sum(
            a.participantes.filter(is_bahai=True).count() for a in aulas_criancas)
        self.sistema_participantes_circulos_bahais = sum(
            c.participantes.filter(is_bahai=True).count() for c in circulos_estudo)
        self.sistema_participantes_devocionais_bahais = (
            sum(r.participantes_bahais for r in reunioes_devocionais) +
            sum(f.membros.filter(is_bahai=True).count() for f in familias_com_rd)
        )
        self.sistema_participantes_familias_bahais = sum(
            g.participantes.filter(is_bahai=True).count() for g in grupos_familias)
        
        # Calcular demografia do sistema
        contatos = Contact.objects.filter(owner=owner)
        from dateutil.relativedelta import relativedelta
        
        hoje = self.data_fim
        criancas = prejovens = jovens = adultos = 0
        
        for contato in contatos:
            if contato.birth_date:
                idade = relativedelta(hoje, contato.birth_date).years
                if idade <= 11:
                    criancas += 1
                elif idade <= 14:
                    prejovens += 1
                elif idade <= 30:
                    jovens += 1
                else:
                    adultos += 1
        
        self.sistema_total_criancas = criancas
        self.sistema_total_prejovens = prejovens
        self.sistema_total_jovens = jovens
        self.sistema_total_adultos = adultos
        
        self.save()


class DetalheLivroHistorico(models.Model):
    """Modelo para armazenar detalhes específicos de cada livro no histórico"""
    
    CATEGORIA_CHOICES = [
        ('sequencia', 'Sequência (Ruhi)'),
        ('abc', 'ABC (Aulas de Crianças)'),
        ('prejovens', 'Pré-jovens'),
        ('outros', 'Outros')
    ]
    
    historico_ciclo = models.ForeignKey(HistoricoCiclo, on_delete=models.CASCADE, related_name='detalhes_livros')
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    nome_livro = models.CharField(max_length=100, help_text="Ex: Livro 1, Série 2, etc.")
    quantidade_iniciados = models.IntegerField(default=0, help_text="Quantas pessoas iniciaram este livro")
    quantidade_concluidos = models.IntegerField(default=0, help_text="Quantas pessoas concluíram este livro")
    observacoes = models.TextField(blank=True, help_text="Observações específicas sobre este livro")
    
    class Meta:
        unique_together = ['historico_ciclo', 'categoria', 'nome_livro']
        ordering = ['categoria', 'nome_livro']
        verbose_name = "Detalhe de Livro no Histórico"
        verbose_name_plural = "Detalhes de Livros no Histórico"
    
    def __str__(self):
        return f"{self.categoria} - {self.nome_livro} (Ciclo {self.historico_ciclo.numero_ciclo})"


class EstatisticasEditaveisHistorico(models.Model):
    """Cópia completa das estatísticas editáveis quando um ciclo é encerrado"""
    # Relacionamento com o histórico do ciclo
    historico_ciclo = models.OneToOneField(
        HistoricoCiclo,
        on_delete=models.CASCADE,
        related_name='estatisticas_editaveis'
    )
    
    # Atividades Comunitárias - cópia exata dos campos de EstatisticasEditaveis
    total_grupos_prejovens = models.IntegerField(default=0)
    participantes_prejovens = models.IntegerField(default=0)
    participantes_prejovens_bahais = models.IntegerField(default=0)
    
    total_aulas_criancas = models.IntegerField(default=0)
    participantes_criancas = models.IntegerField(default=0)
    participantes_criancas_bahais = models.IntegerField(default=0)
    
    total_circulos_estudo = models.IntegerField(default=0)
    participantes_circulos = models.IntegerField(default=0)
    participantes_circulos_bahais = models.IntegerField(default=0)
    
    total_reunioes_devocionais = models.IntegerField(default=0)
    participantes_devocionais = models.IntegerField(default=0)
    participantes_devocionais_bahais = models.IntegerField(default=0)
    
    # Detalhamento das Atividades - Grupos de Pré-jovens
    animadores_prejovens = models.IntegerField(default=0)
    locais_prejovens = models.IntegerField(default=0)
    
    # Detalhamento das Atividades - Aulas para Crianças
    professores_criancas = models.IntegerField(default=0)
    series_criancas = models.CharField(max_length=200, blank=True)
    
    # Detalhamento das Atividades - Círculos de Estudo
    tutores_circulos = models.IntegerField(default=0)
    livros_circulos = models.CharField(max_length=200, blank=True)
    circulos_concluidos = models.IntegerField(default=0)
    
    # Detalhamento das Atividades - Reuniões Devocionais
    facilitadores_devocionais = models.IntegerField(default=0)
    
    # Demografia
    total_criancas = models.IntegerField(default=0)
    total_prejovens = models.IntegerField(default=0)
    total_jovens = models.IntegerField(default=0)
    total_adultos = models.IntegerField(default=0)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Estatísticas Editáveis Históricas"
        verbose_name_plural = "Estatísticas Editáveis Históricas"
    
    def __str__(self):
        ciclo_num = self.historico_ciclo.numero_ciclo
        return f"Estatísticas Editáveis - Ciclo {ciclo_num}"

