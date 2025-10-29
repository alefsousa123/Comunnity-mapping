from django.contrib import admin
from contact import models


class ContactInline(admin.TabularInline):
    model = models.Contact
    extra = 0


@admin.register(models.Rua)
class RuaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(models.Familia)
class FamiliaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "rua",
        "endereco",
        "reuniao_devocional",
        "data_ultima_reuniao",
        "nivel_envolvimento",
    )
    search_fields = ("nome", "endereco")
    list_filter = ("rua", "reuniao_devocional")
    inlines = [ContactInline]


# Register your models here.
@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "familia",
        "birth_date",
        "age",
        "age_group",
        "rua",
    )
    search_fields = ("first_name", "last_name")
    list_filter = ("familia",)
    ordering = ("-id",)


# Novos models
@admin.register(models.GrupoPreJovens)
class GrupoPreJovensAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "rua", "livro", "data_ultimo_encontro", "dia_semana")
    search_fields = ("nome", "livro", "descricao")
    list_filter = ("rua", "dia_semana")
    filter_horizontal = ("pre_jovens",)


@admin.register(models.AulaCrianca)
class AulaCriancaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "rua", "serie", "licao", "professor", "data_ultima_aula", "dia_semana")
    search_fields = ("nome", "serie", "licao", "descricao")
    list_filter = ("rua", "dia_semana")
    filter_horizontal = ("participantes",)


@admin.register(models.GrupoFamilias)
class GrupoFamiliasAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_participantes', 'description', 'owner', 'show')
    search_fields = ("nome",)
    filter_horizontal = ("participantes", "ruas")

    def get_participantes(self, obj):
        return ", ".join([str(p) for p in obj.participantes.all()])
    get_participantes.short_description = "Participantes"


@admin.register(models.CirculoEstudo)
class CirculoEstudoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "tutor", "livro", "unidade", "secao", "data_ultimo_encontro", "dia_semana")
    search_fields = ("nome", "livro", "unidade", "secao")
    list_filter = ("dia_semana",)
    filter_horizontal = ("participantes",)


@admin.register(models.CategoriaLivro)
class CategoriaLivroAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "created_at")
    search_fields = ("nome",)
    list_filter = ("created_at",)


@admin.register(models.Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "categoria", "created_at")
    search_fields = ("titulo",)
    list_filter = ("categoria", "created_at")


@admin.register(models.EstudoAtual)
class EstudoAtualAdmin(admin.ModelAdmin):
    list_display = ("id", "contato", "livro", "status", "data_inicio")
    search_fields = ("contato__first_name", "contato__last_name", "livro__titulo")
    list_filter = ("status", "livro__categoria", "data_inicio")


@admin.register(models.ConfiguracaoEstatisticas)
class ConfiguracaoEstatisticasAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo_plano", "data_inicio_plano", "ativo", "created_at")
    search_fields = ("titulo_plano",)
    list_filter = ("ativo", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.EstatisticasEditaveis)
class EstatisticasEditaveisAdmin(admin.ModelAdmin):
    list_display = ("id", "total_participantes", "total_participantes_bahais", "updated_at")
    list_filter = ("updated_at",)
    readonly_fields = ("total_participantes", "total_participantes_bahais")


@admin.register(models.ReuniaoDevocional)
class ReuniaoDevocionalAdmin(admin.ModelAdmin):
    list_display = ("nome", "rua", "numero_participantes", "ativa", "dia_semana", "created_at")
    search_fields = ("nome", "descricao", "local_detalhes")
    list_filter = ("ativa", "frequencia", "dia_semana", "created_at")
    readonly_fields = ("created_at", "updated_at")
