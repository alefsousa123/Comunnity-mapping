from django.urls import path
from contact import views
from contact.views import family_views

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
]
