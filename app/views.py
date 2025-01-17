from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from random import randint
from .models import User_Game, Friend, Ask_friend, Code_token, Support, Response, area, Game_number, Game_number_instance
from django.contrib import messages
import secrets, os
from django.conf import settings as conf
from email.mime.image import MIMEImage

@login_required(login_url="login")
def index(request):
    return render (request, 'home.html')

def accounts_login(request):
    if request.user.is_authenticated == False:
        print("NECESSITA DAS CREDENCIAIS")
        if request.method == "GET":
            return render(request, 'login.html')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                auth_login(request, user)
                return redirect('login')
            else:
                print("usuario incorreto!")
                return redirect('login')
    else:
        print("USUARIO LIBERADO")
        return render (request, 'next.html')

def accounts_login_with_code(request):
    if request.method == "GET":
        return render(request, 'login-email.html')
    else:
        if 'email' in request.POST:
            email = request.POST['email']
            if User.objects.filter(email=email):
                user_login = User.objects.get(email=email)
                codigo_login = secrets.token_hex(4)
                print(codigo_login)
                user_game = User_Game.objects.get(id=user_login.id)
                if Code_token.objects.filter(user=user_game):
                    return render(request, 'login-with-code.html')
                Code_token.objects.create(user=user_game, token=codigo_login)
                assunto = f'CODIGO PARA LOGIN'
                mensagem = f'O código para login é {codigo_login}'
                enviar_email(user_login.email, assunto, mensagem)
                return render(request, 'login-with-code.html')
        elif 'code' in request.POST:
            code = request.POST['code']
            if Code_token.objects.filter(token=code):
                code_token = Code_token.objects.get(token=code)
                print("code date: ", code_token.date)
                user_game = User_Game.objects.get(id=code_token.user.id)
                user_login = User.objects.get(id=user_game.user.id)
                if not code_token.esta_valido():
                    code_token.delete()
                    messages.error(request, "O código já foi expirado!")
                    return redirect('login-with-code')
                if user_login:
                    code_token.delete()
                    auth_login(request, user_login)
                    return redirect('login')
                else:
                    print("usuario incorreto!")
                    return redirect('login-with-code')
        return redirect('login-with-code')                

    
def accounts_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url="login")
def settings(request):
    user_game = User_Game.objects.get(id=request.user.id)
    return render (request, 'settings.html',{'link': 'silas-games.com.br', 'user_game': user_game})

@login_required(login_url="login")
def friends(request):
    user = request.user
    if request.method == "GET":
        user_game = User_Game.objects.get(user=user)
        friends = Friend.objects.filter(user=user_game.id)
        print(user_game, friends)
        return render (request, 'friends.html', {'friends': friends, 'user_game': user_game})
    else:
        print(request.POST)
        if 'delete_friend' in request.POST:
            id = request.POST.get('delete_friend')
            friend, friend2 = Friend.objects.get(id=id), Friend.objects.get(user=friend.friend, friend=friend.user)
            friend.delete()
            friend2.delete()
        if 'add_friend' in request.POST:
            code = request.POST.get('add_friend')
            print("Código: ", code)
            if User_Game.objects.filter(code=code):
                user_game = User_Game.objects.get(code=code)
                return redirect('profile', user_game.id, user_game.user)
        return redirect('friends')

def profile(request, id, username):
    print("REQUEST.POST: ",request.POST)
    user_atual = request.user
    if request.method == "GET":
        user_friend = User_Game.objects.get(id=id)
        print("EITA-ATRAS-DE-EITA: ",id, " : ", username)
        return render(request, 'profile.html', {'user_friend': user_friend})
    else:
        if 'id_user' in request.POST:
            id_user = request.POST.get('id_user')
            print(id_user)
            if User_Game.objects.filter(id=id_user).exists():
                friend_f = User_Game.objects.get(id=id_user)
                user = User_Game.objects.get(id=user_atual.id)
                if Friend.objects.filter(user=user.id,friend=friend_f.id).exists() and Friend.objects.filter(user=friend_f.id,friend=user.id).exists():
                    return HttpResponse("Vcoês já são amigos! :)")
                if not Ask_friend.objects.filter(user_game1=user.id,user_game2=friend_f.id).exists():
                    ask = Ask_friend.objects.create(user_game1=user,user_game2=friend_f)
                    ask.save()
                    a = (int(ask.date.hour) - 3)
                    if a < 0: a = 24 - a
                    destinatario = [f'{friend_f.user.email}']
                    assunto = f'O USUARIO {str(user.user).upper()} ENVIOU UMA SOLICITAÇÃO DE AMIZADE PARA VOCÊ!'
                    html_content = render_to_string('email/ask_friend.html', {'user': user.user,'data_hora': ask.date.strftime(f'%d/%m/%Y {a}:%M:%S')})
                    text_content = strip_tags(html_content)
                    email = EmailMultiAlternatives(assunto, text_content, 'silasgames.naoresponda@gmail.com', destinatario)
                    email.attach_alternative(html_content, 'text/html')
                    logo_path = os.path.join(conf.BASE_DIR, 'static', 'images', 'logo-silasgames.png')
                    if os.path.exists(logo_path):
                        with open(logo_path, 'rb') as img:
                            image = MIMEImage(img.read())
                            image.add_header('Content-ID', '<logo_silasgames>')
                            image.add_header('Content-Disposition', 'inline', filename='logo-silasgames.png')
                            email.attach(image) 
                    else:
                        print("Imagem não encontrada no caminho especificado.")
                    email.send()
                    return redirect('friends')

        return redirect('profile', id, username)

def register_user(request):
    if request.method == "GET":
        return render (request, 'admin/register_user.html')
    else:
        print("CHEGOU ISSO: ", request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        while True:
            code = randint(100000, 999999)
            if not User_Game.objects.filter(code=code).exists():
                break
        User_Game.objects.create(user=user, code=code)
        return redirect('criar')

@login_required(login_url="login")
def solicitacoes(request):
    user = request.user
    if request.method == "GET":
        pedido = Ask_friend.objects.filter(user_game2=user.id)
        print('get: ')
        print(pedido)
        return render(request, 'solicitacoes.html',{'pedido':pedido})
    else:
        print(request.POST)
        if 'friend-true' in request.POST:
            friend = request.POST.get('friend-true')
            friends = Ask_friend.objects.get(id=friend)
            user1 = User_Game.objects.get(user=friends.user_game1.user)
            user2 = User_Game.objects.get(user=friends.user_game2.user)
            if not Friend.objects.filter(user=user1, friend=user2): Friend.objects.create(user=user1, friend=user2)
            if not Friend.objects.filter(user=user2, friend=user1): Friend.objects.create(user=user2, friend=user1)
        if 'friend-false' in request.POST:
            friend = request.POST.get('friend-false')
            friends = Ask_friend.objects.get(id=friend)
        friends.delete()
        return redirect('solicitacoes')



@login_required(login_url="login")
def accounts(request):
    return HttpResponse("Conta!")

@login_required(login_url="login")
def support(request):
    user_game = User_Game.objects.get(id=request.user.id)
    if user_game.user == 'admin': support = Support.objects.all()
    else: support = Support.objects.filter(user=user_game)
    return render(request, 'settings/support.html',{'support': support})

@login_required(login_url="login")
def support_create(request):
    
    if request.method == "GET":
        return render(request, 'settings/create_support.html', {"area": area.choices})
    else:
        print(request.POST)
        title = request.POST['title']
        description = request.POST['description']
        area_s = request.POST['area_s']
        if title == '' or description == '':
            return redirect('support-create')
        while True:
            protocol = randint(0000000000, 9999999999)
            print("protocolo: ",protocol)
            if not Support.objects.filter(protocol=protocol).exists(): break
            print("aoutra")
        user_game = User_Game.objects.get(id=request.user.id)
        if area == '':support = Support.objects.create(user=user_game, protocol=protocol, title=title, description=description)
        else: support = Support.objects.create(user=user_game, protocol=protocol, title=title, description=description, area=area_s)
        
        email(support.id)
        return redirect('support')

@login_required(login_url="login")
def support_protocol(request, protocol):
    user_game = User_Game.objects.get(id=request.user.id)
    support = Support.objects.get(user=user_game,protocol=protocol)
    return render(request, 'settings/support-protocol.html',{'support': support})

@login_required(login_url="login")
def match(request):
    return HttpResponse("Partida!")


@login_required(login_url="login")
def games(request):
    return render(request, 'games-list.html')

@login_required(login_url="login")
def support_admin(request):
    support = Support.objects.all()
    return render(request, 'admin/admin-support.html',{'support': support})

@login_required(login_url="login")
def request(request):
    return HttpResponse("Solicitação!")

@login_required(login_url="login")
def about(request):
    return HttpResponse("Como posso ajudar?")

@login_required(login_url="login")
def gerador_token(request):
    user = User_Game.objects.get(id=request.user.id)
    token = secrets.token_hex(12)
    server_address = request.get_host()
    print(server_address)
    Code_token.objects.create(user=user ,token=token)
    tokene = f'{server_address}/invite-friends/{user.code}/{token}/'
    return render(request, 'admin/teste.html',{'token': tokene})

@login_required(login_url="login")
def invite_friends(request, codeuser,token):
    if User_Game.objects.filter(code=codeuser):
        user_login = request.user
        friend_f = User_Game.objects.get(code=codeuser)
        user = User_Game.objects.get(id=user_login.id)
        if Code_token.objects.filter(user=friend_f, token=token).exists():
            code_token = Code_token.objects.get(user=friend_f, token=token)
            code_token.delete()
            if not Friend.objects.filter(user=user.id,friend=friend_f.id).exists():
                Friend.objects.create(user=user, friend=friend_f)
            if not Friend.objects.filter(user=friend_f.id,friend=user.id).exists():
                Friend.objects.create(user=friend_f, friend=user)
            if Ask_friend.objects.filter(user_game1=user.id,user_game2=friend_f.id).exists():
                Ask_friend.objects.delete(user_game1=user.id,user_game2=friend_f.id)
            if Ask_friend.objects.filter(user_game2=user.id,user_game1=friend_f.id).exists():
                Ask_friend.objects.delete(user_game2=user.id,user_game1=friend_f.id)
            print(codeuser, friend_f)
            return HttpResponse("Sucesso: ", codeuser)
        else:
            return HttpResponse('Token incorreto!')
    else:
        print(codeuser)

        return HttpResponse("Sucesso: ", codeuser)
    
def criar_inivite_friends(request):
    user = User_Game.objects.get(id=request.user.id)
    token = secrets.token_hex(5)
    Code_token.objects.create(user=user,token=token)
    print(token)
    return redirect('home')



def enviaremail(request):
    if request.method == "POST":
        destinatario = request.POST['email']
        assunto = request.POST['assunto']
        mensagem = request.POST['mensagem']

        try:
            enviar_email(destinatario, assunto, mensagem)
            return HttpResponse('E-mail enviado com sucesso!')
        except Exception as e:
            return HttpResponse(f'Erro ao enviar e-mail: {e}')       
    return render(request, 'admin/enviar-email.html')

def enviar_email(destinatario, assunto, mensagem):
    send_mail(
        assunto,
        mensagem,
        'silasgames.naoresponda@gmail.com', 
        [destinatario], 
        fail_silently=False,  
    )
    print(send_mail)

def paint(request):
    return render(request, 'paint.html')

def game_sweet(request):
    return render(request, 'games/game-paint-sweet.html')

def email(id):
    support = Support.objects.get(id=id)
    assunto = f'SUPORTE SILAS GAMES'
    destinatario = [f'{support.user.user.email}']
    html_content = render_to_string('email/support.html', {'support': support})
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(assunto, text_content, 'silasgames.naoresponda@gmail.com', destinatario)
    email.attach_alternative(html_content, 'text/html')
    logo_path = os.path.join(conf.BASE_DIR, 'static', 'images', 'logo-silasgames.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            image = MIMEImage(img.read())
            image.add_header('Content-ID', '<logo_silasgames>')
            image.add_header('Content-Disposition', 'inline', filename='logo-silasgames.png')
            email.attach(image) 
    else:
        print("Imagem não encontrada no caminho especificado.")
    email.send()

def game(request):
    user_game = User_Game.objects.get(user=request.user.id)
    if request.method == "GET":
        if not Game_number.objects.filter(user=user_game, status=False).exists():
            return render(request,'game-infor.html')
        else: 
            game_number = Game_number.objects.get(user=user_game, status=False)
            return redirect('game_number', game_number.codegame, game_number.token)
    else:
        if not Game_number.objects.filter(user=user_game, status=False).exists():
            number = randint(000,99999)
            token = secrets.token_hex(16)
            codegame = randint(100000,999999)
            game_number = Game_number.objects.create(user=user_game, number=number, token=token, codegame=codegame)
        else:
            game_number = Game_number.objects.get(user=user_game, status=False)
        return redirect('game_number', game_number.codegame, game_number.token)

def game_number(request, codegame, token):
    print(request)
    user_game = User_Game.objects.get(user=request.user.id)
    if request.method == "GET":
        game_number = Game_number.objects.get(user=user_game, status=False)
        if not game_number.esta_valido():
            game_number.delete()
            print("A partida excedeu o limite de 10 minutos!")
            messages.error(request, "A partida excedeu o limite de 10 minutos!")
            return redirect('games')
        print("codegame: ",game_number.codegame, " - " ,codegame," : ","token: ",game_number.token, " - " ,token)
        print()
        if str(game_number.codegame) == str(codegame) and str(game_number.token) == str(token):
            context = {'game_number': game_number}
            if Game_number_instance.objects.filter(game=game_number, correct=False).exists():
                number_result = Game_number_instance.objects.filter(game=game_number).last()
                number_last = Game_number_instance.objects.order_by('-date')[:3]
                context = {
                    'number_result': number_result,
                    'number_last': number_last,
                }
                pass
            return render(request,'games/game-less-more.html', context)
        else:
            return redirect('game')
    else: 
        game_number = Game_number.objects.get(user=user_game, status=False)
        if str(request.user) == str(user_game.user):
            token = secrets.token_hex(16)
            game_number.token = token
            game_number.save()
            if 'exit-game' in request.POST:
                game_number.delete()
                return redirect('games')
            elif 'number_game' in request.POST:
                number =  request.POST.get('number_game')
                if int(number) == int(game_number.number):
                    less_more = "CERTO"
                    Game_number_instance.objects.create(game=game_number, number=number, less_more=less_more, correct=True)
                elif int(number) > int(game_number.number): 
                    less_more = "MENOR"
                    Game_number_instance.objects.create(game=game_number, number=number, less_more=less_more)
                elif int(number) < int(game_number.number): 
                    less_more = "MAIOR"  
                    Game_number_instance.objects.create(game=game_number, number=number, less_more=less_more)
                return redirect('game_number', game_number.codegame, game_number.token)
                
