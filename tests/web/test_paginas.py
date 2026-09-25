"""Páginas, cadastro, filtros, exclusão e CSRF."""

import re

from app.infrastructure.models import Peca


def _csrf(html: str) -> str:
    encontrado = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert encontrado, html
    return encontrado.group(1)


def _cadastrar(client, codigo="QA-1", peso="100", cor="azul", comprimento="15"):
    pagina = client.get("/pecas/nova")
    return client.post(
        "/pecas/nova",
        data={
            "csrf_token": _csrf(pagina.get_data(as_text=True)),
            "codigo": codigo,
            "peso": peso,
            "cor": cor,
            "comprimento": comprimento,
        },
        follow_redirects=True,
    )


def test_paginas_carregam(client):
    for rota in ("/", "/pecas", "/pecas/nova", "/caixas", "/relatorios"):
        resposta = client.get(rota)
        assert resposta.status_code == 200, rota


def test_cadastro_valido_mostra_aprovacao(client):
    resposta = _cadastrar(client)
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    assert "PEÇA APROVADA" in texto
    assert "Todos os critérios de qualidade foram atendidos." in texto
    assert Peca.query.count() == 1


def test_cadastro_reprovado_lista_motivos(client):
    resposta = _cadastrar(client, codigo="QR-1", peso="130", cor="vermelho", comprimento="25")
    texto = resposta.get_data(as_text=True)
    assert "PEÇA REPROVADA" in texto
    assert "Peso acima do permitido" in texto
    assert "Cor não permitida" in texto
    assert "Comprimento acima do permitido" in texto


def test_cadastro_invalido_nao_grava(client):
    resposta = _cadastrar(client, codigo="", peso="abc", cor="", comprimento="-1")
    assert resposta.status_code == 400
    assert Peca.query.count() == 0
    texto = resposta.get_data(as_text=True)
    assert "Informe o ID da peça." in texto
    assert "peso" in texto.lower()


def test_id_duplicado(client):
    _cadastrar(client, codigo="QA-1")
    resposta = _cadastrar(client, codigo="QA-1")
    assert resposta.status_code == 400
    assert "já está cadastrado" in resposta.get_data(as_text=True)
    assert Peca.query.count() == 1


def test_filtros_e_busca(client, servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    servico.cadastrar("QR-1", "80", "verde", "15")
    aprovadas = client.get("/pecas?resultado=aprovadas")
    texto = aprovadas.get_data(as_text=True)
    assert "QA-1" in texto
    assert "QR-1" not in texto
    busca = client.get("/pecas?q=QR-1")
    assert "QR-1" in busca.get_data(as_text=True)
    assert "QA-1" not in busca.get_data(as_text=True)
    cor = client.get("/pecas?cor=azul")
    assert "QA-1" in cor.get_data(as_text=True)
    assert "QR-1" not in cor.get_data(as_text=True)


def test_exclusao_com_confirmacao(client, servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    pagina = client.get("/pecas")
    resposta = client.post(
        "/pecas/QA-1/excluir",
        data={"csrf_token": _csrf(pagina.get_data(as_text=True)), "confirmar": "y"},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert Peca.query.count() == 0
    assert "excluída" in resposta.get_data(as_text=True)
    assert 'data-excluir' in pagina.get_data(as_text=True)
    assert "Confirmo a exclusão" in pagina.get_data(as_text=True)


def test_exclusao_sem_confirmacao_nao_apaga(client, servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    pagina = client.get("/pecas")
    client.post(
        "/pecas/QA-1/excluir",
        data={"csrf_token": _csrf(pagina.get_data(as_text=True))},
        follow_redirects=True,
    )
    assert Peca.query.count() == 1


def test_post_sem_csrf_e_recusado(client):
    resposta = client.post(
        "/pecas/nova",
        data={"codigo": "QA-1", "peso": "100", "cor": "azul", "comprimento": "15"},
    )
    assert resposta.status_code == 400
    assert Peca.query.count() == 0


def test_excluir_por_get_nao_e_permitido(client, servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    resposta = client.get("/pecas/QA-1/excluir")
    assert resposta.status_code == 405
    assert Peca.query.count() == 1


def test_relatorio_pdf_baixa(client, servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    resposta = client.get("/relatorios/pdf")
    assert resposta.status_code == 200
    assert resposta.mimetype == "application/pdf"
    assert resposta.headers.get("Content-Disposition", "").startswith("attachment")
    assert resposta.data[:4] == b"%PDF"


def test_caixas_e_relatorio_depois_de_dez(client, servico):
    for indice in range(1, 11):
        servico.cadastrar(f"A{indice:02d}", "100", "azul", "15")
    caixas = client.get("/caixas")
    texto = caixas.get_data(as_text=True)
    assert "10 / 10 peças — FECHADA" in texto
    assert "Fechada" in texto
    relatorio = client.get("/relatorios").get_data(as_text=True)
    assert "100,0%" in relatorio
    assert "armazenadas" in relatorio
    assert "<strong>10</strong> armazenadas" in relatorio
