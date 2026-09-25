"""Casos de uso: cadastro, avaliação, armazenamento, exclusão e relatórios.

A web e a CLI chamam esta classe. Nenhuma das duas recalcula qualidade
nem decide em qual caixa a peça entra.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from app.application.dto import (
    CadastroRealizado,
    ExclusaoRealizada,
    Painel,
    RegistroAuditoria,
    Relatorio,
)
from app.domain.constants import CAPACIDADE_CAIXA, MOTIVOS_CANONICOS
from app.domain.enums import AcaoAuditoria, EntidadeAuditoria, ResultadoPeca, StatusCaixa
from app.domain.exceptions import CodigoDuplicado, PecaNaoEncontrada
from app.domain.indicadores import calcular_taxa_aprovacao
from app.domain.packing import PecaAlocavel, plano_alocacao, status_para_quantidade
from app.domain.quality import avaliar_peca
from app.domain.validation import validar_cadastro
from app.infrastructure.database import db
from app.infrastructure.models import Caixa, Peca
from app.infrastructure.repositories import AuditoriaRepository, CaixaRepository, PecaRepository


class QualidadeService:
    def __init__(self) -> None:
        self.pecas = PecaRepository()
        self.caixas = CaixaRepository()
        self.auditoria = AuditoriaRepository()

    def cadastrar(self, codigo: object, peso: object, cor: object, comprimento: object) -> CadastroRealizado:
        dados = validar_cadastro(codigo, peso, cor, comprimento)
        if self.pecas.existe(dados.codigo):
            raise CodigoDuplicado(dados.codigo)

        avaliacao = avaliar_peca(dados.peso, dados.cor, dados.comprimento)
        peca = Peca(
            codigo=dados.codigo,
            peso=dados.peso,
            cor=dados.cor,
            comprimento=dados.comprimento,
            resultado=avaliacao.resultado.value,
            cadastrada_em=_agora(),
            caixa_id=None,
        )
        try:
            self.pecas.adicionar(peca)
            for motivo in avaliacao.motivos:
                self.pecas.adicionar_motivo(peca.codigo, motivo)
            db.session.flush()

            eventos: list[RegistroAuditoria] = []
            if avaliacao.aprovada:
                eventos = self._aplicar_plano()

            descricao = _descricao_cadastro(peca.codigo, avaliacao.aprovada, avaliacao.motivos)
            self._gravar(
                RegistroAuditoria(
                    AcaoAuditoria.CADASTRAR.value,
                    EntidadeAuditoria.PECA.value,
                    peca.codigo,
                    descricao,
                )
            )
            for evento in eventos:
                self._gravar(evento)
            db.session.commit()
        except IntegrityError as erro:
            db.session.rollback()
            if self.pecas.existe(dados.codigo):
                raise CodigoDuplicado(dados.codigo) from erro
            raise
        except Exception:
            db.session.rollback()
            raise

        peca_gravada = self.pecas.buscar(dados.codigo)
        if peca_gravada is None:
            raise RuntimeError("A peça não foi encontrada após o cadastro.")
        return CadastroRealizado(
            peca=peca_gravada,
            motivos=avaliacao.motivos,
            aprovada=avaliacao.aprovada,
        )

    def excluir(self, codigo: str) -> ExclusaoRealizada:
        peca = self.pecas.buscar(codigo.strip())
        if peca is None:
            raise PecaNaoEncontrada(codigo)
        codigo_limpo = peca.codigo
        era_aprovada = peca.aprovada
        try:
            peca.caixa_id = None
            self.pecas.excluir(peca)
            db.session.flush()
            eventos = self._aplicar_plano() if era_aprovada else []
            self._gravar(
                RegistroAuditoria(
                    AcaoAuditoria.EXCLUIR.value,
                    EntidadeAuditoria.PECA.value,
                    codigo_limpo,
                    f"Peça {codigo_limpo} excluída.",
                )
            )
            for evento in eventos:
                self._gravar(evento)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        if era_aprovada and eventos:
            mensagem = f"Peça {codigo_limpo} excluída. As caixas foram reorganizadas pela ordem de cadastro."
        else:
            mensagem = f"Peça {codigo_limpo} excluída."
        return ExclusaoRealizada(codigo=codigo_limpo, mensagem=mensagem)

    def obter(self, codigo: str) -> Peca:
        peca = self.pecas.buscar(codigo)
        if peca is None:
            raise PecaNaoEncontrada(codigo)
        return peca

    def listar_pecas(self, resultado: str | None, cor: str | None, codigo: str | None) -> tuple[list[Peca], list[str]]:
        filtro_resultado = _resultado_filtro(resultado)
        cor_filtro = cor.strip().lower() if cor else None
        if cor_filtro == "":
            cor_filtro = None
        busca = codigo.strip() if codigo else None
        if busca == "":
            busca = None
        elif busca and len(busca) > 32:
            busca = busca[:32]
        return self.pecas.listar(filtro_resultado, cor_filtro, busca), self.pecas.cores()

    def listar_caixas(self) -> list[Caixa]:
        return self.caixas.listar()

    def listar_caixas_fechadas(self) -> list[Caixa]:
        return self.caixas.listar_fechadas()

    def listar_auditoria(self) -> list:
        return self.auditoria.listar()

    def painel(self) -> Painel:
        totais = self._totais()
        return Painel(
            total=totais["total"],
            aprovadas=totais["aprovadas"],
            reprovadas=totais["reprovadas"],
            taxa=totais["taxa"],
            caixas_abertas=totais["caixas_abertas"],
            caixas_fechadas=totais["caixas_fechadas"],
            total_caixas=totais["total_caixas"],
            pecas_armazenadas=totais["pecas_armazenadas"],
            atividade=self.auditoria.recentes(8),
            motivos=totais["motivos"],
        )

    def relatorio(self) -> Relatorio:
        totais = self._totais()
        return Relatorio(
            total=totais["total"],
            aprovadas=totais["aprovadas"],
            reprovadas=totais["reprovadas"],
            taxa=totais["taxa"],
            motivos=totais["motivos"],
            total_caixas=totais["total_caixas"],
            caixas_abertas=totais["caixas_abertas"],
            caixas_fechadas=totais["caixas_fechadas"],
            pecas_armazenadas=totais["pecas_armazenadas"],
            caixas=self.caixas.listar(),
        )

    def _totais(self) -> dict[str, object]:
        total = self.pecas.contar()
        aprovadas = self.pecas.contar_resultado(ResultadoPeca.APROVADA.value)
        reprovadas = self.pecas.contar_resultado(ResultadoPeca.REPROVADA.value)
        contagem = self.pecas.contar_motivos()
        motivos = [(motivo, contagem.get(motivo, 0)) for motivo in MOTIVOS_CANONICOS if contagem.get(motivo, 0) > 0]
        return {
            "total": total,
            "aprovadas": aprovadas,
            "reprovadas": reprovadas,
            "taxa": calcular_taxa_aprovacao(aprovadas, total),
            "caixas_abertas": self.caixas.contar_status(StatusCaixa.ABERTA.value),
            "caixas_fechadas": self.caixas.contar_status(StatusCaixa.FECHADA.value),
            "total_caixas": self.caixas.contar(),
            "pecas_armazenadas": aprovadas,
            "motivos": motivos,
        }

    def _aplicar_plano(self) -> list[RegistroAuditoria]:
        """Recalcula as caixas a partir das peças aprovadas ainda gravadas."""
        aprovadas = self.pecas.listar_aprovadas()
        antes = {peca.codigo: peca.caixa_id for peca in aprovadas if peca.caixa_id is not None}
        existentes = self.caixas.listar()
        status_antes = {caixa.id: caixa.status for caixa in existentes}

        plano = plano_alocacao(
            [PecaAlocavel(peca.codigo, peca.cadastrada_em) for peca in aprovadas],
            CAPACIDADE_CAIXA,
        )
        eventos: list[RegistroAuditoria] = []

        while len(existentes) < len(plano):
            caixa = Caixa(
                criada_em=_agora(),
                quantidade=0,
                capacidade=CAPACIDADE_CAIXA,
                status=StatusCaixa.ABERTA.value,
            )
            self.caixas.adicionar(caixa)
            db.session.flush()
            existentes.append(caixa)
            eventos.append(
                RegistroAuditoria(
                    AcaoAuditoria.CRIAR_CAIXA.value,
                    EntidadeAuditoria.CAIXA.value,
                    str(caixa.id),
                    f"Caixa {caixa.id} criada com capacidade de {CAPACIDADE_CAIXA} peças.",
                )
            )

        usadas = existentes[: len(plano)]
        sobrando = existentes[len(plano) :]
        por_codigo = {peca.codigo: peca for peca in aprovadas}

        for peca in aprovadas:
            peca.caixa_id = None
        db.session.flush()

        for caixa in sobrando:
            eventos.append(
                RegistroAuditoria(
                    AcaoAuditoria.REMOVER_CAIXA.value,
                    EntidadeAuditoria.CAIXA.value,
                    str(caixa.id),
                    f"Caixa {caixa.id} removida por ficar sem peças após a reorganização.",
                )
            )
            self.caixas.excluir(caixa)
        db.session.flush()

        for indice, codigos in enumerate(plano):
            caixa = usadas[indice]
            for codigo in codigos:
                por_codigo[codigo].caixa_id = caixa.id
            caixa.quantidade = len(codigos)
            caixa.status = status_para_quantidade(len(codigos), CAPACIDADE_CAIXA).value
            anterior = status_antes.get(caixa.id, StatusCaixa.ABERTA.value)
            if anterior != StatusCaixa.FECHADA.value and caixa.status == StatusCaixa.FECHADA.value:
                eventos.append(
                    RegistroAuditoria(
                        AcaoAuditoria.FECHAR_CAIXA.value,
                        EntidadeAuditoria.CAIXA.value,
                        str(caixa.id),
                        f"Caixa {caixa.id} fechada ao atingir {CAPACIDADE_CAIXA} peças.",
                    )
                )
            elif anterior == StatusCaixa.FECHADA.value and caixa.status == StatusCaixa.ABERTA.value:
                eventos.append(
                    RegistroAuditoria(
                        AcaoAuditoria.REORGANIZAR.value,
                        EntidadeAuditoria.CAIXA.value,
                        str(caixa.id),
                        f"Caixa {caixa.id} reaberta com {caixa.quantidade} peças após exclusão.",
                    )
                )

        db.session.flush()
        depois = {peca.codigo: peca.caixa_id for peca in aprovadas if peca.codigo in antes}
        if any(antes[codigo] != depois.get(codigo) for codigo in antes):
            eventos.append(
                RegistroAuditoria(
                    AcaoAuditoria.REORGANIZAR.value,
                    EntidadeAuditoria.CAIXA.value,
                    "-",
                    "Peças aprovadas reorganizadas pela ordem de cadastro.",
                )
            )
        return eventos

    def _gravar(self, registro: RegistroAuditoria) -> None:
        self.auditoria.registrar(
            registro.acao,
            registro.entidade,
            registro.entidade_id,
            registro.descricao,
        )


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _descricao_cadastro(codigo: str, aprovada: bool, motivos: tuple[str, ...]) -> str:
    if aprovada:
        return f"Peça {codigo} cadastrada com resultado APROVADA."
    lista = "; ".join(motivos)
    return f"Peça {codigo} cadastrada com resultado REPROVADA. Motivos: {lista}."


def _resultado_filtro(valor: str | None) -> str | None:
    if not valor or valor == "todas":
        return None
    mapa = {
        "aprovadas": ResultadoPeca.APROVADA.value,
        "reprovadas": ResultadoPeca.REPROVADA.value,
    }
    return mapa.get(valor)
