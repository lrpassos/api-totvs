from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

@app.get("/artigos-totvs-compras", response_class=HTMLResponse)
def ler_artigos_para_notebooklm():
    url_totvs = "https://centraldeatendimento.totvs.com/api/v2/help_center/pt-br/sections/360011518754/articles.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    resposta = requests.get(url_totvs, headers=headers)
    dados = resposta.json()
    artigos = dados.get("articles", [])
    
    html_content = """
    <html>
        <head>
            <title>Base de Conhecimento TOTVS - Compras</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>Artigos de Compras - TOTVS</h1>
    """
    
    for artigo in artigos:
        titulo = artigo.get("name", "Sem título")
        corpo = artigo.get("body", "") 
        link = artigo.get("html_url", "#")
        
        html_content += f"""
        <article style="margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #ccc;">
            <h2><a href="{link}">{titulo}</a></h2>
            <div>{corpo}</div>
        </article>
        """
        
    html_content += "</body></html>"
    return HTMLResponse(content=html_content)