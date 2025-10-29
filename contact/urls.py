from django.urls import path
from django.shortcuts import render
from contact import views
from contact.views import family_views, abc_views, junior_youth_views, study_circle_views, family_group_views, livro_views, statistics_views, historico_views, cycle_views

from contact.views.abc_views import abc_update


def teste_ciclos_view(request):
    return render(request, 'global/teste_ciclos.html')

app_name = "contact"

urlpatterns = [
    # CRUD URLs
    path("contact/create/", views.create, name="create"),
    path("contact/<int:contact_id>/", views.contact, name="contact"),
    path("contact/<int:contact_id>/update/", views.update, name="update"),
    path("contact/<int:contact_id>/delete/", views.delete, name="delete"),

    # User 
    path("user/register", views.register, name="register"),
    path("user/login", views.login_view, name="login"),
    path("user/logout", views.logout_view, name="logout"),
    path("user/profile", views.profile, name="profile"),

    # ... outras rotas ...
    path("rua/create/", views.rua_create, name="rua_create"),
    path("familia/create/", views.familia_create, name="familia_create"),
    path('familia/<int:familia_id>/', views.familia_detail, name='familia_detail'),
    path('familia/<int:familia_id>/edit/', views.familia_update, name='familia_update'),
    path('familia/<int:familia_id>/delete/', views.familia_delete, name='familia_delete'),
    path("familia/list/", views.family, name="family"),

    # Search URL
    path("search/", views.search, name="search"),
    path('search/familias/', views.search_familias, name='search_familias'),
    path('search/ruas/', views.search_ruas, name='search_ruas'),

    # Index URL
    path("", views.index, name="index"),
    path('rua/<int:rua_id>/edit/', views.rua_update, name='rua_update'),
    path('rua/<int:rua_id>/delete/', views.rua_delete, name='rua_delete'),
    path('rua/<int:rua_id>/', views.rua_detail, name='rua_detail'),
    path('ruas/', views.ruas_list, name='ruas_list'),

    # Marcar Visitado
    path('familia/<int:familia_id>/marcar_visitado/', family_views.marcar_visitado, name='marcar_visitado'),

    #Grupos de Famílias URLs
    path('grupos-familias/', family_group_views.family_group_list, name='grupofamilias_list'),
    path('grupos-familias/<int:pk>/', family_group_views.family_group_detail, name='grupofamilias_detail'),
    path('grupos-familias/criar/', family_group_views.family_group_create, name='grupofamilias_create'),
    path('grupos-familias/<int:pk>/editar/', family_group_views.family_group_update, name='grupofamilias_update'),
    path('grupos-familias/<int:pk>/deletar/', family_group_views.family_group_delete, name='grupofamilias_delete'),

    # Aulas Bahá'í de Crianças (ABC)
    path('abc/', abc_views.abc_list, name='aulacrianca_list'),
    path('abc/<int:pk>/', abc_views.abc_detail, name='aulacrianca_detail'),
    path('abc/criar/', abc_views.abc_create, name='aulacrianca_create'),
    path('abc/<int:pk>/editar/', abc_update, name='aulacrianca_update'),
    path('abc/<int:pk>/deletar/', abc_views.abc_delete, name='aulacrianca_delete'),

    # Grupos de Pré-Jovens
    path('junior-youth/', junior_youth_views.junior_youth_list, name='grupoprejovens_list'),
    path('junior-youth/<int:pk>/', junior_youth_views.junior_youth_detail, name='grupoprejovens_detail'),
    path('junior-youth/criar/', junior_youth_views.junior_youth_create, name='grupoprejovens_create'),
    path('junior-youth/<int:pk>/editar/', junior_youth_views.junior_youth_update, name='grupoprejovens_update'),
    path('junior-youth/<int:pk>/deletar/', junior_youth_views.junior_youth_delete, name='grupoprejovens_delete'),

    # Study Circle URLs
    path('study-circle/', study_circle_views.study_circle_list, name='circuloestudo_list'),
    path('study-circle/<int:pk>/', study_circle_views.study_circle_detail, name='circuloestudo_detail'),
    path('study-circle/criar/', study_circle_views.study_circle_create, name='circuloestudo_create'),
    path('study-circle/<int:pk>/editar/', study_circle_views.study_circle_update, name='circuloestudo_update'),
    path('study-circle/<int:pk>/deletar/', study_circle_views.study_circle_delete, name='circuloestudo_delete'),

    # Livros Ruhi URLs
    path('livros/', livro_views.livro_list, name='livro_list'),
    path('livros/criar/', livro_views.livro_create, name='livro_create'),
    path('livros/criar-rapido/', livro_views.livro_create_quick, name='livro_create_quick'),
    path('livros/<int:pk>/', livro_views.livro_detail, name='livro_detail'),
    path('livros/<int:pk>/editar/', livro_views.livro_edit, name='livro_edit'),
    path('livros/<int:pk>/excluir/', livro_views.livro_delete, name='livro_delete'),
    path('contatos/<int:contato_id>/estudos/', livro_views.contato_estudos, name='contato_estudos'),
    path('contatos/<int:contato_id>/gerenciar-estudos/', livro_views.gerenciar_estudos, name='gerenciar_estudos'),
    path('contatos/<int:contato_id>/atribuir-livro/', livro_views.atribuir_livro, name='atribuir_livro'),
    path('contatos/<int:contato_id>/estudo-action/', livro_views.quick_action_estudo, name='quick_action_estudo'),

    # Categorias de Livros URLs
    path('categorias/', livro_views.categoria_list, name='categoria_list'),
    path('categorias/criar/', livro_views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', livro_views.categoria_edit, name='categoria_edit'),
    path('categorias/<int:pk>/excluir/', livro_views.categoria_delete, name='categoria_delete'),

    # Estatísticas URLs
    path('estatisticas/', statistics_views.dashboard_estatisticas, name='dashboard_estatisticas'),
    path('estatisticas/configuracao/', statistics_views.editar_configuracao, name='editar_configuracao'),
    path('estatisticas/historico/', statistics_views.historico_ciclos, name='historico_ciclos'),
    path('estatisticas/historico/<int:numero_ciclo>/', statistics_views.historico_ciclo_detalhado, name='historico_ciclo_detalhado'),
    path('estatisticas/editar/', statistics_views.editar_estatisticas, name='editar_estatisticas'),
    path('estatisticas/salvar-inline/', statistics_views.salvar_atividades_inline, name='salvar_atividades_inline'),
    path('estatisticas/encerrar-ciclo/', statistics_views.encerrar_ciclo_atual, name='encerrar_ciclo_atual'),

    # Histórico de Ciclos URLs
    path('historico/', historico_views.gerenciar_historico, name='gerenciar_historico'),
    path('historico/criar/<int:numero_ciclo>/', historico_views.criar_historico, name='criar_historico'),
    path('historico/excluir/<int:historico_id>/', historico_views.excluir_historico, name='excluir_historico'),
    path('historico/<int:historico_id>/detalhes/', historico_views.detalhes_historico, name='detalhes_historico'),
    path('historico/<int:historico_id>/atualizar-sistema/', historico_views.atualizar_dados_sistema_historico, name='atualizar_dados_sistema_historico'),
    path('historico/atualizar-todos-sistema/', historico_views.atualizar_todos_dados_sistema, name='atualizar_todos_dados_sistema'),
    
    # Teste de formulário
    path('test-form/', lambda request: __import__('test_views').test_form_view(request), name='test_form'),
    
    # Teste de ciclos
    path('teste-ciclos/', teste_ciclos_view, name='teste_ciclos'),

    # Statistics URLs (compatibilidade)
    path('statistics/', statistics_views.dashboard_estatisticas, name='statistics_dashboard'),

    # URLs para gerenciamento de ciclos
    path('ciclos/', cycle_views.gerenciar_planos_ciclos, name='gerenciar_planos_ciclos'),
    path('ciclos/criar/', cycle_views.criar_plano_ciclo, name='criar_plano_ciclo'),
    path('ciclos/plano/<int:plano_id>/editar/', cycle_views.editar_plano_ciclo, name='editar_plano_ciclo'),
    path('ciclos/plano/<int:plano_id>/excluir/', cycle_views.excluir_plano_ciclo, name='excluir_plano_ciclo'),
    path('ciclos/plano/<int:plano_id>/alternar-principal/', cycle_views.alternar_plano_principal, name='alternar_plano_principal'),
    path('ciclos/plano/<int:plano_id>/info/', cycle_views.obter_info_plano, name='obter_info_plano'),
    path('ciclos/plano/<int:plano_id>/info-teste/', cycle_views.obter_info_plano_teste, name='obter_info_plano_teste'),
    path('ciclos/plano/<int:plano_id>/ciclos/', cycle_views.obter_ciclos_plano, name='obter_ciclos_plano'),

    # Participante Autocomplete
    
]
