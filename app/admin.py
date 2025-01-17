from django.contrib import admin
from .models import Friend, User_Game, Ask_friend, Code_token, Support, Response, Game_number, Game_number_instance
# Register your models here.

@admin.register(User_Game)
class User_GameAdmin(admin.ModelAdmin):
    list_display = ('id','user','code')
    search_fields = ('id','user','code')

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('id','user','friend','date')
    search_fields = ('id','user','friend','date')

@admin.register(Code_token)
class Code_tokenAdmin(admin.ModelAdmin):
    list_display = ('id','user','token','date')
    search_fields = ('id','user','token','date')

@admin.register(Ask_friend)
class Ask_friendAdmin(admin.ModelAdmin):
    list_display = ('id','user_game1','user_game2','date')
    search_fields = ('id','user_game1','user_game2','date')

@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('id','user','protocol','title','status','area','date')
    search_fields = ('id','user','protocol','title','status','area','date')

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id','user','support','response','date')
    search_fields = ('id','user','support','response','date')

@admin.register(Game_number)
class Game_numberAdmin(admin.ModelAdmin):
    list_display = ('id','user','codegame','status','token','date')
    search_fields = ('id','user','codegame','status','token','date')


@admin.register(Game_number_instance)
class Game_number_instanceAdmin(admin.ModelAdmin):
    list_display = ('id','game','number','less_more','date')
    search_fields = ('id','game','number','less_more','date')