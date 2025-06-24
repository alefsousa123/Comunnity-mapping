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
