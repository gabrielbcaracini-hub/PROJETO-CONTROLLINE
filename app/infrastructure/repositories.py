"""Consultas e gravações. As rotas não montam SQL."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.enums import ResultadoPeca
from app.infrastructure.database import db
from app.infrastructure.models import Auditoria, Caixa, MotivoReprovacao, Peca


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PecaRepository:
    def __init__(self, session: Session | None = None) -> None:
        self.session = session or db.session

    def buscar(self, codigo: str) -> Peca | None:
        return self.session.get(Peca, codigo)

    def existe(self, codigo: str) -> bool:
        return self.buscar(codigo) is not None

    def adicionar(self, peca: Peca) -> None:
        self.session.add(peca)

    def excluir(self, peca: Peca) -> None:
        self.session.delete(peca)

    def listar(self, resultado: str | None, cor: str | None, codigo: str | None) -> list[Peca]:
        consulta = self.session.query(Peca)
        if resultado:
            consulta = consulta.filter(Peca.resultado == resultado)
        if cor:
            consulta = consulta.filter(Peca.cor == cor)
        if codigo:
            termo = _padrao_like(codigo)
            consulta = consulta.filter(Peca.codigo.ilike(termo, escape="\\"))
        return consulta.order_by(Peca.cadastrada_em.desc(), Peca.codigo.asc()).all()

    def listar_aprovadas(self) -> list[Peca]:
        return (
            self.session.query(Peca)
            .filter(Peca.resultado == ResultadoPeca.APROVADA.value)
            .order_by(Peca.cadastrada_em.asc(), Peca.codigo.asc())
            .all()
        )

    def contar(self) -> int:
        return self.session.query(func.count(Peca.codigo)).scalar() or 0

    def contar_resultado(self, resultado: str) -> int:
        return (
            self.session.query(func.count(Peca.codigo)).filter(Peca.resultado == resultado).scalar() or 0
        )

    def cores(self) -> list[str]:
        linhas = self.session.query(Peca.cor).distinct().order_by(Peca.cor.asc()).all()
        return [linha[0] for linha in linhas]

    def contar_motivos(self) -> dict[str, int]:
        linhas = (
            self.session.query(MotivoReprovacao.descricao, func.count(MotivoReprovacao.id))
            .group_by(MotivoReprovacao.descricao)
            .all()
        )
        return {descricao: quantidade for descricao, quantidade in linhas}

    def adicionar_motivo(self, peca_codigo: str, descricao: str) -> None:
        self.session.add(MotivoReprovacao(peca_codigo=peca_codigo, descricao=descricao))


class CaixaRepository:
    def __init__(self, session: Session | None = None) -> None:
        self.session = session or db.session

    def listar(self) -> list[Caixa]:
        return self.session.query(Caixa).order_by(Caixa.id.asc()).all()

    def listar_fechadas(self) -> list[Caixa]:
        from app.domain.enums import StatusCaixa

        return (
            self.session.query(Caixa)
            .filter(Caixa.status == StatusCaixa.FECHADA.value)
            .order_by(Caixa.id.asc())
            .all()
        )

    def adicionar(self, caixa: Caixa) -> None:
        self.session.add(caixa)

    def excluir(self, caixa: Caixa) -> None:
        self.session.delete(caixa)

    def contar(self) -> int:
        return self.session.query(func.count(Caixa.id)).scalar() or 0

    def contar_status(self, status: str) -> int:
        return self.session.query(func.count(Caixa.id)).filter(Caixa.status == status).scalar() or 0


class AuditoriaRepository:
    def __init__(self, session: Session | None = None) -> None:
        self.session = session or db.session

    def registrar(self, acao: str, entidade: str, entidade_id: str, descricao: str) -> Auditoria:
        registro = Auditoria(
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            descricao=descricao[:500],
            criada_em=_agora(),
        )
        self.session.add(registro)
        return registro

    def recentes(self, limite: int = 8) -> list[Auditoria]:
        return (
            self.session.query(Auditoria)
            .order_by(Auditoria.criada_em.desc(), Auditoria.id.desc())
            .limit(limite)
            .all()
        )

    def listar(self) -> list[Auditoria]:
        return self.session.query(Auditoria).order_by(Auditoria.criada_em.desc(), Auditoria.id.desc()).all()


def _padrao_like(termo: str) -> str:
    escapado = termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escapado}%"
