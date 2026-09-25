"""Persistência, caixas, auditoria e transação."""

import pytest

from app.domain.constants import (
    MOTIVO_COMPRIMENTO_ABAIXO,
    MOTIVO_COR,
    MOTIVO_PESO_ABAIXO,
)
from app.domain.enums import AcaoAuditoria
from app.domain.exceptions import CodigoDuplicado, PecaNaoEncontrada
from app.infrastructure.models import Auditoria, Caixa, Peca


def test_aprovada_entra_na_caixa_e_gera_auditoria(servico):
    resultado = servico.cadastrar("QA-1", "100", "azul", "15")
    assert resultado.aprovada
    assert resultado.peca.caixa_id == 1
    caixa = servico.listar_caixas()[0]
    assert caixa.quantidade == 1
    assert caixa.status == "ABERTA"
    assert [peca.codigo for peca in caixa.pecas] == ["QA-1"]
    acoes = [item.acao for item in servico.listar_auditoria()]
    assert AcaoAuditoria.CADASTRAR.value in acoes
    assert AcaoAuditoria.CRIAR_CAIXA.value in acoes


def test_reprovada_nao_cria_caixa(servico):
    resultado = servico.cadastrar("QR-1", "80", "amarelo", "4")
    assert resultado.motivos == (MOTIVO_PESO_ABAIXO, MOTIVO_COR, MOTIVO_COMPRIMENTO_ABAIXO)
    assert resultado.peca.caixa_id is None
    assert servico.listar_caixas() == []


def test_id_duplicado_nao_grava_segunda_linha(servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    with pytest.raises(CodigoDuplicado):
        servico.cadastrar("QA-1", "101", "verde", "16")
    assert Peca.query.count() == 1


def test_fecha_na_decima_e_abre_outra_na_seguinte(servico):
    for indice in range(1, 11):
        servico.cadastrar(f"A{indice:02d}", "100", "azul", "15")
    caixas = servico.listar_caixas()
    assert len(caixas) == 1
    assert caixas[0].status == "FECHADA"
    assert caixas[0].quantidade == 10
    assert any(item.acao == AcaoAuditoria.FECHAR_CAIXA.value for item in servico.listar_auditoria())

    servico.cadastrar("A11", "100", "verde", "12")
    caixas = servico.listar_caixas()
    assert [(caixa.status, caixa.quantidade) for caixa in caixas] == [("FECHADA", 10), ("ABERTA", 1)]


def test_exclusao_reempacota_e_atualiza_caixa(servico):
    for indice in range(1, 12):
        servico.cadastrar(f"B{indice:02d}", "100", "verde", "18")
    servico.excluir("B03")
    with pytest.raises(PecaNaoEncontrada):
        servico.obter("B03")
    caixas = servico.listar_caixas()
    assert len(caixas) == 1
    assert caixas[0].status == "FECHADA"
    assert caixas[0].quantidade == 10
    codigos = [peca.codigo for peca in caixas[0].pecas]
    assert "B03" not in codigos
    assert codigos[2] == "B04"
    assert Caixa.query.count() == 1
    assert any(item.acao == AcaoAuditoria.EXCLUIR.value for item in Auditoria.query.all())


def test_exclusao_de_reprovada_nao_mexe_na_caixa(servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    servico.cadastrar("QR-1", "100", "vermelho", "15")
    servico.excluir("QR-1")
    caixa = servico.listar_caixas()[0]
    assert caixa.quantidade == 1
    assert [peca.codigo for peca in caixa.pecas] == ["QA-1"]


def test_rollback_se_a_auditoria_falhar(servico, monkeypatch):
    def falha(*_args, **_kwargs):
        raise RuntimeError("falha de auditoria")

    monkeypatch.setattr(servico.auditoria, "registrar", falha)
    with pytest.raises(RuntimeError):
        servico.cadastrar("QA-9", "100", "azul", "15")
    assert Peca.query.count() == 0
    assert Caixa.query.count() == 0


def test_limites_exatos_e_normalizacao_persistem(servico):
    resultado = servico.cadastrar("  LIM-1 ", "95", " AZUL ", "10")
    assert resultado.aprovada
    assert resultado.peca.codigo == "LIM-1"
    assert resultado.peca.cor == "azul"
    servico.cadastrar("LIM-2", "105,00", "verde", "20")
    assert servico.obter("LIM-2").aprovada


def test_relatorio_agrupa_motivos(servico):
    servico.cadastrar("QA-1", "100", "azul", "15")
    servico.cadastrar("R1", "90", "azul", "15")
    servico.cadastrar("R2", "90", "vermelho", "8")
    relatorio = servico.relatorio()
    assert relatorio.total == 3
    assert relatorio.aprovadas == 1
    assert relatorio.reprovadas == 2
    assert relatorio.pecas_armazenadas == 1
    motivos = dict(relatorio.motivos)
    assert motivos[MOTIVO_PESO_ABAIXO] == 2
    assert motivos[MOTIVO_COR] == 1
    assert motivos[MOTIVO_COMPRIMENTO_ABAIXO] == 1


def test_entradas_invalidas_nao_persistem(servico):
    from app.domain.exceptions import DadosInvalidos

    for peso, cor, comprimento in (("", "azul", "15"), ("-5", "azul", "15"), ("abc", "azul", "15"), ("0", "azul", "15")):
        with pytest.raises(DadosInvalidos):
            servico.cadastrar("X1", peso, cor, comprimento)
    assert Peca.query.count() == 0
