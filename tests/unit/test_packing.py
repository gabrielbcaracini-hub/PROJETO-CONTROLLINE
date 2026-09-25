"""Plano determinístico das caixas."""

from datetime import datetime, timedelta

from app.domain.enums import StatusCaixa
from app.domain.packing import PecaAlocavel, plano_alocacao, status_para_quantidade


def _pecas(quantidade: int) -> list[PecaAlocavel]:
    base = datetime(2026, 9, 1, 8, 0, 0)
    return [PecaAlocavel(f"P{indice:02d}", base + timedelta(seconds=indice)) for indice in range(quantidade)]


def test_decima_peca_fecha_a_unica_caixa():
    plano = plano_alocacao(_pecas(10))
    assert plano == [ [f"P{indice:02d}" for indice in range(10)] ]
    assert status_para_quantidade(10) is StatusCaixa.FECHADA


def test_decima_primeira_abre_nova_caixa():
    plano = plano_alocacao(_pecas(11))
    assert len(plano) == 2
    assert len(plano[0]) == 10
    assert plano[1] == ["P10"]
    assert status_para_quantidade(1) is StatusCaixa.ABERTA


def test_remocao_reorganiza_pela_ordem_de_cadastro():
    pecas = _pecas(11)
    restantes = [peca for peca in pecas if peca.codigo != "P02"]
    plano = plano_alocacao(restantes)
    assert len(plano) == 1
    assert len(plano[0]) == 10
    assert plano[0][2] == "P03"


def test_empate_de_horario_desempata_pelo_id():
    momento = datetime(2026, 9, 1, 8, 0, 0)
    plano = plano_alocacao(
        [
            PecaAlocavel("B", momento),
            PecaAlocavel("A", momento),
        ]
    )
    assert plano == [["A", "B"]]
