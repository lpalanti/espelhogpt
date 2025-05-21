import os
import json
import openai
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.auth.credentials import Credentials

# Configuração da API do ChatGPT
openai.api_key = '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'

# Escopos necessários para acessar o Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Recuperando o conteúdo do 'client_secret.json' da variável de ambiente
client_secret_json = os.getenv('GOOGLE_CLIENT_SECRET')

# Verifique se a variável de ambiente foi configurada
if not client_secret_json:
    st.error("A variável de ambiente GOOGLE_CLIENT_SECRET não está configurada!")
    st.stop()

# Converta o conteúdo da variável de ambiente para um dicionário
client_secret_dict = json.loads(client_secret_json)

# Função de login com o Google
def login_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_secret_dict, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

# Função para acessar os e-mails do Gmail
def mostrar_emails(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])
    
    if not messages:
        st.write('Nenhuma nova mensagem.')
    else:
        st.write('Novas mensagens:')
        for message in messages[:5]:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            st.write(f"Assunto: {msg['snippet']}")

# Função de interação com o ChatGPT
def get_chatgpt_response(prompt):
    response = openai.Completion.create(
        engine="gpt-4",  # ou gpt-3.5-turbo
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Interface Streamlit
st.title("ChatGPT com Google OAuth 2.0")

if st.button('Login com Gmail'):
    try:
        service = login_gmail()
        mostrar_emails(service)
    except Exception as e:
        st.write("Erro durante a autenticação:", e)

user_input = st.text_input("Digite sua pergunta para o ChatGPT:")

if user_input:
    response = get_chatgpt_response(user_input)
    st.write("Resposta do ChatGPT:")
    st.write(response)

