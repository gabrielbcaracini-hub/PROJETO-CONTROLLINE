# LineControl

Esta pasta contém o sistema completo: código, páginas, testes, migrações e documentação.

Sistema web de gestão de peças, qualidade e armazenamento. O operador cadastra uma peça, o Python avalia peso, cor e comprimento e, se a peça for aprovada, a coloca sozinho em uma caixa de até 10 peças.

O fluxo da apresentação é:

**operador → cadastro → avaliação automática → aprovada ou reprovada → caixa → dashboard → relatório**

É um projeto acadêmico de Algoritmos e Lógica de Programação. A interface principal é web. O menu de terminal existe e usa as mesmas regras, sem repetir a lógica de negócio.

## Objetivo

Simular um trecho de automação industrial em que a decisão de qualidade não depende de cálculo manual. O sistema precisa mostrar, na tela, por que a peça passou ou falhou e onde a peça aprovada foi guardada.

## Tecnologias

- Python 3.10+
- Flask
- SQLAlchemy e Flask-Migrate (Alembic)
- SQLite
- Flask-WTF
- HTML5, CSS3 e JavaScript
- Jinja2
- pytest

Não há Bootstrap nem biblioteca de gráficos. O visual é CSS próprio, para a estrutura ficar legível na apresentação.

## Arquitetura

| Camada | Onde está | Função |
|---|---|---|
| Domínio | `app/domain/` | Constantes, avaliação, plano das caixas e validação |
| Aplicação | `app/application/` | Casos de uso usados pela web e pela CLI |
| Infraestrutura | `app/infrastructure/` | Models, repositórios e SQLite |
| Web | `app/web/` e `app/templates/` | Rotas, formulários e páginas |
| CLI | `app/cli.py` | Menu do enunciado, sem regra duplicada |

A página não decide se a peça passa. Ela mostra o resultado que o serviço já gravou.

## Regras de negócio

Constantes em `app/domain/constants.py`:

| Regra | Valor |
|---|---|
| Peso | 95 g a 105 g, inclusive |
| Cor | `azul` ou `verde`, depois de tirar espaços e passar para minúsculas |
| Comprimento | 10 cm a 20 cm, inclusive |
| Caixa | 10 peças |

A peça só é **APROVADA** se as três condições forem verdadeiras. Cada falha gera um motivo:

- Peso abaixo do permitido
- Peso acima do permitido
- Cor não permitida
- Comprimento abaixo do permitido
- Comprimento acima do permitido

Campo vazio, texto no lugar de número, zero, negativo ou valor acima de 1 000 000 não é gravado. Peso 80 g ou cor `vermelho` é entrada válida e vira peça **REPROVADA**.

### Decisão das caixas

Caixa fechada não é um lote imutável. Depois de excluir uma peça aprovada, as aprovadas que restam são reorganizadas nesta ordem: data de cadastro e, em empate, o ID.

A peça de índice `i` vai para a caixa `i // 10`. Só existe uma caixa aberta. Caixa com 10 peças fica fechada. Se a exclusão esvazia uma caixa, ela sai do banco. Isso evita duas caixas abertas e evita caixa fechada com menos de 10 peças.

Peça reprovada não entra em caixa. Excluir uma reprovada não mexe nas caixas.

## Segurança e dados

- Validação no navegador e, de forma obrigatória, no servidor
- ORM, sem SQL montado com texto do usuário
- Escaping padrão do Jinja2
- Token CSRF nos formulários
- Exclusão só por POST, com confirmação
- Transação com rollback se a operação falhar
- Sem `eval` e sem `exec`
- Sem login e sem dado pessoal: o trabalho não pede operador identificável

O SQLite deste projeto não é criptografado. Criptografar o arquivo exigiria SQLCipher, uma dependência nativa desnecessária para instalar e apresentar o trabalho. O banco guarda código da peça, medidas, cor, resultado e a trilha operacional. O arquivo fica em `instance/` e não entra no Git.

A chave do CSRF não fica no código. Se `SECRET_KEY` não vier do ambiente, a aplicação grava uma chave em `instance/secret_key`.

## Instalação no seu PC (sem nuvem)

Esta pasta já traz o código e os pacotes baixados em `dependencias/`.

### Windows

1. Instale o [Python 3.10+](https://www.python.org/downloads/) e marque **Add python.exe to PATH**.
2. Copie a pasta `qualilinha` para o computador (Área de trabalho ou Documentos).
3. Abra a pasta e dê dois cliques em `instalar.bat`.
4. Depois dê dois cliques em `executar.bat`.
5. Abra `http://127.0.0.1:8741`.

O instalador usa só os arquivos `.whl` desta pasta. Não precisa baixar de novo.

### Linux e macOS

```text
cd qualilinha
chmod +x instalar.sh
./instalar.sh
.venv/bin/python run.py
```

### Instalação manual (se preferir)

Entre nesta pasta antes de instalar:

```text
cd qualilinha
python -m venv .venv
```

Ative o ambiente:

```text
# Linux e macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Instale as dependências a partir da pasta local (sem internet):

```text
pip install --no-index --find-links=dependencias -r requirements.txt
```

Se quiser baixar de novo da internet:

```text
pip install -r requirements.txt
```

Opcional: copie `.env.example` para `.env` e defina `SECRET_KEY` e `PORT`.

## Banco

As migrações usam Flask-Migrate. `python run.py` aplica o que estiver pendente. O comando explícito é:

```text
python -m flask --app run.py db upgrade
```

O arquivo fica em `instance/qualidade.db`.

## Execução

```text
python run.py
```

Abra:

```text
http://127.0.0.1:8741
```

A porta padrão é **8741**. Para usar outra:

```text
# Linux e macOS
PORT=5000 python run.py

# Windows PowerShell
$env:PORT="5000"; python run.py
```

## Dados de demonstração

O seed não roda sozinho. Com o banco vazio:

```text
python seed.py
```

Ele grava 15 peças aprovadas e 6 reprovadas. O resultado é uma caixa fechada (10/10) e uma caixa aberta (5/10), com os cinco motivos de reprovação. Se o banco já tiver peças, o script para e não mistura os dados.

## Testes

```text
pytest
```

A suíte cobre a avaliação, os limites, a caixa, a exclusão, o banco, as páginas, os filtros, o CSRF e o menu da CLI.

## Menu de terminal

```text
python -m app.cli
```

1. Cadastrar nova peça
2. Listar peças aprovadas/reprovadas
3. Remover peça cadastrada
4. Listar caixas fechadas
5. Gerar relatório final
6. Sair

## Rotas

| Método | Rota | Tela |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/pecas` | Listagem e filtros |
| GET e POST | `/pecas/nova` | Cadastro |
| GET | `/pecas/<id>` | Resultado da peça |
| POST | `/pecas/<id>/excluir` | Exclusão confirmada |
| GET | `/caixas` | Caixas e peças |
| GET | `/relatorios` | Relatório final |
| GET | `/auditoria` | Trilha de operações |

## Estrutura

```text
qualilinha/
  app/
    domain/            regras puras e constantes
    application/       casos de uso
    infrastructure/    banco, models e repositórios
    web/               rotas e formulários
    templates/         HTML
    static/css/        visual
    static/js/         menu, confirmação e validação de tela
    cli.py
  tests/
  migrations/
  docs/
    TEORIA.md
    PITCH_SCRIPT.md
  dependencias/      pacotes .whl já baixados
  run.py
  seed.py
  instalar.bat
  executar.bat
  requirements.txt
  .env.example
```

## Exemplos

Cadastro aprovado:

```text
ID: QA-016
Peso: 100
Cor: azul
Comprimento: 15
```

Resultado: **PEÇA APROVADA**. Todos os critérios foram atendidos e a peça entra na caixa aberta.

Cadastro reprovado por mais de um motivo:

```text
ID: QR-007
Peso: 70
Cor: amarelo
Comprimento: 4
```

Resultado: **PEÇA REPROVADA**, com peso abaixo do permitido, cor não permitida e comprimento abaixo do permitido. A peça não entra em caixa.

Limites que ainda aprovam: peso 95 ou 105, comprimento 10 ou 20, cor `Azul` ou `VERDE`.

## Capturas

O espaço abaixo é das telas usadas na apresentação. Gere as imagens com a aplicação no ar, depois do `python seed.py`.

- Dashboard: totais, taxa, barras e atividade recente
- Cadastro: formulário e critérios ao lado
- Ficha: faixa **PEÇA APROVADA** ou **PEÇA REPROVADA** com a lista de motivos
- Caixas: ocupação `7 / 10 peças` ou `10 / 10 peças — FECHADA`
- Relatório: motivos agrupados e situação das caixas

## Documentos da disciplina

- [Teoria](docs/TEORIA.md)
- [Roteiro de apresentação](docs/PITCH_SCRIPT.md)
