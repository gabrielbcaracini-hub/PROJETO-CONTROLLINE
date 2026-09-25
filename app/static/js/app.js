(function () {
  var regrasEl = document.getElementById("regras-qualidade");
  var regras = regrasEl ? JSON.parse(regrasEl.textContent) : null;

  var botaoMenu = document.querySelector("[data-menu]");
  if (botaoMenu) {
    botaoMenu.addEventListener("click", function () {
      var aberto = document.body.classList.toggle("menu-aberto");
      botaoMenu.setAttribute("aria-expanded", aberto ? "true" : "false");
    });
  }

  var dialogo = document.getElementById("dialogo-excluir");
  var formExcluir = document.getElementById("form-excluir");
  var textoExcluir = document.getElementById("texto-excluir");
  document.querySelectorAll("[data-excluir]").forEach(function (botao) {
    botao.addEventListener("click", function () {
      var codigo = botao.getAttribute("data-codigo");
      var url = botao.getAttribute("data-url");
      if (!formExcluir || !dialogo) {
        return;
      }
      formExcluir.action = url;
      var caixa = formExcluir.querySelector("input[name='confirmar']");
      if (caixa) {
        caixa.checked = false;
      }
      if (textoExcluir) {
        textoExcluir.textContent = "A peça " + codigo + " será removida. Se ela estava em uma caixa, as aprovadas restantes são reorganizadas pela ordem de cadastro.";
      }
      if (typeof dialogo.showModal === "function") {
        dialogo.showModal();
      } else if (window.confirm("Confirma a exclusão da peça " + codigo + "?")) {
        if (caixa) {
          caixa.checked = true;
        }
        formExcluir.submit();
      }
    });
  });

  document.querySelectorAll("[data-fechar-dialogo]").forEach(function (botao) {
    botao.addEventListener("click", function () {
      if (dialogo && typeof dialogo.close === "function") {
        dialogo.close();
      }
    });
  });

  var popoverAjuda = document.getElementById("help-popover");
  var wrapAjuda = document.querySelector(".help-popover-wrap");
  var formAjuda = document.getElementById("form-ajuda");
  var respostaAjuda = document.getElementById("resposta-ajuda");
  var perguntaAjuda = document.getElementById("pergunta-ajuda");
  var botaoAjuda = document.querySelector("[data-ajuda]");

  function fecharAjuda() {
    if (!popoverAjuda || !botaoAjuda) {
      return;
    }
    popoverAjuda.hidden = true;
    botaoAjuda.setAttribute("aria-expanded", "false");
  }

  function abrirAjuda() {
    if (!popoverAjuda || !botaoAjuda) {
      return;
    }
    if (respostaAjuda) {
      respostaAjuda.hidden = true;
      respostaAjuda.textContent = "";
    }
    if (perguntaAjuda) {
      perguntaAjuda.value = "";
    }
    popoverAjuda.hidden = false;
    botaoAjuda.setAttribute("aria-expanded", "true");
    if (perguntaAjuda) {
      perguntaAjuda.focus();
    }
  }

  if (botaoAjuda && popoverAjuda) {
    botaoAjuda.addEventListener("click", function (evento) {
      evento.stopPropagation();
      if (popoverAjuda.hidden) {
        abrirAjuda();
      } else {
        fecharAjuda();
      }
    });
  }

  document.querySelectorAll("[data-fechar-ajuda]").forEach(function (botao) {
    botao.addEventListener("click", function (evento) {
      evento.stopPropagation();
      fecharAjuda();
    });
  });

  document.addEventListener("click", function (evento) {
    if (!wrapAjuda || !popoverAjuda || popoverAjuda.hidden) {
      return;
    }
    if (!wrapAjuda.contains(evento.target)) {
      fecharAjuda();
    }
  });

  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape") {
      fecharAjuda();
    }
  });

  if (formAjuda) {
    formAjuda.addEventListener("submit", function (evento) {
      evento.preventDefault();
      var texto = perguntaAjuda ? perguntaAjuda.value.trim() : "";
      if (!respostaAjuda) {
        return;
      }
      respostaAjuda.hidden = false;
      respostaAjuda.textContent = responderAjuda(texto);
    });
  }

  function responderAjuda(pergunta) {
    var chave = normalizar(pergunta);
    if (!chave) {
      return "Digite uma pergunta sobre o sistema para receber orientação.";
    }

    var respostas = [
      {
        palavras: ["cadastr", "nova peca", "nova peça", "registr", "incluir peca", "incluir peça"],
        texto: "Para cadastrar uma peça, acesse Cadastrar peça no menu lateral. Informe ID, peso, cor e comprimento e envie o formulário. O sistema avalia os critérios e mostra se a peça foi aprovada ou reprovada."
      },
      {
        palavras: ["peca", "peça", "pecas", "peças", "listar", "consultar", "buscar"],
        texto: "A tela Peças lista todas as peças cadastradas. Use os filtros por resultado, cor ou busca por ID para encontrar um registro específico e abrir o detalhe."
      },
      {
        palavras: ["aprovar", "aprovada", "aprovadas", "aprovacao", "aprovação"],
        texto: "A aprovação é automática no cadastro. Se peso, cor e comprimento estiverem dentro dos critérios, a peça é aprovada e pode entrar em uma caixa de armazenamento."
      },
      {
        palavras: ["reprovar", "reprovada", "reprovadas", "reprovacao", "reprovação", "motivo"],
        texto: "Peças reprovadas ficam registradas com os motivos que falharam (peso, cor ou comprimento). Você vê os motivos no resultado do cadastro, no dashboard e no relatório."
      },
      {
        palavras: ["caixa", "caixas", "armazen", "fechad", "aberta"],
        texto: "Peças aprovadas são alocadas em caixas com capacidade limitada. Quando uma caixa enche, ela é fechada e outra aberta. Acompanhe a ocupação em Caixas no menu."
      },
      {
        palavras: ["relatorio", "relatório", "pdf", "baixar", "exportar", "imprimir"],
        texto: "Em Relatórios você vê totais, motivos de reprovação e situação das caixas. Use Baixar Relatório para gerar um PDF com o resumo consolidado."
      },
      {
        palavras: ["excluir", "remover", "apagar", "deletar"],
        texto: "Na lista de peças, use Excluir no registro desejado. Confirme a exclusão no diálogo. Se a peça estava em uma caixa, as aprovadas restantes são reorganizadas."
      },
      {
        palavras: ["dashboard", "inicio", "início", "painel", "indicador", "atividade"],
        texto: "O dashboard mostra totais, taxa de aprovação, gráficos de motivos e a atividade recente das operações do sistema."
      },
      {
        palavras: ["criterio", "critério", "peso", "cor", "comprimento", "regra"],
        texto: "Os critérios de qualidade são validados no cadastro: peso e comprimento dentro dos limites e cor entre as permitidas. Valores inválidos no formulário são recusados antes da avaliação."
      }
    ];

    for (var indice = 0; indice < respostas.length; indice += 1) {
      var item = respostas[indice];
      for (var pos = 0; pos < item.palavras.length; pos += 1) {
        if (chave.indexOf(item.palavras[pos]) !== -1) {
          return item.texto;
        }
      }
    }

    return "Não encontrei uma resposta exata para isso. Explore o menu lateral: Dashboard, Peças, Cadastrar peça, Caixas e Relatórios cobrem as principais funções do LineControl.";
  }

  function normalizar(texto) {
    return texto
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9\s?]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  var formPeca = document.getElementById("form-peca");
  if (formPeca && regras) {
    formPeca.addEventListener("submit", function (evento) {
      var erros = validarFormulario(formPeca, regras);
      limparErros(formPeca);
      var campos = Object.keys(erros);
      if (!campos.length) {
        return;
      }
      evento.preventDefault();
      campos.forEach(function (campo) {
        mostrarErro(campo, erros[campo]);
      });
      var primeiro = formPeca.querySelector("[name='" + campos[0] + "']");
      if (primeiro) {
        primeiro.focus();
      }
    });
  }

  function validarFormulario(form, regrasAtuais) {
    var erros = {};
    var codigo = valor(form, "codigo");
    var peso = valor(form, "peso");
    var cor = valor(form, "cor");
    var comprimento = valor(form, "comprimento");
    var codigoOk = new RegExp("^[A-Za-z0-9][A-Za-z0-9_-]{0," + (regrasAtuais.codigoMax - 1) + "}$");

    if (!codigo) {
      erros.codigo = "Informe o ID da peça.";
    } else if (!codigoOk.test(codigo)) {
      erros.codigo = "Use de 1 a " + regrasAtuais.codigoMax + " caracteres: letras, números, hífen ou sublinhado, começando por letra ou número.";
    }
    validarNumero(erros, "peso", peso, "o peso em gramas", regrasAtuais);
    validarNumero(erros, "comprimento", comprimento, "o comprimento em centímetros", regrasAtuais);
    if (!cor) {
      erros.cor = "Informe a cor.";
    } else if (cor.length > regrasAtuais.corMax) {
      erros.cor = "A cor deve ter no máximo " + regrasAtuais.corMax + " caracteres.";
    }
    return erros;
  }

  function validarNumero(erros, campo, bruto, nome, regrasAtuais) {
    if (!bruto) {
      erros[campo] = "Informe " + nome + ".";
      return;
    }
    var texto = bruto.replace(",", ".");
    if (!/^\d+(\.\d+)?$/.test(texto)) {
      erros[campo] = "Informe " + nome + " com até " + regrasAtuais.casasDecimais + " casas decimais, usando ponto ou vírgula.";
      return;
    }
    var numero = Number(texto);
    if (!(numero > 0)) {
      erros[campo] = nome.charAt(0).toUpperCase() + nome.slice(1) + " deve ser maior que zero.";
      return;
    }
    if (numero > regrasAtuais.valorMaximo) {
      erros[campo] = nome.charAt(0).toUpperCase() + nome.slice(1) + " ultrapassa o limite aceito neste cadastro.";
      return;
    }
    var casas = texto.indexOf(".") === -1 ? 0 : texto.split(".")[1].length;
    if (casas > regrasAtuais.casasDecimais) {
      erros[campo] = "Use no máximo " + regrasAtuais.casasDecimais + " casas decimais em " + nome + ".";
    }
  }

  function valor(form, nome) {
    var campo = form.querySelector("[name='" + nome + "']");
    return campo ? campo.value.trim() : "";
  }

  function limparErros(form) {
    form.querySelectorAll(".erro-campo").forEach(function (el) {
      el.textContent = "";
      el.hidden = true;
    });
    form.querySelectorAll("[aria-invalid='true']").forEach(function (el) {
      el.removeAttribute("aria-invalid");
    });
  }

  function mostrarErro(campo, mensagem) {
    var alvo = document.getElementById("erro-" + campo);
    var input = document.getElementById(campo);
    if (alvo) {
      alvo.hidden = false;
      alvo.textContent = mensagem;
    }
    if (input) {
      input.setAttribute("aria-invalid", "true");
    }
  }
})();
