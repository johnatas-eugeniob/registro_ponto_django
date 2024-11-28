from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_qrcode, name='login_qrcode'),
    path('login/', views.login, name='login'),
    path('login_text/', views.login_text, name='login_text'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('marcador/', views.marcador, name='marcador'),
    #path('minhas_marcações/', views.minha_marcacao, name='marcações'),
    #path('filtrar_data/', views.filtro_de_data, name='filtrar_data'),
    path('exportar/', views.exportar, name='exportar'),
    path('logout/', views.logout, name='logout'),
    #path('em_manutencao/', views.em_manutencao, name='em_manutencao'),
]