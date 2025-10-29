"""
Mixins for forms and views to provide common functionality
"""
from django import forms
from django.utils import timezone


class CycleSelectorMixin:
    """
    Mixin para formulários que precisam de seleção de plano e ciclo
    Adiciona funcionalidade para selecionar o plano e ciclo de criação
    """
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Armazenar o usuário para uso posterior
        self.user = user
        
        if user and hasattr(self, 'fields'):
            # Configurar campo de plano se existir
            if 'plano_ciclo' in self.fields:
                from .models import ConfiguracaoEstatisticas
                planos_queryset = ConfiguracaoEstatisticas.objects.filter(
                    owner=user, ativo=True
                ).order_by('-principal', 'titulo_plano')
                
                self.fields['plano_ciclo'].queryset = planos_queryset
                self.fields['plano_ciclo'].empty_label = "Selecione um plano"
                
                # Se há um plano principal, definir como padrão
                plano_principal = planos_queryset.filter(principal=True).first()
                if plano_principal and not self.instance.pk:
                    self.fields['plano_ciclo'].initial = plano_principal
            
            # Configurar campo de ciclo se existir
            if 'numero_ciclo_criacao' in self.fields:
                # Ciclo será preenchido via JavaScript baseado no plano selecionado
                self.fields['numero_ciclo_criacao'].widget.attrs.update({
                    'class': 'form-select',
                    'data-depends-on': 'plano_ciclo'
                })
                
                # Se há uma instância com plano, calcular ciclo atual
                if self.instance.pk and hasattr(self.instance, 'plano_ciclo') and self.instance.plano_ciclo:
                    ciclo_atual = self.instance.plano_ciclo.calcular_ciclo_atual()
                    if not self.instance.numero_ciclo_criacao:
                        self.fields['numero_ciclo_criacao'].initial = ciclo_atual

    def clean(self):
        cleaned_data = super().clean()
        plano = cleaned_data.get('plano_ciclo')
        ciclo_criacao = cleaned_data.get('numero_ciclo_criacao')
        
        if plano and ciclo_criacao:
            # Validar se o ciclo está dentro do range do plano
            if ciclo_criacao > plano.total_ciclos_plano:
                raise forms.ValidationError(
                    f'Ciclo {ciclo_criacao} excede o total de ciclos do plano '
                    f'({plano.total_ciclos_plano})'
                )
            
            if ciclo_criacao < 1:
                raise forms.ValidationError(
                    'Ciclo deve ser maior que zero'
                )
        
        return cleaned_data


class HistoricoAutomaticoMixin:
    """
    Mixin para views que precisam salvar automaticamente no histórico
    quando uma atividade é criada/editada com ciclo anterior ao atual
    """
    
    def salvar_no_historico_se_necessario(self, instance, ciclo_selecionado=None):
        """
        Verifica se deve salvar no histórico e cria/atualiza o registro automaticamente
        """
        plano_ciclo = instance.plano_ciclo
        numero_ciclo = ciclo_selecionado or instance.numero_ciclo_criacao
        
        if not plano_ciclo or not numero_ciclo:
            return None
        
        # Calcular ciclo atual do plano
        try:
            ciclo_info = plano_ciclo.calcular_ciclo_atual()
            ciclo_atual = ciclo_info['numero'] if ciclo_info else None
        except:
            return None
        
        # Se o ciclo selecionado for diferente do atual, salvar no histórico
        if numero_ciclo != ciclo_atual:
            return self._criar_ou_atualizar_historico(instance, numero_ciclo)
        
        return None
    
    def _criar_ou_atualizar_historico(self, instance, numero_ciclo):
        """
        Cria ou atualiza registro no histórico para o ciclo especificado
        """
        from .models import HistoricoCiclo
        
        plano_ciclo = instance.plano_ciclo
        owner = plano_ciclo.owner
        
        # Primeiro verificar se existe HistoricoCiclo para este ciclo
        historico_ciclo, created_historico = HistoricoCiclo.objects.get_or_create(
            owner=owner,
            configuracao=plano_ciclo,
            numero_ciclo=numero_ciclo,
            defaults={
                'data_inicio': plano_ciclo.calcular_data_inicio_ciclo(numero_ciclo),
                'data_fim': plano_ciclo.calcular_data_fim_ciclo(numero_ciclo),
            }
        )
        
        # Incrementar contador correspondente ao tipo de atividade no HistoricoCiclo
        if hasattr(instance, '_meta'):
            model_name = instance._meta.model_name
            
            if model_name == 'grupoprejovens':
                historico_ciclo.total_grupos_prejovens += 1
                historico_ciclo.novas_grupos_prejovens += 1
            elif model_name == 'aulacrianca':
                historico_ciclo.total_aulas_criancas += 1
                historico_ciclo.novas_aulas_criancas += 1
            elif model_name == 'circuloestudo':
                historico_ciclo.total_circulos_estudo += 1
                historico_ciclo.novas_circulos_estudo += 1
            elif model_name == 'grupofamilias':
                historico_ciclo.total_grupos_familias += 1
            elif model_name == 'reuniaodevocional':
                historico_ciclo.total_reunioes_devocionais += 1
                historico_ciclo.novas_reunioes_devocionais += 1
            elif model_name == 'familia':
                # Para famílias com RD ativadas, contar como RD
                if hasattr(instance, 'reuniao_devocional') and instance.reuniao_devocional:
                    historico_ciclo.total_reunioes_devocionais += 1
                    historico_ciclo.novas_familias_rds += 1
            elif model_name == 'estudoatual':
                # Para estudos, incrementamos o total de livros iniciados
                historico_ciclo.livros_iniciados += 1
                historico_ciclo.novos_livros_iniciados += 1
        
        historico_ciclo.save()
        
        if created_historico:
            print(f"✅ HistoricoCiclo criado automaticamente para ciclo {numero_ciclo}")
        else:
            print(f"✅ HistoricoCiclo atualizado para ciclo {numero_ciclo}")
        
        return historico_ciclo