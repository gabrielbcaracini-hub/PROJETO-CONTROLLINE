"""Modelos persistidos: peças, motivos, caixas e auditoria."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint

from app.domain.constants import CAPACIDADE_CAIXA, MOTIVOS_CANONICOS
from app.domain.enums import ResultadoPeca, StatusCaixa
from app.infrastructure.database import DecimalTexto, db


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Peca(db.Model):
    __tablename__ = "pecas"
    __table_args__ = (
        CheckConstraint("resultado IN ('APROVADA', 'REPROVADA')", name="ck_peca_resultado"),
        CheckConstraint("peso > 0", name="ck_peca_peso"),
        CheckConstraint("comprimento > 0", name="ck_peca_comprimento"),
    )

    codigo = db.Column(db.String(32), primary_key=True)
    peso = db.Column(DecimalTexto(), nullable=False)
    cor = db.Column(db.String(32), nullable=False, index=True)
    comprimento = db.Column(DecimalTexto(), nullable=False)
    resultado = db.Column(db.String(16), nullable=False, index=True)
    cadastrada_em = db.Column(db.DateTime, nullable=False, default=_agora, index=True)
    caixa_id = db.Column(db.Integer, db.ForeignKey("caixas.id", ondelete="SET NULL"), nullable=True, index=True)

    motivos = db.relationship(
        "MotivoReprovacao",
        back_populates="peca",
        cascade="all, delete-orphan",
        order_by="MotivoReprovacao.id",
    )
    caixa = db.relationship("Caixa", back_populates="pecas")

    @property
    def aprovada(self) -> bool:
        return self.resultado == ResultadoPeca.APROVADA.value

    @property
    def motivos_texto(self) -> list[str]:
        return [motivo.descricao for motivo in self.motivos]


class MotivoReprovacao(db.Model):
    __tablename__ = "motivos_reprovacao"
    __table_args__ = (
        CheckConstraint(
            "descricao IN ({})".format(", ".join(f"'{item}'" for item in MOTIVOS_CANONICOS)),
            name="ck_motivo_descricao",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    peca_codigo = db.Column(
        db.String(32),
        db.ForeignKey("pecas.codigo", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    descricao = db.Column(db.String(80), nullable=False)
    peca = db.relationship("Peca", back_populates="motivos")


class Caixa(db.Model):
    __tablename__ = "caixas"
    __table_args__ = (
        CheckConstraint("status IN ('ABERTA', 'FECHADA')", name="ck_caixa_status"),
        CheckConstraint("quantidade >= 0 AND quantidade <= capacidade", name="ck_caixa_quantidade"),
        CheckConstraint(f"capacidade = {CAPACIDADE_CAIXA}", name="ck_caixa_capacidade"),
    )

    id = db.Column(db.Integer, primary_key=True)
    criada_em = db.Column(db.DateTime, nullable=False, default=_agora)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    capacidade = db.Column(db.Integer, nullable=False, default=CAPACIDADE_CAIXA)
    status = db.Column(db.String(16), nullable=False, default=StatusCaixa.ABERTA.value, index=True)
    pecas = db.relationship(
        "Peca",
        back_populates="caixa",
        order_by="Peca.cadastrada_em, Peca.codigo",
    )

    @property
    def fechada(self) -> bool:
        return self.status == StatusCaixa.FECHADA.value

    @property
    def resumo_ocupacao(self) -> str:
        base = f"{self.quantidade} / {self.capacidade} peças"
        if self.fechada:
            return f"{base} — FECHADA"
        return base


class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(32), nullable=False)
    entidade = db.Column(db.String(32), nullable=False)
    entidade_id = db.Column(db.String(64), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    criada_em = db.Column(db.DateTime, nullable=False, default=_agora, index=True)
