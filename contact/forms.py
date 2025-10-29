from django import forms
from django.core.exceptions import ValidationError
from contact.models import Contact
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from .models import Familia, Rua, GrupoFamilias, GrupoPreJovens, AulaCrianca, CirculoEstudo, Livro, CategoriaLivro, ReuniaoDevocional
from .widgets import ParticipanteWidget
from dal import autocomplete
from .utils import contatos_do_usuario
from .mixins import CycleSelectorMixin, HistoricoAutomaticoMixin



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'familia', 'birth_date', 'is_bahai', 'description', 'rua']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_bahai': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'is_bahai': 'Marque se a pessoa é Bahá\'í',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['familia'].queryset = Familia.objects.filter(owner=user)
            self.fields['rua'].queryset = Rua.objects.filter(owner=user)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError("First name is required.", code='required')
        return first_name


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. 30 characters or fewer.',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. 30 characters or fewer.',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User 
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.", code='required')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.", code='unique')
        return email   


class RegisterUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. 30 characters or fewer.',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. 30 characters or fewer.',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        required=False,  # Alterado para False
        help_text='Garanta que seja um email válido.',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', }),
        help_text=password_validation.password_validators_help_text_html(),
        required=False
    )
    password2 = forms.CharField(
        label='Confirm Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', }),
        help_text='Enter the same password as above, for verification.',
        required=False
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        # Permite campo vazio se já houver email registrado
        if not email and current_email:
            return current_email

        # if not email:
        #     raise ValidationError("Email is required.", code='required')

        if current_email != email:
            if User.objects.filter(email=email).exists():
                raise ValidationError("Email already exists.", code='unique')
        return email

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = super().save(commit=False)
        password = cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()
        
        return user
       
    
    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            self.add_error('password2', ValidationError('Passwords do not match.'))

        return super().clean()

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as e:
                self.add_error(
                    'password1',
                    ValidationError(e)
                )
        return password1


class FamiliaForm(CycleSelectorMixin, HistoricoAutomaticoMixin, forms.ModelForm):
    membros = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Selecione os membros da família'
    )
    
    class Meta:
        model = Familia
        fields = ('nome', 'rua', 'endereco', 'reuniao_devocional', 
                 'data_ultima_reuniao', 'nivel_envolvimento', 'description', 
                 'membros', 'plano_ciclo', 'numero_ciclo_criacao')

    def __init__(self, *args, **kwargs):
        # user já será extraído pelo CycleSelectorMixin
        super().__init__(*args, **kwargs)
        
        if hasattr(self, 'user') and self.user:
            self.fields['rua'].queryset = Rua.objects.filter(owner=self.user)
            self.fields['membros'].queryset = Contact.objects.filter(
                owner=self.user)
            
        # Se estamos editando uma família existente, carregue os membros atuais
        if self.instance and self.instance.pk:
            self.fields['membros'].initial = self.instance.membros.all()

    def save(self, commit=True):
        familia = super().save(commit)
        if commit:
            # Primeiro, remove todos os contatos desta família
            Contact.objects.filter(familia=familia).update(familia=None)
            # Depois, adiciona os novos membros selecionados
            membros_selecionados = self.cleaned_data.get('membros')
            if membros_selecionados:
                for membro in membros_selecionados:
                    membro.familia = familia
                    membro.save()
            
            # Se reuniao_devocional=True e tem ciclo configurado, 
            # criar histórico automático
            if (familia.reuniao_devocional and familia.plano_ciclo and 
                familia.numero_ciclo_criacao):
                self.salvar_no_historico_se_necessario(familia)
                
        return familia


class RuaForm(forms.ModelForm):
    class Meta:
        model = Rua
        fields = ('nome', 'bairro', 'description')  # Adicionado 'description'



class GrupoPreJovensForm(CycleSelectorMixin, forms.ModelForm):
    class Meta:
        model = GrupoPreJovens
        fields = ('nome', 'rua', 'livro', 'licoes', 'description', 'pre_jovens', 'animador', 'data_ultimo_encontro', 'dia_semana', 'plano_ciclo', 'numero_ciclo_criacao')
        widgets = {
            'pre_jovens': forms.CheckboxSelectMultiple,
            # Remova esta linha:
            # 'rua': forms.CheckboxSelectMultiple,
            # 'animador': forms.RadioSelect,  # Opcional, se quiser radio no form
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['pre_jovens'].queryset = Contact.objects.filter(owner=user)
            self.fields['animador'].queryset = Contact.objects.filter(owner=user)
            self.fields['rua'].queryset = Rua.objects.filter(owner=user)

class AulaCriancaForm(CycleSelectorMixin, forms.ModelForm):
    class Meta:
        model = AulaCrianca
        fields = ('nome', 'rua', 'participantes', 'serie', 'licao', 'dia_semana', 'data_ultima_aula', 'description', 'professor', 'plano_ciclo', 'numero_ciclo_criacao')
        widgets = {
            'participantes': forms.CheckboxSelectMultiple,
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['rua'].queryset = Rua.objects.filter(owner=user)
            self.fields['participantes'].queryset = Contact.objects.filter(owner=user)
            self.fields['professor'].queryset = Contact.objects.filter(owner=user)


class GrupoFamiliasForm(forms.ModelForm):
    class Meta:
        model = GrupoFamilias
        fields = ('nome', 'participantes', 'familias', 'ruas', 'description', 'data_ultima_reuniao_reflexao')
        widgets = {
            'participantes': forms.CheckboxSelectMultiple,
            'familias': forms.CheckboxSelectMultiple,
            'ruas': forms.CheckboxSelectMultiple,
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['participantes'].queryset = Contact.objects.filter(owner=user)
            self.fields['familias'].queryset = Familia.objects.filter(owner=user)
            self.fields['ruas'].queryset = Rua.objects.filter(owner=user)

class CirculoEstudoForm(CycleSelectorMixin, forms.ModelForm):
    class Meta:
        model = CirculoEstudo
        fields = (
            'nome', 'tutor', 'participantes', 'dia_semana', 'data_ultimo_encontro',
            'livro_ruhi', 'livro', 'unidade', 'secao', 'description', 'rua', 'plano_ciclo', 'numero_ciclo_criacao'
        )
        widgets = {
            'participantes': forms.CheckboxSelectMultiple,
            # NÃO defina 'rua' aqui, pois você renderiza manualmente
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['tutor'].queryset = Contact.objects.filter(owner=user)
            self.fields['participantes'].queryset = Contact.objects.filter(owner=user)
            self.fields['rua'].queryset = Rua.objects.filter(owner=user)
        
        # Configurar o campo livro_ruhi
        self.fields['livro_ruhi'].queryset = Livro.objects.filter(ativo=True).order_by('numero')
        self.fields['livro_ruhi'].empty_label = "Selecione um livro do Instituto Ruhi"
        
        # Configurar labels e help_text
        self.fields['livro_ruhi'].label = "Livro do Instituto Ruhi"
        self.fields['livro'].label = "Outros livros/materiais"
        self.fields['livro'].help_text = "Para livros que não são do Instituto Ruhi"

    def clean(self):
        cleaned = super().clean()
        # Força a limpeza do campo rua
        cleaned['rua'] = self.clean_rua()
        return cleaned

    def clean_rua(self):
        data = self.data.getlist('rua')
        if not data:
            return None
        if len(data) > 1:
            raise ValidationError("Selecione apenas uma rua.")
        try:
            return Rua.objects.get(pk=data[0])
        except Rua.DoesNotExist:
            raise ValidationError("Rua inválida.")


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['categoria', 'numero', 'titulo', 'descricao', 'ativo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Descrição do conteúdo do livro...'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'categoria': 'Categoria à qual este livro pertence',
            'numero': 'Número do livro/série (1, 2, 3, etc.)',
            'titulo': 'Título completo do livro',
            'descricao': 'Descrição opcional do conteúdo',
            'ativo': 'Se o livro está disponível para estudo'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = CategoriaLivro.objects.filter(ativo=True).order_by('ordem', 'nome')
        self.fields['categoria'].empty_label = "Selecione uma categoria"


class CategoriaLivroForm(forms.ModelForm):
    class Meta:
        model = CategoriaLivro
        fields = ['nome', 'descricao', 'cor', 'ordem', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Descrição da categoria...'}),
            'cor': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'nome': 'Nome descritivo da categoria',
            'descricao': 'Descrição opcional da categoria',
            'cor': 'Cor para identificar a categoria',
            'ordem': 'Ordem de exibição (menor número aparece primeiro)',
            'ativo': 'Se a categoria está disponível para uso'
        }


class ReuniaoDevocionalForm(CycleSelectorMixin, forms.ModelForm):
    class Meta:
        model = ReuniaoDevocional
        fields = [
            'nome', 'rua', 'numero_participantes', 'participantes_bahais', 
            'dia_semana', 'horario', 'frequencia', 'descricao', 'local_detalhes', 
            'plano_ciclo', 'numero_ciclo_criacao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Reunião Devocional'}),
            'rua': forms.Select(attrs={'class': 'form-control'}),
            'numero_participantes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'participantes_bahais': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'dia_semana': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Domingo'}),
            'horario': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'frequencia': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Descrição da reunião devocional...'}),
            'local_detalhes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Casa da família Silva'}),
        }
        help_texts = {
            'nome': 'Nome ou identificação da reunião devocional',
            'numero_participantes': 'Número total de participantes',
            'participantes_bahais': 'Quantos dos participantes são Bahá\'ís',
            'dia_semana': 'Dia da semana que acontece a reunião',
            'horario': 'Horário da reunião',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar ruas do usuário
            self.fields['rua'].queryset = Rua.objects.filter(owner=user)


class CyclePlanForm(forms.ModelForm):
    """Formulário para criar/editar planos de ciclos"""
    
    class Meta:
        from .models import ConfiguracaoEstatisticas
        model = ConfiguracaoEstatisticas
        fields = [
            'titulo_plano', 'descricao', 'principal', 'data_inicio_plano',
            'duracao_ciclo_meses', 'total_ciclos_plano'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'data_inicio_plano': forms.DateInput(attrs={'type': 'date'}),
            'principal': forms.CheckboxInput(
                attrs={'help_text': 'Marque se este é o plano principal'}
            ),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Verificar se já existe um plano principal
        if self.user:
            from .models import ConfiguracaoEstatisticas
            tem_principal = ConfiguracaoEstatisticas.objects.filter(
                owner=self.user, principal=True
            ).exists()
            
            if tem_principal and not (self.instance and self.instance.principal):
                self.fields['principal'].help_text = (
                    "Já existe um plano principal. Marcar este como principal "
                    "tornará o outro como secundário."
                )



