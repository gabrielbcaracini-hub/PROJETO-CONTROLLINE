"""Cadastro, listagem, ficha e exclusão de peças."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.application.services import QualidadeService
from app.domain.exceptions import CodigoDuplicado, DadosInvalidos, PecaNaoEncontrada
from app.web.forms import FormExclusao, FormPeca
from app.web.helpers import itens_avaliacao

bp = Blueprint("pecas", __name__, url_prefix="/pecas")


@bp.get("/", strict_slashes=False)
def lista():
    servico = QualidadeService()
    pecas, cores = servico.listar_pecas(
        request.args.get("resultado"),
        request.args.get("cor"),
        request.args.get("q"),
    )
    return render_template(
        "pecas/lista.html",
        pecas=pecas,
        cores=cores,
        resultado=request.args.get("resultado") or "todas",
        cor=request.args.get("cor") or "",
        q=request.args.get("q") or "",
        form_exclusao=FormExclusao(),
    )


@bp.route("/nova", methods=["GET", "POST"])
def nova():
    form = FormPeca()
    erros: dict[str, str] = {}
    if request.method == "POST":
        if not form.validate_on_submit():
            abort(400)
        servico = QualidadeService()
        try:
            resultado = servico.cadastrar(
                form.codigo.data,
                form.peso.data,
                form.cor.data,
                form.comprimento.data,
            )
        except DadosInvalidos as exc:
            erros = exc.erros
        except CodigoDuplicado:
            erros = {"codigo": "Este ID já está cadastrado."}
        else:
            flash("Cadastro concluído. A avaliação automática está na ficha da peça.", "sucesso")
            return redirect(url_for("pecas.detalhe", codigo=resultado.peca.codigo, cadastrada=1))
        return render_template("pecas/nova.html", form=form, erros=erros), 400
    return render_template("pecas/nova.html", form=form, erros=erros)


@bp.get("/<codigo>")
def detalhe(codigo: str):
    try:
        peca = QualidadeService().obter(codigo)
    except PecaNaoEncontrada:
        abort(404)
    return render_template(
        "pecas/detalhe.html",
        peca=peca,
        itens=itens_avaliacao(peca),
        cadastrada=request.args.get("cadastrada") == "1",
        form_exclusao=FormExclusao(),
    )


@bp.post("/<codigo>/excluir")
def excluir(codigo: str):
    form = FormExclusao()
    if not form.validate_on_submit():
        flash("Confirme a exclusão para continuar.", "erro")
        destino = request.referrer or url_for("pecas.lista")
        return redirect(destino)
    try:
        resultado = QualidadeService().excluir(codigo)
    except PecaNaoEncontrada:
        abort(404)
    flash(resultado.mensagem, "sucesso")
    return redirect(url_for("pecas.lista"))
