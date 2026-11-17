from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests

app = FastAPI(title="Conector Base de Conhecimento TOTVS")

URL_TOTVS = "https://centraldeatendimento.totvs.com/api/v2/help_center/pt-br/sections/360011518754/articles.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def formatar_data(data_iso: str | None) -> str:
    """Converte a data ISO da API do Zendesk para o padrão brasileiro."""
    if not data_iso:
        return "Data não informada"
    try:
        dt = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return data_iso


@app.get("/artigos-totvs-compras", response_class=HTMLResponse)
def ler_artigos_para_notebooklm() -> HTMLResponse:
    try:
        resposta = requests.get(URL_TOTVS, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.RequestException as erro:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao consultar a Central de Atendimento TOTVS: {erro}",
        )

    artigos = dados.get("articles", [])
    indice_html: list[str] = []
    cards_html: list[str] = []

    for idx, artigo in enumerate(artigos, start=1):
        artigo_id = artigo.get("id", idx)
        titulo = artigo.get("name", "Sem título")
        corpo = artigo.get("body", "<p>Conteúdo indisponível.</p>")
        link = artigo.get("html_url", "#")
        atualizado_em = formatar_data(artigo.get("updated_at"))

        # Item do índice rápido no topo
        indice_html.append(
            f'<li><a href="#artigo-{artigo_id}">{idx}. {titulo}</a></li>'
        )

        # Card individual do artigo
        cards_html.append(f"""
        <article id="artigo-{artigo_id}" class="card">
            <header class="card-header">
                <div class="meta">
                    <span class="badge">Artigo #{idx}</span>
                    <span class="date">Atualizado em: {atualizado_em}</span>
                </div>
                <h2><a href="{link}" target="_blank" rel="noopener noreferrer">{titulo}</a></h2>
            </header>
            <div class="article-body">
                {corpo}
            </div>
        </article>
        """)

    html_final = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base de Conhecimento TOTVS - Compras</title>
    <style>
        :root {{
            --bg-page: #f3f5f8;
            --bg-card: #ffffff;
            --primary: #006699;
            --primary-hover: #004c73;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --border: #e5e7eb;
        }}

        * {{
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            line-height: 1.65;
        }}

        .top-bar {{
            background: linear-gradient(135deg, #004c73 0%, #0077b3 100%);
            color: #ffffff;
            padding: 36px 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        .top-bar h1 {{
            margin: 0 0 8px 0;
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        .top-bar p {{
            margin: 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }}

        .container {{
            max-width: 880px;
            margin: 32px auto;
            padding: 0 20px;
        }}

        .toc {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            border-radius: 8px;
            padding: 20px 24px;
            margin-bottom: 32px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }}

        .toc h3 {{
            margin: 0 0 12px 0;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-muted);
        }}

        .toc ul {{
            margin: 0;
            padding-left: 18px;
            columns: 1;
        }}

        .toc li {{
            margin-bottom: 6px;
        }}

        .toc a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }}

        .toc a:hover {{
            text-decoration: underline;
            color: var(--primary-hover);
        }}

        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 28px 32px;
            margin-bottom: 28px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        }}

        .card-header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}

        .meta {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
            font-size: 0.82rem;
        }}

        .badge {{
            background-color: #e0f2fe;
            color: var(--primary);
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 999px;
        }}

        .date {{
            color: var(--text-muted);
        }}

        .card-header h2 {{
            margin: 0;
            font-size: 1.35rem;
            line-height: 1.35;
        }}

        .card-header h2 a {{
            color: var(--text-main);
            text-decoration: none;
        }}

        .card-header h2 a:hover {{
            color: var(--primary);
        }}

        /* Normalização do HTML interno vindo do Zendesk */
        .article-body img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid var(--border);
            margin: 12px 0;
            display: block;
        }}

        .article-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 0.92rem;
            display: block;
            overflow-x: auto;
        }}

        .article-body th,
        .article-body td {{
            border: 1px solid var(--border);
            padding: 8px 12px;
            text-align: left;
        }}

        .article-body pre,
        .article-body code {{
            background-color: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 0.88rem;
            overflow-x: auto;
        }}

        .article-body pre {{
            padding: 12px;
        }}

        @media print {{
            body {{ background: #fff; }}
            .card {{ box-shadow: none; break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <header class="top-bar">
        <h1>Base de Conhecimento TOTVS — Compras</h1>
        <p>{len(artigos)} artigos carregados da Central de Atendimento</p>
    </header>

    <main class="container">
        <nav class="toc">
            <h3>Índice de Artigos</h3>
            <ul>
                {"".join(indice_html)}
            </ul>
        </nav>

        {"".join(cards_html)}
    </main>
</body>
</html>"""

    return HTMLResponse(content=html_final)