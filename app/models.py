from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

class User_Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"Usuário: {self.user} | Código: {self.code}"
    
    class Meta:
        verbose_name = 'Usuario'

class Friend(models.Model):
    user = models.ForeignKey(User_Game, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(User_Game, on_delete=models.CASCADE, related_name='friend')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usuário: {self.user} | Amigo: {self.friend} | Data: {self.date}"

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['user', 'friend'], name='unique_friendship')
        ]

class Ask_friend(models.Model):
    user_game1 = models.ForeignKey(User_Game, on_delete=models.CASCADE, related_name='friend1')
    user_game2 = models.ForeignKey(User_Game, on_delete=models.CASCADE, related_name='friend2')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usuário 1: {self.user_game1} | Usuário 2: {self.user_game2} | Data: {self.date}"

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['user_game1', 'user_game2'], name='unique_friend1')
        ]

class Code_token(models.Model):
    user = models.ForeignKey(User_Game, on_delete=models.CASCADE)
    token = models.CharField(max_length=24)
    date = models.DateTimeField(default=now)

    def __str__(self):
        return f"Usuário: {self.user} | token: ******** | Data: {self.date}"
    
    def esta_valido(self):
        return now() <= self.date + timedelta(minutes=15)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_one1')
        ]

class status(models.IntegerChoices):
    progress = 0, "Em andamento"
    finashed = 1, "Finalizado"

class area(models.IntegerChoices):
    login = 0, "Login"
    account = 1, "Conta"
    game = 2, "Jogo"
    pageNotFound = 3, "Pagina não encontrada"
    Ask_friend = 4, "Solicitação de amizade"
    others = 5, "Outros"
    
class Support(models.Model):
    user = models.ForeignKey(User_Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=300)
    date = models.DateTimeField(default=now)
    status = models.IntegerField(choices=status.choices, default=status.progress)
    protocol = models.CharField(max_length=10, unique=True)
    area = models.IntegerField(choices=area.choices, default=area.others)

    def __str__(self):
        return f"{self.user.user}  |  {self.protocol}"

class Response(models.Model):
    user = models.ForeignKey(User_Game, on_delete=models.CASCADE)
    support = models.ForeignKey(Support, on_delete=models.CASCADE)
    response = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user} | {self.support.protocol} | {self.date}"
    
class Game_number(models.Model):
    user = models.ForeignKey(User_Game, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    token = models.CharField(max_length=32, unique=True)
    codegame = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(default=now)
    tentative = models.IntegerField(default=10)
    correct = models.BooleanField(default=False)

    def esta_valido(self):
        return now() <= self.date + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.user} | {self.codegame} | {self.status} | {self.date}"

class Game_number_instance(models.Model):
    game = models.ForeignKey(Game_number, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    less_more = models.CharField(max_length=5)
    correct = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game} | {self.number} | {self.less_more} | {self.date}"