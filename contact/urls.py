from django.urls import path
from contact import views
from contact.views import family_views, abc_views, junior_youth_views, study_circle_views, family_group_views

from contact.views.abc_views import abc_update

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

    # Participante Autocomplete
    
]
