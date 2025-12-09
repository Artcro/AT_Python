# IMDb Top 250 – Scraping, Banco de Dados e Análise

Este projeto faz o seguinte fluxo completo:

1. Baixa as páginas do **IMDb Top 250 filmes** e **IMDb Top 250 séries**.
2. Faz **scraping** com BeautifulSoup para extrair:
   - título  
   - ano de lançamento  
   - nota (rating)
3. Constrói uma hierarquia de classes:
   - `TV` (base)  
   - `Movie` (filmes)  
   - `Series` (séries)
4. Salva os dados em um banco **SQLite (`imdb.db`)** usando SQLAlchemy.
5. Carrega os dados com **Pandas** para:
   - criar categorias de nota (Obra-prima, Excelente, Bom, Mediano)
   - montar um resumo por categoria e ano
   - exportar para **CSV** e **JSON**
6. Exibe tudo no terminal com **Rich**, usando cores e tabelas legíveis.

---

## Tecnologias usadas

- Python 3.x
- [requests](https://pypi.org/project/requests/)  
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)  
- [SQLAlchemy](https://www.sqlalchemy.org/)  
- [pandas](https://pandas.pydata.org/)  
- [rich](https://rich.readthedocs.io/)

As dependências estão listadas em `requirements.txt`.

---

## Estrutura do projeto

Principais arquivos e pastas:

- `config.json`  
  Arquivo de configuração (URLs, limites, caminhos de saída etc).

- `requirements.txt`  
  Dependências do projeto.

- `src/`  
  Código-fonte principal:
  - `main.py`  
    Orquestra todo o fluxo do trabalho (scraping → banco → análise).
  - `config_loader.py`  
    Lê o `config.json` e monta o objeto `Config`.
  - `models.py`  
    Classes de domínio:
    - `TV`
    - `Movie`
    - `Series`
  - `scraping.py`  
    Funções para:
    - baixar HTML das páginas do IMDb
    - carregar HTML local
    - extrair filmes e séries com BeautifulSoup
  - `database.py`  
    - Modelos SQLAlchemy (`MovieModel`, `SeriesModel`)
    - criação do schema (`create_database_schema`)
    - inserção de filmes e séries (`insert_movies_and_series`)
  - `analysis.py`  
    Funções de análise com Pandas:
    - leitura das tabelas em DataFrames
    - classificação de notas em categorias
    - resumo por categoria e ano
    - exportação para CSV e JSON

- `data/`  
  Pasta usada para:
  - arquivos HTML baixados automaticamente
  - banco `imdb.db`
  - arquivos `movies.csv`, `series.csv`, `movies.json`, `series.json`

---