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
