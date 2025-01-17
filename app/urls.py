from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('settings/accounts/login', views.accounts_login, name="login"),
    path('settings/accounts/login-with-code', views.accounts_login_with_code, name="login-with-code"),
    path('settings/accounts/logout', views.accounts_logout, name="logout"),
    path('settings/accounts', views.accounts, name="accounts"),
    path('settings/match', views.match, name="match"),
    path('settings/request', views.request, name="request"),
    path('settings/about', views.about, name="about"),
    path('support', views.support, name="support"),
    path('support/<int:protocol>/', views.support_protocol, name="support-protocol"),
    path('support/create/', views.support_create, name="support-create"),
    path('settings/', views.settings, name="settings"),
    path('games/', views.games, name="games"),
    path('game', views.game, name="game"),
    path('friends/', views.friends, name="friends"),

    path('invite-friends/<str:codeuser>/<str:token>/', views.invite_friends),
    path('criar/', views.register_user, name="criar"),
    path('solicitacoes/', views.solicitacoes, name="solicitacoes"),
    path('profile/<int:id>/<str:username>/', views.profile, name="profile"),

    path('teste/token', views.gerador_token, name="teste"),
    path('paint/', views.paint, name="paint"),
    path('enviar-email/', views.enviaremail, name="enviar-email"),
    path('criar-token/', views.criar_inivite_friends, name="criar-token"),
    path('admin/support', views.support_admin, name="support-admin"),

    path('game/number-less-more/<int:codegame>/<str:token>/', views.game_number, name="game-number"),
    path('game/paint-sweet', views.game_sweet, name="game-sweet"),
]