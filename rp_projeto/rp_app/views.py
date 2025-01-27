from django.shortcuts import render

# Create your views here.
import requests
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.utils.translation import gettext as _
from django.http import HttpResponseForbidden
from django.db import IntegrityError
from .models import HorasMarcadas

# Create your views here.
def login_text(request):
    return render(request, 'login_text.html')
#-----------------------------------------------------------------------------------------------------------------------
def login(request):
    if request.method == "POST":
        username = request.POST.get('name')
        senha = request.POST.get('senha')
        user_login = authenticate(username=username, password=senha)
        if user_login is not None and user_login.is_staff == True:
            login_django(request, user_login)
            return render(request, 'exportar.html')
        else:
            messages.error(request, "Nome ou Senha inválidos")
            return render(request, 'login_text.html')
    else:
        return HttpResponse('Recarregue a página e tente novamente')
#-----------------------------------------------------------------------------------------------------------------------            

def login_qrcode(request):
    #credenciais
    username_api = "gestao_qualidade"
    password_api = "tj3hSmf7oxKmDinhwjX6wnZf1Gc"
    scope = "qr"

    if request.method == "POST":
        username = request.POST.get('username')

        # Lógica de login
        if username:
            #Se encontrar o mesmo user vindo da variavel "username" prossegue
            user = User.objects.filter(username=username).first()
            if user:
                login_django(request, user)
                return redirect('dashboard')
            else:
                #Caso não encontre um User com a matricula inserida no "username" tente!
                try:
                    #auth da API
                    auth_url = "https://api.pessoas.loggi.com/v1/token"
                    auth_payload = {
                        'username': username_api,
                        'password': password_api,
                        'scope': scope
                    }

                    # Auth para gerar o token com lib "requests"
                    auth_response = requests.post(auth_url, data=auth_payload, timeout=10)

                    #Caso retorne 200 que é sucesso, siga com a lógica
                    if auth_response.status_code == 200:
                        auth_data = auth_response.json()
                        #armazena o token de acesso dentro da variavel
                        access_token = auth_data.get('access_token')

                        if access_token:
                            # Agora faz a chamada para a API que retorna o nome e email
                            api_url = f"https://api.pessoas.loggi.com/v1/s3/qr_code?qr_token={username}"
                            headers = {
                                'Authorization': f'Bearer {access_token}',
                            }

                            api_response = requests.get(api_url, headers=headers, timeout=10)

                            if api_response.status_code == 200:
                                api_data = api_response.json()

                                # Acessa o obj data onde estão o nome e email
                                data = api_data.get('data', {})

                                # Recebe nome e email dentro do objeto Data
                                nome = data.get('name', 'N/A').title().strip() #Formatação de escrita EX:"Robson Santos Cunha" e o .strip é para cancelar espaços no final da string
                                email = data.get('email', 'N/A').lower() #Formatação de escrita para email, EX: "bababa@gmail.com"

                                messages.success(request, f"Email: {email}")

                                user = User.objects.create_user(username=username, first_name=nome, email=email, password='1a2s2s3d')
                                user.save()

                                exportar_para_novos_users(request, user)  # Passar o usuário recém-criado

                                messages.success(request, 'Usuário cadastrado, faça o scan novamente')
                                return redirect('login_qrcode')
                            else:
                                messages.error(request, f"Erro: {api_response.status_code}")
                        else:
                            messages.error(request, f"Erro: {api_response.status_code}")
                    else:
                        messages.error(request, f"Autenticação falhou. Status code: {auth_response.status_code}")
                #Except do try        
                except IntegrityError:
                    messages.success(request, 'Usuário já cadastrado, faça o scan novamente')
                    return redirect('login_qrcode')
        else:
            return HttpResponse('QR Code inválido')
    else:
        return render(request, 'login_qrcode.html')

 #-----------------------------------------------------------------------------------------------------------------------   

@login_required(login_url="/")
def dashboard(request):
        return render(request, 'dashboard.html')

#-----------------------------------------------------------------------------------------------------------------------
#MARCADOR
def marcador(request):
    if request.method == "POST":
        tipo = request.POST.get('choice_tipo')
        para_onde = request.POST.get('choice_para_onde')
        justificativa = request.POST.get('choice_just')

        if tipo and para_onde and justificativa:
            usuario = request.user         
            marcar = HorasMarcadas(
                nome_marcador = request.user,
                hora_marcada = timezone.now(),
                tipo = tipo,
                para_onde = para_onde,
                justificativa = justificativa
            )
            marcar.save()
            messages.success(request, 'Marcação feita com sucesso!')
            
            # Chama a função de exportação para o Google Sheets
            exportar_para_google_sheets(request)

            return redirect('logout')
        else:
            messages.error(request,"Preencha todos os campos para proseguir!")
            return render(request, 'dashboard.html')
    else:
        messages.error(request,"Envie o formulario novamente")
        return  render(request, 'dashboard.html')
    
#-----------------------------------------------------------------------------------------------------------------------

#@login_required(login_url="/")
#def minha_marcacao(request):
    # Buscar todas as marcações do usuário logado com um limite de 5
    usuario = request.user
    pontos = HorasMarcadas.objects.filter(nome_marcador=usuario).order_by('-hora_marcada')

    # Organizar as marcações por data
    dados = {}
    for ponto in pontos:
        data = ponto.hora_marcada.date()
        if data not in dados:
            dados[data] = []
        dados[data].append(ponto)

    return render(request, 'minha_marcacao.html', {'dados': dados})

#-----------------------------------------------------------------------------------------------------------------------

#@login_required(login_url="/")
#def filtro_de_data(request):
    data = request.GET.get('data')
    usuario = request.user
    if data:
        pontos = HorasMarcadas.objects.filter(nome_marcador=usuario, hora_marcada__date=data).order_by('-hora_marcada')
    else:
        pontos = HorasMarcadas.objects.filter(nome_marcador=usuario).order_by('-hora_marcada')[:5]

    dados = {}
    for ponto in pontos:
        data = ponto.hora_marcada.date()
        if data not in dados:
            dados[data] = []
        dados[data].append(ponto)

    return render(request, 'minha_marcacao.html', {'dados': dados})

#-----------------------------------------------------------------------------------------------------------------------

@login_required(login_url="/")
def logout(request):
    auth_logout(request)
    return redirect('login_qrcode')
#-----------------------------------------------------------------------------------------------------------------------
def exportar_para_novos_users(request, new_user):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cred_path = os.path.join(BASE_DIR, 'static', 'cred.json')
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1t07F1k_lgrsc-7K9hRWyiaCgX5hoj7wj-2CuDoY15-o/edit?usp=sharing')
    
    # Nome da aba que você deseja usar
    aba_name = 'novos_users'  # Altere isso para o nome da aba que você deseja
    sheet_new_users = spreadsheet.worksheet(aba_name)

    # Preparar os dados para inserir uma nova linha
    nova_linha = [
        new_user.username,
        new_user.first_name,
        new_user.email
    ]

    # Obtém o índice da próxima linha vazia
    next_row = len(sheet_new_users.get_all_values()) + 1  # Use sheet_new_users aqui
    sheet_new_users.insert_row(nova_linha, next_row)

#-----------------------------------------------------------------------------------------------------------------------

def exportar_para_google_sheets(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cred_path = os.path.join(BASE_DIR, 'static', 'cred.json')
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1t07F1k_lgrsc-7K9hRWyiaCgX5hoj7wj-2CuDoY15-o/edit?usp=sharing')
    sheet = spreadsheet.sheet1

    # Buscar apenas as últimas duas marcações do usuário (Entrada e Saída)
    marcacoes = HorasMarcadas.objects.filter(nome_marcador=request.user).order_by('-hora_marcada')[:1]

    for marcacao in marcacoes:

        email = marcacao.nome_marcador.email

        # Preparar os dados para inserir uma nova linha
        nova_linha = [
            marcacao.nome_marcador.first_name,
            email,
            marcacao.nome_marcador.username,
            marcacao.tipo,
            marcacao.hora_marcada.strftime("%d/%m/%Y"),
            marcacao.hora_marcada.strftime("%H:%M:%S"),
            marcacao.para_onde,
            marcacao.justificativa
        ]

        # Obtém o índice da próxima linha vazia
        next_row = len(sheet.get_all_values()) + 1
        sheet.insert_row(nova_linha, next_row)

#-----------------------------------------------------------------------------------------------------------------------

@login_required(login_url="/")
def exportar(request):
    return render(request, 'exportar.html')

#-----------------------------------------------------------------------------------------------------------------------
def csrf_failure(request, reason=""):
    context = {
        'message': _("A security error occurred. Please try again."),
        'reason': reason
    }
    return HttpResponseForbidden(render(request, 'dashboard.html', context))
#-----------------------------------------------------------------------------------------------------------------------
#def em_manutencao(request):
    return render(request, 'manutencao.html')
