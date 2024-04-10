import os
import requests
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

app = Flask(__name__)

@app.route("/")
def home():
  return render_template('home.html')

@app.route("/sobremim")
def sobre_mim():
  return render_template('sobremim.html')

@app.route("/portfolio")
def portfolio():
  return render_template('portfolio.html')

@app.route("/contato")
def contato():
  return render_template('contato.html')

@app.route("/dou")
def dou():
    palavras_chave = ['Comunicação', 'Jornalista', 'Imprensa']
    page = requests.get('https://www.in.gov.br/leiturajornal')
    soup = BeautifulSoup(page.text, 'html.parser')
    conteudo = json.loads(soup.find("script", {"id": "params"}).string)
    URL_BASE = 'https://www.in.gov.br/en/web/dou/-/'

    resultados_por_palavra = {palavra: [] for palavra in palavras_chave}
    nenhum_resultado_encontrado = True  # Inicializa como True, nenhum resultado encontrado até agora

    for resultado in conteudo['jsonArray']:
        item = {}
        item['section'] = 'Seção 1'
        item['title'] = resultado['title']
        item['href'] = URL_BASE + resultado['urlTitle']
        item['abstract'] = resultado['content']
        item['date'] = resultado['pubDate']

        for palavra in palavras_chave:
            if palavra.lower() in item['abstract'].lower():
                resultados_por_palavra[palavra].append(item)
                nenhum_resultado_encontrado = False  # Define como False quando ao menos um resultado é encontrado

    # Se nenhum resultado foi encontrado, renderiza a página dou-vazio
    if nenhum_resultado_encontrado:
        data_atual = datetime.today()
        data_formatada = data_atual.strftime("%d/%m/%Y")
        return render_template('dou-vazio.html', data_formatada=data_formatada)

    # Passamos a primeira data encontrada para o template para exibir
    date = resultados_por_palavra[palavras_chave[0]][0]['date']

    return render_template('dou.html', resultados_por_palavra=resultados_por_palavra, date=date)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/enviaemail', methods=['POST'])
def envia_email():
    smtp_server = "smtp-relay.brevo.com"
    port = 587
    email = "heloisav.x@gmail.com"  # MUDE AQUI
    password = os.getenv('CHAVE_EMAIL')

    remetente = request.form['email']
    destinatario = ["heloisav.x@gmail.com", 'alvarojusten@gmail.com']
    titulo = request.form['titulo']
    corpo = request.form['corpo']

    server = smtplib.SMTP(smtp_server, port)  # Inicia a conexão com o servidor
    server.starttls()  # Altera a comunicação para utilizar criptografia
    server.login(email, password)  # Autentica

    # Preparando o objeto da mensagem ("documento" do email):
    mensagem = MIMEMultipart()
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem["Subject"] = titulo

    # Adicionando o corpo do e-mail como parte da mensagem
    mensagem.attach(MIMEText(corpo, 'plain'))

    # Enviando o email pela conexão já estabelecida:
    server.sendmail(remetente, destinatario, mensagem.as_string())
    server.quit()  # Encerrar a conexão com o servidor SMTP
    return 'E-mail enviado'

if __name__ == "__main__":
    app.run(debug=True)
