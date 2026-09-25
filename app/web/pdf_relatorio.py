"""Geração de PDF do relatório consolidado."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.application.dto import Relatorio
from app.web.formatacao import formatar_data, formatar_percentual

_SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def gerar_pdf(relatorio: Relatorio) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Relatório LineControl",
    )
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloRelatorio",
        parent=estilos["Heading1"],
        fontSize=18,
        spaceAfter=6,
    )
    subtitulo = ParagraphStyle(
        "SubtituloRelatorio",
        parent=estilos["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        spaceAfter=14,
    )
    secao = ParagraphStyle(
        "SecaoRelatorio",
        parent=estilos["Heading2"],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=8,
    )

    elementos: list = []
    agora = datetime.now(timezone.utc).astimezone(_SAO_PAULO)
    elementos.append(Paragraph("LineControl — Relatório de Inspeção", titulo))
    elementos.append(Paragraph(f"Gerado em {agora.strftime('%d/%m/%Y %H:%M')}", subtitulo))

    totais = [
        ["Peças cadastradas", str(relatorio.total)],
        ["Aprovadas", str(relatorio.aprovadas)],
        ["Reprovadas", str(relatorio.reprovadas)],
        ["Percentual de aprovação", formatar_percentual(relatorio.taxa)],
        ["Caixas utilizadas", str(relatorio.total_caixas)],
        ["Caixas abertas", str(relatorio.caixas_abertas)],
        ["Caixas fechadas", str(relatorio.caixas_fechadas)],
        ["Peças armazenadas", str(relatorio.pecas_armazenadas)],
    ]
    elementos.append(Paragraph("Resumo geral", secao))
    elementos.append(_tabela_simples(totais, [5.5 * cm, None]))
    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(Paragraph("Motivos de reprovação", secao))
    if relatorio.motivos:
        motivos = [[nome, str(qtd)] for nome, qtd in relatorio.motivos]
        elementos.append(_tabela_simples([["Motivo", "Quantidade"], *motivos], [10 * cm, 3 * cm], cabecalho=True))
    else:
        elementos.append(Paragraph("Nenhum motivo registrado.", estilos["Normal"]))
    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(Paragraph("Caixas", secao))
    if relatorio.caixas:
        linhas = [["Caixa", "Status", "Ocupação", "Criação"]]
        for caixa in relatorio.caixas:
            linhas.append(
                [
                    str(caixa.id),
                    "Fechada" if caixa.fechada else "Aberta",
                    caixa.resumo_ocupacao,
                    formatar_data(caixa.criada_em),
                ]
            )
        elementos.append(_tabela_simples(linhas, [1.8 * cm, 2.5 * cm, 5.5 * cm, 4 * cm], cabecalho=True))
    else:
        elementos.append(Paragraph("Nenhuma caixa utilizada.", estilos["Normal"]))

    doc.build(elementos)
    return buffer.getvalue()


def _tabela_simples(linhas: list[list[str]], larguras: list, cabecalho: bool = False) -> Table:
    tabela = Table(linhas, colWidths=larguras, hAlign="LEFT")
    estilo = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if cabecalho:
        estilo.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef2")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    tabela.setStyle(TableStyle(estilo))
    return tabela
