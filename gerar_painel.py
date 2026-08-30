r"""
Gera o "Painel de Resultados" em ESTILO APRESENTAÇÃO — cada seção ocupa a
tela inteira (como um slide), navega com setas do teclado / clique / swipe,
igual à reunião de fechamento mensal que virava PowerPoint. Autocontido
(CSS/JS inline), pronto pra Artifact ou GitHub Pages.
"""

import base64
import json
import os

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(PASTA_BASE, "dados.json")
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "painel.html")

# Reaproveita as fotos e o logo já cadastrados no painel_pilares.
PASTA_FOTOS_SUPERVISORES = os.path.join(PASTA_BASE, "..", "painel_pilares", "fotos_supervisores")
PASTA_FOTOS_RCAS = os.path.join(PASTA_BASE, "..", "painel_pilares", "fotos_rcas")
CAMINHO_LOGO = os.path.join(PASTA_BASE, "..", "painel_pilares", "logo_tet.png")


PASTA_EMBLEMAS = os.path.join(PASTA_BASE, "emblemas")
CAMINHO_LOGO_FRIATO = os.path.join(PASTA_EMBLEMAS, "logo_friato.png")
NOMES_EMBLEMAS = ["gladiadores", "vencedores", "imperadores", "aguia", "invictus", "veteranos", "titans", "falcao"]
CAMINHO_PRODUTOS_FRIATO = os.path.join(PASTA_BASE, "imagens", "produtos_friato.png")
CAMINHO_VENDEDOR_TROFEU = os.path.join(PASTA_BASE, "imagens", "vendedor_trofeu.png")
CAMINHO_GRAMADO = os.path.join(PASTA_BASE, "imagens", "gramado_churrascaria.png")
CAMINHO_RESTAURANTE_INTERIOR = os.path.join(PASTA_BASE, "imagens", "restaurante_interior.png")
CAMINHO_RESTAURANTE_BUFFET = os.path.join(PASTA_BASE, "imagens", "restaurante_buffet.png")


def _logo_data_uri():
    if not os.path.exists(CAMINHO_LOGO):
        return ""
    with open(CAMINHO_LOGO, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


def _imagem_data_uri(caminho):
    if not os.path.exists(caminho):
        return ""
    with open(caminho, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


def _fotos_json(pasta, com_subpastas):
    fotos = {}
    if not os.path.isdir(pasta):
        return json.dumps(fotos, ensure_ascii=False)
    origens = []
    if com_subpastas:
        for nome_pasta in os.listdir(pasta):
            caminho = os.path.join(pasta, nome_pasta)
            if os.path.isdir(caminho):
                origens.append(caminho)
    else:
        origens.append(pasta)
    for origem in origens:
        for nome_arquivo in os.listdir(origem):
            nome, ext = os.path.splitext(nome_arquivo)
            if ext.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            tipo_mime = "image/png" if ext.lower() == ".png" else "image/jpeg"
            with open(os.path.join(origem, nome_arquivo), "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            fotos[nome.upper().strip()] = f"data:{tipo_mime};base64,{b64}"
    return json.dumps(fotos, ensure_ascii=False)


_FOTOS_SUPERVISORES_JSON = _fotos_json(PASTA_FOTOS_SUPERVISORES, com_subpastas=False)
_FOTOS_RCAS_JSON = _fotos_json(PASTA_FOTOS_RCAS, com_subpastas=True)
_LOGO_URI = _logo_data_uri()
_LOGO_FRIATO_URI = _imagem_data_uri(CAMINHO_LOGO_FRIATO)
_EMBLEMAS_JSON = json.dumps(
    {nome: _imagem_data_uri(os.path.join(PASTA_EMBLEMAS, f"{nome}.png")) for nome in NOMES_EMBLEMAS},
    ensure_ascii=False,
)
_PRODUTOS_FRIATO_URI = _imagem_data_uri(CAMINHO_PRODUTOS_FRIATO)
_VENDEDOR_TROFEU_URI = _imagem_data_uri(CAMINHO_VENDEDOR_TROFEU)
_GRAMADO_URI = _imagem_data_uri(CAMINHO_GRAMADO)
_RESTAURANTE_INTERIOR_URI = _imagem_data_uri(CAMINHO_RESTAURANTE_INTERIOR)
_RESTAURANTE_BUFFET_URI = _imagem_data_uri(CAMINHO_RESTAURANTE_BUFFET)

TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de Resultados — Equipe GYN</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700;900&display=swap" rel="stylesheet">
<style>
:root {
  /* Paleta extraída do PowerPoint original (tema + slides): fundo branco,
     vermelho T&T (BF2B24) nos títulos, dourado (F3C500) nos destaques de
     troféu, creme (FFECB3) nos cartões de vitrine. */
  --bg: #FFFFFF; --surface: #FFFFFF; --surface-2: #F7F4EE; --border: #E6E1D6;
  --ink: #1A1A1A; --ink-soft: #55524C; --ink-faint: #8A867C;
  --accent: #BF2B24; --good: #196B24; --warn: #E97132; --bad: #BF2B24;
  --gold: #F3C500; --creme: #FFECB3;
}
* { box-sizing: border-box; }
html, body { height: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink); overflow: hidden;
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
h1, h2, .eyebrow, .destaque-nome, .capa-linha {
  font-family: "Roboto Slab", Georgia, "Times New Roman", ui-serif, serif;
}

.slides { height: 100vh; width: 100vw; position: relative; }
.slide {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; padding: 40px 6vw;
  opacity: 0; pointer-events: none; transition: opacity 0.35s ease;
  text-align: center;
}
.slide.active { opacity: 1; pointer-events: auto; }

.eyebrow { font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em; color: var(--accent); margin-bottom: 10px; }
.slide h1 { font-size: clamp(32px, 5vw, 58px); font-weight: 800; margin: 0 0 6px; letter-spacing: -0.01em; }
.slide h2 { font-size: clamp(24px, 3.4vw, 38px); font-weight: 800; margin: 0 0 28px; }
.slide .sub { color: var(--ink-soft); font-size: clamp(15px, 1.6vw, 19px); margin: 0 0 8px; }

/* Capa — replica o slide 1 do PowerPoint: título vermelho em 3 linhas
   (evento / mês / ano) + logo T&T dentro de um anel prateado com sombra. */
.capa-titulo { margin: 0 0 24px; line-height: 1.12; }
.capa-linha { display: block; font-size: clamp(26px, 4.6vw, 48px); font-weight: 900; color: var(--accent); letter-spacing: 0.01em; }
.capa-linha.ano { font-size: clamp(18px, 3.1vw, 32px); }
.capa .logo-anel { display: flex; align-items: center; justify-content: center; }
.capa .logo-anel img {
  width: auto; height: clamp(120px, 28vh, 220px); max-width: 60vw;
  filter: drop-shadow(0 14px 24px rgba(26,26,26,0.3));
}

/* Divisor de seção — réplica do slide 2 (Cronograma): faixa preta horizontal
   com título branco centralizado, resto da tela em branco. Mesmo padrão
   visual usado nos slides de abertura de cada bloco do PowerPoint. */
.slide.divisor { justify-content: flex-start; padding: 0; }
.divisor-faixa {
  position: absolute; top: 9.5%; left: 0; width: 100%; height: 10.8%;
  background: #000000; display: flex; align-items: center; justify-content: center;
  padding: 0 6vw;
}
.divisor-faixa h1 {
  margin: 0; color: #FFFFFF; font-size: clamp(20px, 2.6vw, 32px); font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.01em;
}

/* Título com linha vermelha embaixo — réplica do slide 3 (Novos
   Colaboradores): título vermelho maiúsculo + barra fina vermelha centrada. */
.titulo-com-linha { margin: 0 0 32px; }
.titulo-com-linha h1 {
  color: var(--accent); font-size: clamp(28px, 4.2vw, 46px); font-weight: 800;
  margin: 0 0 10px; text-transform: uppercase; letter-spacing: 0.01em;
}
.titulo-com-linha .linha { width: 260px; max-width: 55vw; height: 4px; background: var(--accent); margin: 0 auto; border-radius: 2px; }

/* Ilustração "quatro peças se encaixando" (substitui a foto de banco de
   imagens do PPT original) — grade 2x2 nas cores da marca, cada peça com um
   canto arredondado maior apontando pra fora, sugerindo encaixe. */
.novos-colab-img {
  display: grid; grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(2, 1fr);
  gap: 10px; width: 300px; height: 300px; max-width: 60vw; max-height: 60vw;
}
.novos-colab-img .peca { box-shadow: 0 10px 24px rgba(26,26,26,0.18); }
.novos-colab-img .peca:nth-child(1) { background: var(--accent); border-radius: 22px 22px 22px 64px; }
.novos-colab-img .peca:nth-child(2) { background: var(--ink); border-radius: 22px 22px 64px 22px; }
.novos-colab-img .peca:nth-child(3) { background: var(--gold); border-radius: 22px 64px 22px 22px; }
.novos-colab-img .peca:nth-child(4) { background: var(--ink-soft); border-radius: 64px 22px 22px 22px; }

/* Evolução Anual GYN — réplica dos slides de tabela mensal: logos T&T nos
   dois cantos superiores, título vermelho centralizado, e a tabela do ano
   (faturamento ou indicadores operacionais) igual à planilha do PowerPoint. */
.slide.evolucao { justify-content: flex-start; padding-top: 34px; }
.evolucao-logo { position: absolute; top: 14px; }
.evolucao-logo.esq { left: 20px; }
.evolucao-logo.dir { right: 20px; }
.evolucao-logo img {
  width: 92px; height: auto; max-width: 16vw;
  filter: drop-shadow(0 8px 14px rgba(26,26,26,0.3));
}
.evolucao-titulo {
  color: var(--accent); font-weight: 800; text-transform: uppercase;
  font-size: clamp(22px, 3vw, 36px); margin: 0 0 16px;
}
.tabela-evolucao {
  width: 100%; max-width: 980px; border-collapse: collapse;
  font-size: clamp(10.5px, 1.05vw, 13px);
}
.tabela-evolucao caption {
  background: var(--good); color: #fff; font-weight: 800; padding: 7px;
  text-transform: uppercase; letter-spacing: 0.03em; caption-side: top;
}
.tabela-evolucao th {
  background: var(--surface-2); border: 1px solid var(--border);
  padding: 5px 7px; font-weight: 800; text-transform: uppercase; font-size: 0.82em;
}
.tabela-evolucao td {
  border: 1px solid var(--border); padding: 4px 7px; text-align: center;
  font-variant-numeric: tabular-nums;
}
.tabela-evolucao td.mes, .tabela-evolucao th:first-child { text-align: left; font-weight: 700; }
.tabela-evolucao td.neg { color: var(--accent); font-weight: 700; }
.tabela-evolucao tr.total td { background: var(--good); color: #fff; font-weight: 800; }

/* Resultado 4 Pilares — divisor do bloco (réplica do slide "TIME T&T
   GYN"): logos Friato/T&T nos cantos, subtítulo vermelho, nome do time
   gigante, e a fileira de brasões das equipes dos supervisores embaixo. */
.slide.pilares-capa { justify-content: flex-start; padding-top: 34px; padding-bottom: 22px; }
.slide.pilares-capa .emblemas-row { margin-top: auto; }
.pilares-capa .logo-topo { position: absolute; top: 20px; }
.pilares-capa .logo-topo.esq { left: 24px; }
.pilares-capa .logo-topo.dir { right: 24px; }
.pilares-capa .logo-topo img { height: 62px; width: auto; filter: drop-shadow(0 6px 12px rgba(26,26,26,0.25)); }
.pilares-capa-meio { display: flex; flex-direction: column; align-items: center; }
.pilares-capa .subtitulo {
  color: var(--accent); font-weight: 800; text-transform: uppercase;
  font-size: clamp(18px, 2.3vw, 28px); margin: 0 0 4px;
}
.pilares-capa .titulo-time {
  color: #EE0000; font-weight: 900; text-transform: uppercase; line-height: 1.05;
  font-size: clamp(32px, 5.6vw, 62px); margin: 0;
}
.emblemas-row {
  display: flex; gap: 18px; align-items: center; justify-content: center; flex-wrap: wrap;
  width: 100%; max-width: 1040px; padding: 20px; box-sizing: border-box;
  border: 1px solid var(--border); border-radius: 16px; background: var(--surface-2);
}
.emblemas-row .emblema {
  width: clamp(90px, 12vw, 150px); height: clamp(90px, 12vw, 150px); border-radius: 14px; background: #fff;
  box-shadow: 0 4px 14px rgba(26,26,26,0.2); border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.emblemas-row .emblema img { width: 100%; height: 100%; object-fit: contain; }

/* Divisor de cada supervisor (réplica dos slides "SUPERVISOR X"): fundo
   escuro gradiente (era um degradê preto->teal gerado pelo Designer do
   PowerPoint), título branco, e o trio foto do supervisor + logo Friato +
   brasão da equipe. */
.slide.supervisor-capa { background: linear-gradient(135deg, #04141f 0%, #0b3a52 55%, #156082 100%); }
.supervisor-capa h1 { color: #fff; font-size: clamp(26px, 3.8vw, 44px); font-weight: 800; text-transform: uppercase; margin: 0 0 36px; }
.supervisor-capa .trio { display: flex; align-items: center; justify-content: center; gap: 32px; flex-wrap: wrap; margin-bottom: 30px; }
.supervisor-capa .quadro {
  width: 180px; height: 180px; border-radius: 16px; background: #fff; overflow: hidden;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}
.supervisor-capa .quadro img { width: 100%; height: 100%; object-fit: cover; }
.supervisor-capa .quadro.contido img { object-fit: contain; padding: 14px; }
.supervisor-capa .quadro-fallback {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  font-size: 56px; font-weight: 800; background: var(--surface-2); color: var(--ink-soft);
}
.supervisor-capa .subtitulo-nome { color: #fff; font-weight: 800; text-transform: uppercase; font-size: clamp(18px, 2.2vw, 26px); }

/* Slide individual de cada RCA (réplica das telas "RCA: X - NOME" do
   PowerPoint) — mesmo padrão visual de barras do Painel do Gerente
   (painel_pilares), com foto do vendedor, logo Friato e brasão da equipe. */
.slide.rca-slide { justify-content: flex-start; padding-top: 14px; }
.rca-topo { position: relative; width: 100%; display: flex; align-items: center; justify-content: center; margin-bottom: 2px; }
.rca-topo img { position: absolute; height: 64px; width: auto; }
.rca-topo .rca-logo-friato { left: 0; }
.rca-topo .rca-emblema { right: 0; height: 78px; }
.rca-titulo { color: var(--accent); font-size: clamp(16px, 2vw, 24px); font-weight: 800; text-transform: uppercase; margin: 0; }
.rca-perfil { display: flex; flex-direction: column; align-items: center; margin: 8px 0 12px; }
.rca-perfil .avatar {
  width: 108px; height: 108px; border-radius: 50%; object-fit: cover;
  border: 4px solid var(--gold); box-shadow: 0 4px 12px rgba(26,26,26,0.2);
}
.rca-perfil .avatar-fallback {
  width: 108px; height: 108px; border-radius: 50%; border: 4px solid var(--gold);
  display: flex; align-items: center; justify-content: center;
  font-size: 36px; font-weight: 800; background: var(--surface-2); color: var(--ink-soft);
}
.rca-perfil .rca-nome { font-weight: 800; font-size: clamp(15px, 1.8vw, 20px); margin-top: 6px; }
.rca-perfil .rca-sub { color: var(--ink-soft); font-size: 12px; }
.rca-pilares { width: 100%; max-width: 600px; display: flex; flex-direction: column; gap: 8px; }
.rca-stat {
  width: 100%; max-width: 600px; display: flex; justify-content: space-between;
  font-weight: 800; font-size: 14px; margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--border);
}
.pilar-linha .topo { display: flex; justify-content: space-between; align-items: baseline; font-weight: 800; font-size: 13px; }
.pilar-linha .track { height: 8px; border-radius: 999px; background: var(--surface-2); overflow: hidden; margin: 4px 0 2px; }
.pilar-linha .fill { height: 100%; border-radius: 999px; }
.pilar-linha .sub { font-size: 14px; font-weight: 700; color: var(--ink-soft); }
.rca-rodape { color: var(--accent); font-weight: 800; text-transform: uppercase; margin-top: 12px; font-size: clamp(13px, 1.5vw, 17px); }

/* Legenda "RECOMPRA" — regra fixa de leitura das tabelas de recompra por
   equipe (>=30% grave, 20-29% precisa baixar, <20% no caminho do ideal). */
.recompra-legenda-lista { width: 100%; max-width: 820px; display: flex; flex-direction: column; gap: 34px; }
.recompra-legenda-linha { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; font-weight: 800; font-size: clamp(15px, 1.9vw, 22px); text-align: left; color: var(--ink); }
.recompra-legenda-linha .bullet { font-size: 1.4em; }
.recompra-legenda-linha .badge { padding: 2px 12px; border-radius: 4px; }
.recompra-legenda-linha .badge.bad { background: var(--bad); color: #fff; }
.recompra-legenda-linha .valor.bad { color: var(--bad); }
.recompra-legenda-linha .valor.warn { color: var(--bad); }
.recompra-legenda-linha .msg.bad { color: var(--bad); }
.recompra-legenda-linha .msg.warn { color: var(--warn); }
.recompra-legenda-linha .msg.good, .recompra-legenda-linha .valor.good { color: var(--good); }

/* Comissão Extra de 2% Thermoprocessado — ranking dos RCAs que bateram o
   prêmio (thermo.premio > 0), puxado direto do painel_pilares. Layout de
   2 colunas (título à esquerda, tabela à direita), igual ao slide original. */
.slide.comissao { justify-content: flex-start; padding-top: 30px; }
.comissao-corpo { display: flex; flex-direction: column; align-items: center; gap: 22px; width: 100%; }
.comissao-titulo { text-align: center; margin-bottom: 4px; }
.comissao-titulo div { font-weight: 800; font-size: clamp(18px, 2.2vw, 28px); color: var(--ink); text-transform: uppercase; line-height: 1.15; letter-spacing: 0.03em; }
.comissao-titulo .pct-destaque { color: var(--good); font-size: clamp(22px, 2.8vw, 34px); }
.comissao-titulo::after {
  content: ""; display: block; width: 60px; height: 4px; border-radius: 2px; margin: 14px auto 0;
  background: linear-gradient(90deg, var(--good), var(--gold));
}
.tabela-comissao {
  width: 100%; max-width: 760px; border-collapse: separate; border-spacing: 0;
  font-size: clamp(10.5px, 1vw, 13px); border-radius: 14px; overflow: hidden;
  box-shadow: 0 6px 22px rgba(26,26,26,0.1); border: 1px solid var(--border);
}
.tabela-comissao th {
  background: linear-gradient(135deg, var(--good), #147a4b); color: #fff; border: none; padding: 10px 14px;
  text-transform: uppercase; font-weight: 800; text-align: left; letter-spacing: 0.02em;
}
.tabela-comissao td { border: none; border-top: 1px solid var(--border); padding: 8px 14px; }
.tabela-comissao tbody tr:nth-child(even) { background: var(--surface-2); }
.tabela-comissao tbody tr:hover { background: var(--creme); }
.tabela-comissao td.cod { text-align: center; font-weight: 700; color: var(--ink-soft); }
.tabela-comissao td.valor { text-align: right; font-weight: 800; color: var(--good); font-variant-numeric: tabular-nums; }

/* Recompra por equipe — réplica das tabelas "RECOMPRA EQUIPE X": >=30%
   grave (destaque vermelho), 20-29% atenção (texto vermelho simples),
   <20% no caminho (destaque verde) — regra do slide "RECOMPRA" do PPT. */
.recompra-titulo { color: #1A1A1A; font-weight: 800; text-transform: uppercase; font-size: clamp(22px, 3vw, 36px); margin: 0 0 24px; }
.tabela-recompra { width: 100%; max-width: 820px; border-collapse: collapse; font-size: clamp(12px, 1.2vw, 16px); border: 2px solid #1A1A1A; }
.tabela-recompra th, .tabela-recompra td { border: 1px solid #1A1A1A; padding: 8px 14px; text-align: center; }
.tabela-recompra th { color: #1B3A8C; font-weight: 800; background: #fff; }
.tabela-recompra th:first-child, .tabela-recompra td.nome-col { text-align: left; color: #1A1A1A; font-weight: 800; }
.tabela-recompra td.pct { color: var(--accent); font-weight: 800; }
.tabela-recompra td.pct.alerta { background: #F7C9C9; }
.tabela-recompra td.pct.baixo { background: #C9F0D8; }
.tabela-recompra tr.total td { font-weight: 800; }
.sem-ganhadores {
  margin-top: 12px; display: flex; flex-direction: column; align-items: center; gap: 14px;
  background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
  padding: 44px 60px; box-shadow: 0 10px 30px rgba(26,26,26,0.08);
}
.sem-ganhadores .icone-vazio {
  width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: var(--surface-2); font-size: 26px;
}
.sem-ganhadores .texto-vazio {
  font-weight: 800; font-size: clamp(18px, 2.2vw, 26px); color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.02em;
}
.sem-ganhadores .sub-vazio { font-size: 13px; color: var(--ink-faint); font-weight: 600; text-transform: none; }

/* Divisor "Realizado Departamentos" — título vermelho em 2 linhas + foto
   real dos produtos Friato (extraída do PowerPoint) ocupando a metade
   inferior do slide, igual ao original. */
.slide.departamentos-capa { padding: 0; justify-content: flex-start; }
.departamentos-capa .logo-topo { position: absolute; top: 20px; z-index: 2; }
.departamentos-capa .logo-topo.esq { left: 24px; }
.departamentos-capa .logo-topo.dir { right: 24px; }
.departamentos-capa .logo-topo img { height: 60px; width: auto; filter: drop-shadow(0 6px 12px rgba(26,26,26,0.25)); }
.departamentos-capa .titulo-wrap { padding: 60px 8vw 30px; text-align: center; }
.departamentos-capa h1 {
  color: var(--accent); font-weight: 800; text-transform: uppercase; line-height: 1.18;
  font-size: clamp(22px, 3.4vw, 40px); margin: 0;
}
.departamentos-capa .foto-produtos { width: 100%; flex: 1; overflow: hidden; }
.departamentos-capa .foto-produtos img { width: 100%; height: 100%; object-fit: cover; display: block; }

/* Equipe X — Realizado Departamentos: tabela larga com uma coluna por
   categoria (mínimo no cabeçalho, cor por bateu/não bateu). */
.tabela-departamentos { width: 100%; max-width: 1150px; border-collapse: collapse; font-size: clamp(12px, 1.1vw, 16px); }
.tabela-departamentos th, .tabela-departamentos td { border: 1px solid var(--border); padding: 7px 9px; text-align: center; }
.tabela-departamentos thead tr.linha-minimo th { color: var(--accent); font-weight: 800; border: 2px solid var(--accent); background: #fff; }
.tabela-departamentos thead tr.linha-categoria th { background: var(--surface-2); font-weight: 800; text-transform: uppercase; }
.tabela-departamentos td.nome-col, .tabela-departamentos th.corner { text-align: left; font-weight: 800; }
.tabela-departamentos td.bateu { color: var(--good); font-weight: 800; background: #E1F5EA; }
.tabela-departamentos td.nao-bateu { color: var(--bad); font-weight: 800; background: #FBE1DF; }
.tabela-departamentos tr.total td { background: var(--surface-2); font-weight: 800; }

/* Divisor "Vendedor Destaque" — painel dividido: texto à esquerda, e à
   direita uma composição (círculo dourado + troféu) no lugar da foto de
   banco de imagens datada do PowerPoint original. */
.slide.destaque-capa { padding: 0; justify-content: flex-start; align-items: flex-start; text-align: left; position: relative; overflow: hidden; }
.destaque-capa-arte {
  position: absolute; inset: 0; background: var(--accent);
  clip-path: polygon(40% 0, 100% 0, 100% 100%, 26% 100%);
  display: flex; align-items: center; justify-content: center;
}
.destaque-capa-circulo {
  position: absolute; width: 56%; aspect-ratio: 1; border-radius: 50%; background: var(--gold);
  right: 6%; top: 50%; transform: translateY(-50%);
}
.destaque-capa-foto { position: relative; z-index: 2; height: 92%; max-height: 640px; width: auto; object-fit: contain; }
.destaque-capa-texto { position: relative; z-index: 2; max-width: 50%; padding: 64px 4vw 40px 6vw; }
.destaque-capa-texto h1 { font-size: clamp(26px, 3.6vw, 46px); font-weight: 800; text-transform: uppercase; margin: 0 0 8px; color: var(--ink); line-height: 1.1; }
.destaque-capa-texto .subtitulo { font-size: clamp(14px, 1.8vw, 21px); font-weight: 800; text-transform: uppercase; margin: 0 0 30px; color: var(--ink); }
.destaque-capa-lista { list-style: none; padding: 0; margin: 0 0 40px; display: flex; flex-direction: column; gap: 18px; }
.destaque-capa-lista li { font-size: clamp(14px, 1.6vw, 20px); font-weight: 800; color: var(--ink); }
.destaque-capa-lista li::before { content: "✦ "; color: var(--accent); }
.destaque-capa-texto .logo-friato-rodape img { height: 50px; width: auto; }

/* Prêmio (Jantar Exclusivo etc.) — título preto itálico com sombra tipo
   "gravado", logos Friato nos dois cantos, logo do prêmio centralizada. */
.slide.premio-capa { justify-content: flex-start; padding-top: 30px; }
.premio-capa .logo-topo { position: absolute; top: 20px; }
.premio-capa .logo-topo.esq { left: 26px; }
.premio-capa .logo-topo.dir { right: 26px; }
.premio-capa .logo-topo img { height: 62px; width: auto; }
.premio-titulo {
  font-weight: 800; font-style: italic; text-transform: uppercase; color: #1A1A1A;
  font-size: clamp(24px, 3.4vw, 40px); text-align: center; line-height: 1.2; margin: 8px 0 40px;
  text-shadow: 2px 3px 3px rgba(26,26,26,0.35);
}
.premio-logo { max-width: 380px; width: 44%; height: auto; filter: drop-shadow(0 10px 20px rgba(26,26,26,0.15)); }

/* Grade 2x2 do prêmio (ambiente do restaurante): fotos reais extraídas do
   PowerPoint, logos nos quadrantes brancos. O quadrante do buffet corta a
   faixa de marca d'água do rodapé da foto original. */
.slide.premio-grade { padding: 0; }
.premio-grid { width: 100%; height: 100%; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; }
.premio-grid .quadro { display: flex; align-items: center; justify-content: center; overflow: hidden; background: #fff; position: relative; }
.premio-grid .quadro img.foto { width: 100%; height: 100%; object-fit: cover; }
.premio-grid .quadro.buffet img.foto { object-position: 50% 8%; transform: scale(1.1); }
.premio-grid .quadro img.marca { max-width: 62%; max-height: 55%; object-fit: contain; }

/* Sequência "Resultado / Vendedor Destaque" — cabeçalho com logo T&T à
   esquerda e Friato à direita, título preto, e uma onda vermelha cobrindo
   a parte de baixo do slide (réplica do PowerPoint). */
.slide.resultado-onda-slide { padding: 0; }
.resultado-onda-inner {
  position: relative; overflow: hidden; width: 100%; height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
}
.resultado-onda { position: absolute; left: -20%; width: 140%; top: 27vh; height: 100vh; border-radius: 50%; background: var(--accent); }
.resultado-cabecalho { position: relative; z-index: 2; width: 100%; display: flex; align-items: center; justify-content: center; padding: 14px 6vw 0; flex: 0 0 auto; }
.resultado-cabecalho .logo-tt { position: absolute; left: 22px; top: 10px; height: 92px; width: auto; }
.resultado-cabecalho .logo-friato { position: absolute; right: 22px; top: 10px; height: 86px; width: auto; }
.resultado-cabecalho h1 { color: #1A1A1A; font-weight: 800; text-transform: uppercase; font-size: clamp(28px, 3.6vw, 44px); margin: 0; }
.resultado-subtitulo {
  position: relative; z-index: 2; text-align: center; font-family: "Roboto Slab", Georgia, serif;
  font-style: italic; font-weight: 800; color: var(--accent); text-decoration: underline;
  text-decoration-color: var(--accent); font-size: clamp(22px, 3.2vw, 36px); margin: 8px 0 20px;
}
.resultado-corpo { position: relative; z-index: 2; width: 100%; display: flex; align-items: center; justify-content: center; gap: 34px; flex-wrap: wrap; padding: 0 5vw; margin-top: 10px; }
.tabela-resultado { border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; font-size: clamp(16px, 1.7vw, 22px); box-shadow: 0 10px 26px rgba(0,0,0,0.25); }
.tabela-resultado th { background: #111; color: #fff; padding: 14px 26px; text-transform: uppercase; font-weight: 800; }
.tabela-resultado td { padding: 13px 26px; text-align: center; border: 1px solid #ddd; font-weight: 700; }
.tabela-resultado td.pct { background: #A9E8B4; font-weight: 800; }
.tabela-resultado tr.media td { background: var(--good); color: #fff; font-weight: 800; }
.tabela-resultado tr.media td.pct { background: #111; color: #fff; }
.resultado-vazio {
  position: relative; z-index: 2; background: #fff; border-radius: 16px; padding: 30px 44px;
  font-weight: 800; text-transform: uppercase; color: var(--ink-soft); text-align: center;
  font-size: clamp(16px, 2vw, 22px); box-shadow: 0 10px 26px rgba(0,0,0,0.2);
}
.badge-vendedor { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.badge-vendedor .anel {
  width: 190px; height: 190px; border-radius: 50%; background: var(--gold);
  display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 26px rgba(0,0,0,0.25); position: relative;
}
.badge-vendedor .anel img.foto-vendedor { width: 76%; height: 76%; border-radius: 50%; object-fit: cover; border: 4px solid #fff; }
.badge-vendedor .anel .foto-fallback {
  width: 76%; height: 76%; border-radius: 50%; border: 4px solid #fff; background: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 44px; font-weight: 800; color: var(--ink-soft);
}
.badge-vendedor .anel .logo-mini { position: absolute; top: 4px; left: 4px; height: 30px; width: auto; background: #fff; border-radius: 50%; padding: 3px; }
.badge-vendedor .legenda {
  background: #fff; border-radius: 999px; padding: 6px 18px; font-weight: 800; font-size: 12px;
  text-transform: uppercase; color: var(--ink); box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.estrategia-alvo { position: relative; width: 220px; height: 220px; display: flex; align-items: center; justify-content: center; }
.estrategia-alvo .anel-alvo { position: absolute; border-radius: 50%; border: 10px solid rgba(255,255,255,0.9); }
.estrategia-alvo .anel-1 { width: 220px; height: 220px; }
.estrategia-alvo .anel-2 { width: 150px; height: 150px; border-color: rgba(255,255,255,0.7); }
.estrategia-alvo .anel-3 { width: 80px; height: 80px; background: #fff; border: none; }
.estrategia-alvo .dardo { position: absolute; width: 90px; top: 50%; left: 50%; transform: translate(-20%, -50%) rotate(-8deg); filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4)); }
.resultado-banner {
  position: relative; z-index: 2; width: 100%; text-align: center; color: #fff; font-weight: 800;
  text-transform: uppercase; font-size: clamp(18px, 2.6vw, 30px); padding: 18px 0 30px;
}

/* Positivação Dia 15 e Dia 30 — slide de regras (texto fixo, sem dados
   variáveis): título verde, logos T&T nos cantos, 3 linhas com ícone +
   explicação, igual ao original. */
.regras-titulo { color: var(--good); font-weight: 800; text-transform: uppercase; font-size: clamp(20px, 2.8vw, 34px); margin: 0 0 26px; }
.regras-lista { width: 100%; max-width: 880px; display: flex; flex-direction: column; gap: 16px; }
.regra-linha { display: flex; align-items: center; gap: 20px; background: var(--surface-2); border-radius: 14px; padding: 16px 28px; }
.regra-linha .icone {
  width: 54px; height: 54px; border: 2px solid var(--border); border-radius: 10px; background: #fff;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.regra-linha .icone svg { width: 30px; height: 30px; stroke: #2E5F7A; fill: none; }
.regra-linha .texto { font-weight: 800; font-size: clamp(14px, 1.7vw, 20px); text-align: left; color: var(--ink); }

/* Destaque (vendedor/supervisor) */
.destaque-card {
  display: flex; flex-direction: column; align-items: center; gap: 18px;
}
.destaque-foto {
  width: 168px; height: 168px; border-radius: 50%; border: 4px solid var(--gold);
  object-fit: cover; box-shadow: 0 0 0 8px rgba(231,178,59,0.12);
}
.destaque-foto-fallback {
  width: 168px; height: 168px; border-radius: 50%; border: 4px solid var(--gold);
  box-shadow: 0 0 0 8px rgba(231,178,59,0.12);
  display: flex; align-items: center; justify-content: center;
  font-size: 56px; font-weight: 800; background: var(--surface-2); color: var(--ink-soft);
}
.destaque-nome { font-size: clamp(30px, 4.4vw, 50px); font-weight: 800; }
.destaque-sub { color: var(--ink-soft); font-size: 16px; margin-top: -8px; }
.destaque-motivo {
  max-width: 640px; font-size: 18px; color: var(--ink-soft); line-height: 1.5;
  background: var(--creme); border: 1px solid var(--gold); border-radius: 16px; padding: 20px 26px; margin-top: 10px;
  box-shadow: 0 2px 10px rgba(26,26,26,0.06);
}
.trofeu { font-size: 44px; margin-bottom: -6px; }

/* Navegação */
.nav-dots { position: fixed; bottom: 26px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; z-index: 20; }
.nav-dots .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--border); cursor: pointer; transition: background 0.2s, transform 0.2s; }
.nav-dots .dot.active { background: var(--accent); transform: scale(1.3); }
.nav-arrow {
  position: fixed; top: 50%; transform: translateY(-50%); z-index: 20;
  width: 44px; height: 44px; border-radius: 50%; border: 1px solid var(--border);
  background: var(--surface); color: var(--ink-soft); display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 20px; box-shadow: 0 2px 10px rgba(26,26,26,0.08);
}
.nav-arrow:hover { color: var(--ink); border-color: var(--accent); }
.nav-arrow.prev { left: 20px; }
.nav-arrow.next { right: 20px; }
.slide-counter { position: fixed; top: 20px; right: 24px; color: var(--ink-faint); font-size: 13px; font-weight: 700; z-index: 20; }

@media (max-width: 700px) {
  .nav-arrow { display: none; }
}
</style>
</head>
<body>

<div class="slides" id="slides"></div>
<button class="nav-arrow prev" id="btnPrev">&larr;</button>
<button class="nav-arrow next" id="btnNext">&rarr;</button>
<div class="nav-dots" id="dots"></div>
<div class="slide-counter" id="counter"></div>

<script>
const DADOS = __DADOS_JSON__;
const FOTOS_SUPERVISORES = __FOTOS_SUPERVISORES_JSON__;
const FOTOS_RCAS = __FOTOS_RCAS_JSON__;
const EMBLEMAS = __EMBLEMAS_JSON__;

function normalizarNomeFoto(nome) {
  return (nome || "").replace(/\s*-\s*$/, "").trim().toUpperCase();
}
function fmtPct(v) { return (v * 100).toLocaleString("pt-BR", { maximumFractionDigits: 0 }) + "%"; }
function fmtNum1(v) { return v.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }); }
function iniciais(nome) {
  return (nome || "").split(/\s+/).filter(Boolean).slice(0, 2).map(p => p[0]).join("").toUpperCase();
}

function slideCapa() {
  const partesMes = (DADOS.mes || "").split(" ");
  const mesNome = (partesMes[0] || "").toUpperCase();
  const ano = partesMes[1] || "";
  return `
    <div class="slide capa active">
      <h1 class="capa-titulo">
        <span class="capa-linha">REUNIÃO DE FECHAMENTO</span>
        <span class="capa-linha">${mesNome}</span>
        <span class="capa-linha ano">${ano}</span>
      </h1>
      <div class="logo-anel"><img src="__LOGO_URI__" alt="T&amp;T Alimentos"></div>
    </div>`;
}

function slideCronograma() {
  return `
    <div class="slide divisor">
      <div class="divisor-faixa"><h1>Cronograma da Reunião</h1></div>
    </div>`;
}

function slideNovosColaboradores() {
  return `
    <div class="slide">
      <div class="titulo-com-linha">
        <h1>Novos Colaboradores</h1>
        <div class="linha"></div>
      </div>
      <div class="novos-colab-img">
        <div class="peca"></div><div class="peca"></div><div class="peca"></div><div class="peca"></div>
      </div>
    </div>`;
}

function fmtMoeda(v) {
  return "R$ " + Math.abs(v).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function celMoeda(v) {
  if (v === null || v === undefined) return `<td></td>`;
  const neg = v < 0;
  return `<td class="${neg ? "neg" : ""}">${neg ? "(" + fmtMoeda(v) + ")" : fmtMoeda(v)}</td>`;
}
function celPct(v) {
  if (v === null || v === undefined) return `<td></td>`;
  const txt = (v * 100).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
  return `<td class="${v < 0 ? "neg" : ""}">${txt}</td>`;
}
function celNum(v) {
  if (v === null || v === undefined) return `<td></td>`;
  return `<td class="${v < 0 ? "neg" : ""}">${v.toLocaleString("pt-BR")}</td>`;
}
function celPreco(v) {
  if (v === null || v === undefined) return `<td></td>`;
  return `<td>R$ ${v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>`;
}
function logosEvolucao(uriEsq, uriDir) {
  uriEsq = uriEsq || "__LOGO_URI__";
  uriDir = uriDir || "__LOGO_URI__";
  return `
    <div class="evolucao-logo esq"><img src="${uriEsq}" alt="T&amp;T Alimentos"></div>
    <div class="evolucao-logo dir"><img src="${uriDir}" alt="T&amp;T Alimentos"></div>`;
}

function slideEvolucaoFaturamento() {
  const linhas = DADOS.evolucao_faturamento || [];
  const total = DADOS.evolucao_total_faturamento || {};
  if (!linhas.length) return "";
  const rows = linhas.map(m => `
    <tr>
      <td class="mes">${m.mes.toUpperCase()}</td>
      ${celMoeda(m.meta)}
      ${celMoeda(m.faturamento)}
      ${celPct(m.pct_meta)}
      ${celMoeda(m.saldo_meta)}
    </tr>`).join("");
  return `
    <div class="slide evolucao">
      ${logosEvolucao()}
      <h1 class="evolucao-titulo">Evolução Anual GYN</h1>
      <table class="tabela-evolucao">
        <caption>Faturamento 2026</caption>
        <thead><tr><th>Mês</th><th>Meta 2025</th><th>Faturamento</th><th>% Meta</th><th>Saldo Meta</th></tr></thead>
        <tbody>
          ${rows}
          <tr class="total">
            <td class="mes">TOTAL</td>
            ${celMoeda(total.meta)}
            ${celMoeda(total.faturamento)}
            ${celPct(total.pct_meta)}
            ${celMoeda(total.saldo_meta)}
          </tr>
        </tbody>
      </table>
    </div>`;
}

function slideEvolucaoOperacional() {
  const linhas = DADOS.evolucao_operacional || [];
  const total = DADOS.evolucao_total_operacional || {};
  if (!linhas.length) return "";
  const rows = linhas.map(m => `
    <tr>
      <td class="mes">${m.mes.toUpperCase()}</td>
      ${celPct(m.margem_pct)}
      ${celNum(m.peso)}
      ${celPreco(m.preco_medio)}
      ${celPct(m.variacao_pct)}
      ${celNum(m.cli_atendidos)}
      ${celNum(m.cresc_mensal)}
    </tr>`).join("");
  return `
    <div class="slide evolucao">
      ${logosEvolucao()}
      <h1 class="evolucao-titulo">Evolução Anual GYN</h1>
      <table class="tabela-evolucao">
        <thead><tr><th>Mês</th><th>Margem</th><th>Peso</th><th>Preço Médio</th><th>Variação</th><th>Cli. Atendidos</th><th>Cresc. Mensal</th></tr></thead>
        <tbody>
          ${rows}
          <tr class="total">
            <td class="mes">TOTAL</td>
            ${celPct(total.margem_pct)}
            ${celNum(total.peso)}
            ${celPreco(total.preco_medio)}
            ${celPct(total.variacao_pct)}
            ${celNum(total.cli_atendidos)}
            ${celNum(total.cresc_mensal)}
          </tr>
        </tbody>
      </table>
    </div>`;
}

function slideResultado4PilaresCapa() {
  const ordem = ["gladiadores", "vencedores", "imperadores", "aguia", "invictus", "veteranos"];
  const emblemasHtml = ordem.map(nome => `<div class="emblema"><img src="${EMBLEMAS[nome]}" alt="${nome}"></div>`).join("");
  return `
    <div class="slide pilares-capa">
      <div class="logo-topo esq"><img src="__LOGO_FRIATO_URI__" alt="Friato Alimentos"></div>
      <div class="logo-topo dir"><img src="__LOGO_URI__" alt="T&amp;T Alimentos"></div>
      <div class="pilares-capa-meio">
        <div class="subtitulo">Resultado 4 Pilares</div>
        <div class="titulo-time">TIME T&amp;T<br>GYN</div>
      </div>
      <div class="emblemas-row">${emblemasHtml}</div>
    </div>`;
}

function slideSupervisorCapa(nome, emblemaChave) {
  const foto = FOTOS_SUPERVISORES[normalizarNomeFoto(nome)];
  const fotoHtml = foto
    ? `<div class="quadro"><img src="${foto}" alt="${nome}"></div>`
    : `<div class="quadro contido"><div class="quadro-fallback">${iniciais(nome)}</div></div>`;
  return `
    <div class="slide supervisor-capa">
      <h1>Resultado 4 Pilares</h1>
      <div class="trio">
        ${fotoHtml}
        <div class="quadro contido"><img src="__LOGO_FRIATO_URI__" alt="Friato Alimentos"></div>
        <div class="quadro contido"><img src="${EMBLEMAS[emblemaChave]}" alt="${emblemaChave}"></div>
      </div>
      <div class="subtitulo-nome">Supervisor ${nome}</div>
    </div>`;
}

function corPct(pct) {
  if (pct >= 1) return "good";
  if (pct >= 0.7) return "warn";
  return "bad";
}

function linhaPilar(label, p) {
  const cor = corPct(p.pct);
  const largura = Math.min(p.pct * 100, 100);
  return `
    <div class="pilar-linha">
      <div class="topo">
        <span>${label}</span>
        <span style="color:var(--${cor})">${fmtPct(p.pct)}</span>
      </div>
      <div class="track"><div class="fill" style="width:${largura}%;background:var(--${cor})"></div></div>
      <div class="sub">Meta ${p.meta.toLocaleString("pt-BR", { maximumFractionDigits: 2 })} · Realizado ${p.real.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}</div>
    </div>`;
}

function slideRcaPilares(rca, emblemaChave) {
  const foto = FOTOS_RCAS[normalizarNomeFoto(rca.nome)];
  const fotoHtml = foto
    ? `<img class="avatar" src="${foto}" alt="${rca.nome}">`
    : `<div class="avatar-fallback">${iniciais(rca.nome)}</div>`;
  return `
    <div class="slide rca-slide">
      <div class="rca-topo">
        <img class="rca-logo-friato" src="__LOGO_FRIATO_URI__" alt="Friato Alimentos">
        <h1 class="rca-titulo">Resultado 4 Pilares</h1>
        <img class="rca-emblema" src="${EMBLEMAS[emblemaChave]}" alt="${emblemaChave}">
      </div>
      <div class="rca-perfil">
        ${fotoHtml}
        <div class="rca-nome">${rca.nome}</div>
        <div class="rca-sub">RCA ${rca.codigo} · ${rca.rota}</div>
      </div>
      <div class="rca-pilares">
        ${linhaPilar("Financeiro", rca.pilares.financeiro)}
        ${linhaPilar("Margem", rca.pilares.margem)}
        ${linhaPilar("Mix", rca.pilares.mix)}
        ${linhaPilar("Positivação", rca.pilares.positivacao)}
      </div>
      <div class="rca-rodape">Supervisor ${rca.supervisor}</div>
    </div>`;
}

function _media(lista) {
  return lista.length ? lista.reduce((s, v) => s + v, 0) / lista.length : 0;
}

// Monta um "RCA" sintético com os totais do time — mesmo cálculo do
// Painel do Gerente (painel_pilares/gerar_painel.py: agregarTime).
function agregarTime(rcas, nomeSupervisor) {
  const somarMeta = campo => rcas.reduce((s, r) => s + r.pilares[campo].meta, 0);
  const somarReal = campo => rcas.reduce((s, r) => s + r.pilares[campo].real, 0);
  const pilar = campo => {
    const meta = somarMeta(campo);
    const real = somarReal(campo);
    return { meta, real, pct: meta ? real / meta : 0 };
  };
  const pilarMedia = campo => {
    const meta = somarMeta(campo) / (rcas.length || 1);
    const real = somarReal(campo) / (rcas.length || 1);
    return { meta, real, pct: meta ? real / meta : 0 };
  };
  return {
    codigo: "EQUIPE",
    nome: nomeSupervisor,
    rota: `${rcas.length} RCA${rcas.length > 1 ? "s" : ""}`,
    supervisor: nomeSupervisor,
    pilares: {
      positivacao: pilar("positivacao"),
      margem: pilarMedia("margem"),
      mix: pilarMedia("mix"),
      financeiro: pilar("financeiro"),
    },
    recompra_pct: _media(rcas.map(r => r.recompra_pct)),
  };
}

// Regra oficial do slide "RECOMPRA": >=30% grave, 20-29% precisa baixar
// para 20%, <20% está no caminho dos 10% (o ideal).
function corRecompra(pct) {
  if (pct >= 0.3) return "bad";
  if (pct >= 0.2) return "warn";
  return "good";
}

function classeRecompra(pct) {
  if (pct >= 0.3) return "alerta";
  if (pct < 0.2) return "baixo";
  return "";
}

function slideEquipePilares(nomeSupervisor, emblemaChave) {
  const rcas = (DADOS.rcas_pilares || []).filter(r => r.supervisor === nomeSupervisor);
  if (!rcas.length) return "";
  const time = agregarTime(rcas, nomeSupervisor);
  const foto = FOTOS_SUPERVISORES[normalizarNomeFoto(nomeSupervisor)];
  const fotoHtml = foto
    ? `<img class="avatar" src="${foto}" alt="${nomeSupervisor}">`
    : `<div class="avatar-fallback">${iniciais(nomeSupervisor)}</div>`;
  return `
    <div class="slide rca-slide">
      <div class="rca-topo">
        <img class="rca-logo-friato" src="__LOGO_FRIATO_URI__" alt="Friato Alimentos">
        <h1 class="rca-titulo">Resultado 4 Pilares</h1>
        <img class="rca-emblema" src="${EMBLEMAS[emblemaChave]}" alt="${emblemaChave}">
      </div>
      <div class="rca-perfil">
        ${fotoHtml}
        <div class="rca-nome">${time.nome}</div>
        <div class="rca-sub">RCA Equipe · ${time.rota}</div>
      </div>
      <div class="rca-pilares">
        ${linhaPilar("Financeiro", time.pilares.financeiro)}
        ${linhaPilar("Margem", time.pilares.margem)}
        ${linhaPilar("Mix", time.pilares.mix)}
        ${linhaPilar("Positivação", time.pilares.positivacao)}
      </div>
      <div class="rca-stat"><span>Recompra</span><span style="color:var(--${corRecompra(time.recompra_pct)})">${fmtPct(time.recompra_pct)}</span></div>
      <div class="rca-rodape">Supervisor ${time.nome}</div>
    </div>`;
}

function slidesEquipeSupervisor(nomeSupervisor, emblemaChave) {
  const rcas = (DADOS.rcas_pilares || []).filter(r => r.supervisor === nomeSupervisor);
  return rcas.map(rca => slideRcaPilares(rca, emblemaChave));
}

function slideDepartamentosCapa() {
  const mesNome = (DADOS.mes || "").split(" ")[0].toUpperCase();
  return `
    <div class="slide departamentos-capa">
      <div class="logo-topo esq"><img src="__LOGO_URI__" alt="T&amp;T Alimentos"></div>
      <div class="logo-topo dir"><img src="__LOGO_URI__" alt="T&amp;T Alimentos"></div>
      <div class="titulo-wrap">
        <h1>Realizado Departamentos<br>${mesNome} por Supervisão</h1>
      </div>
      <div class="foto-produtos"><img src="__PRODUTOS_FRIATO_URI__" alt="Produtos Friato"></div>
    </div>`;
}

const CATEGORIAS_DEPARTAMENTOS = ["bacon", "bovino", "batata", "suino", "calabresa", "paes", "frescais", "lacteos", "thermo"];

function slideEquipeDepartamentos(supervisorChave, supervisorNome) {
  const rcas = (DADOS.rcas_departamentos || []).filter(r => r.supervisor === supervisorChave);
  if (!rcas.length) return "";
  const primeira = rcas[0].categorias;

  const linhaHtml = r => `
    <tr>
      <td class="nome-col">${r.codigo} - ${r.nome}</td>
      ${CATEGORIAS_DEPARTAMENTOS.map(c => {
        const cat = r.categorias[c];
        return `<td class="${cat.bateu ? "bateu" : "nao-bateu"}">${Math.round(cat.real)}</td>`;
      }).join("")}
    </tr>`;

  const totais = CATEGORIAS_DEPARTAMENTOS.map(c => rcas.reduce((s, r) => s + r.categorias[c].real, 0));

  return `
    <div class="slide evolucao">
      ${logosEvolucao()}
      <h1 class="recompra-titulo">Equipe ${supervisorNome}</h1>
      <table class="tabela-departamentos">
        <thead>
          <tr class="linha-minimo">
            <th class="corner">${supervisorNome}</th>
            ${CATEGORIAS_DEPARTAMENTOS.map(c => `<th>Mínimo ${Math.round(primeira[c].meta)}</th>`).join("")}
          </tr>
          <tr class="linha-categoria">
            <th class="corner">RCA · Vendedor</th>
            ${CATEGORIAS_DEPARTAMENTOS.map(c => `<th>${primeira[c].label}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${rcas.map(linhaHtml).join("")}
          <tr class="total">
            <td class="nome-col">TOTAL</td>
            ${totais.map(t => `<td>${Math.round(t)}</td>`).join("")}
          </tr>
        </tbody>
      </table>
    </div>`;
}

function slideRecompraLegenda() {
  return `
    <div class="slide evolucao">
      ${logosEvolucao()}
      <h1 class="recompra-titulo">Recompra</h1>
      <div class="recompra-legenda-lista">
        <div class="recompra-legenda-linha">
          <span class="bullet">•</span> ACIMA DE <span class="badge bad">30%</span>
          <span class="msg bad">GRAVE BAIXAR URGENTE!</span>
        </div>
        <div class="recompra-legenda-linha">
          <span class="bullet">•</span> DE <span class="valor warn">21%</span> A <span class="valor warn">29%</span>
          <span class="msg warn">BAIXA PARA 20%</span>
        </div>
        <div class="recompra-legenda-linha">
          <span class="bullet">•</span> ABAIXO DE <span class="valor good">20%</span>
          <span class="msg good">ESTÁ NO CAMINHO DOS 10%</span>
        </div>
      </div>
    </div>`;
}

function slideRecompraEquipe(supervisorChave, supervisorNome) {
  const rcas = (DADOS.rcas_pilares || []).filter(r => r.supervisor === supervisorChave);
  if (!rcas.length) return "";
  const mesNome = (DADOS.mes || "").split(" ")[0].toUpperCase();

  const linha = r => {
    const positivacao = Math.round(r.pilares.positivacao.real);
    const qtdRecompra = Math.round(r.recompra_pct * positivacao);
    return { codigoNome: `${r.codigo} - ${r.nome}${r.rota ? " - " + r.rota : ""}`, positivacao, qtdRecompra, pct: r.recompra_pct };
  };
  const linhas = rcas.map(linha);
  const totalPositivacao = linhas.reduce((s, l) => s + l.positivacao, 0);
  const totalRecompra = linhas.reduce((s, l) => s + l.qtdRecompra, 0);
  const totalPct = totalPositivacao ? totalRecompra / totalPositivacao : 0;

  const linhaHtml = l => `
    <tr>
      <td class="nome-col">${l.codigoNome}</td>
      <td>${l.positivacao}</td>
      <td>${l.qtdRecompra}</td>
      <td class="pct ${classeRecompra(l.pct)}">${fmtPct(l.pct)}</td>
    </tr>`;

  return `
    <div class="slide evolucao">
      ${logosEvolucao()}
      <h1 class="recompra-titulo">Recompra Equipe ${supervisorNome}</h1>
      <table class="tabela-recompra">
        <thead><tr><th>${supervisorNome}</th><th>Positivação</th><th>${mesNome}</th><th>%</th></tr></thead>
        <tbody>
          ${linhas.map(linhaHtml).join("")}
          <tr class="total">
            <td class="nome-col">TOTAL</td>
            <td>${totalPositivacao}</td>
            <td>${totalRecompra}</td>
            <td class="pct ${classeRecompra(totalPct)}">${fmtPct(totalPct)}</td>
          </tr>
        </tbody>
      </table>
    </div>`;
}

// Um bloco por supervisor: divisor -> cada RCA do time -> resumo do time
// (nessa ordem — o resumo fecha o bloco, é o último slide da equipe).
const SUPERVISORES = [
  { chave: "LEANDRO", nome: "Leandro", emblema: "gladiadores" },
  { chave: "RICARDO", nome: "Ricardo", emblema: "veteranos" },
  { chave: "RICHARD", nome: "Richard", emblema: "titans" },
  { chave: "RODRIGO", nome: "Rodrigo", emblema: "imperadores" },
  { chave: "IDEGLAN", nome: "Ideglan", emblema: "aguia" },
  { chave: "FLAVIANE", nome: "Flaviane", emblema: "falcao" },
];

function slidesBlocoSupervisor(sup) {
  return [
    slideSupervisorCapa(sup.nome, sup.emblema),
    ...slidesEquipeSupervisor(sup.chave, sup.emblema),
    slideEquipePilares(sup.chave, sup.emblema),
  ];
}

function fmtMoedaSimples(v) {
  return "R$ " + Number(v).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function slideComissaoThermo() {
  const ganhadores = (DADOS.rcas_pilares || [])
    .filter(r => r.thermo && r.thermo.premio > 0)
    .sort((a, b) => b.thermo.premio - a.thermo.premio);
  if (!ganhadores.length) return "";
  const linhas = ganhadores.map(r => `
    <tr>
      <td class="cod">${r.codigo}</td>
      <td>${r.nome} - ${r.rota}</td>
      <td class="valor">${fmtMoedaSimples(r.thermo.premio)}</td>
    </tr>`).join("");
  return `
    <div class="slide comissao">
      ${logosEvolucao("__LOGO_FRIATO_URI__", "__LOGO_FRIATO_URI__")}
      <div class="comissao-corpo">
        <div class="comissao-titulo">
          <div>Comissão Extra de</div>
          <div class="pct-destaque">2%</div>
          <div>Thermoprocessado</div>
        </div>
        <table class="tabela-comissao">
          <thead><tr><th>Codusu</th><th>Nome</th><th>G. Termo</th></tr></thead>
          <tbody>${linhas}</tbody>
        </table>
      </div>
    </div>`;
}

function slidePositivacaoDiaRegras() {
  const iconePessoas = `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`;
  const iconePlay = `<svg viewBox="0 0 24 24" fill="#2E5F7A" stroke="none"><polygon points="6,3 21,12 6,21"/></svg>`;
  const iconeDinheiro = `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/></svg>`;
  return `
    <div class="slide evolucao">
      ${logosEvolucao()}
      <h1 class="regras-titulo">Positivação Dia 15 e Dia 30</h1>
      <div class="regras-lista">
        <div class="regra-linha"><div class="icone">${iconePessoas}</div><div class="texto">Bater a positivação dia 15 = R$ 150,00</div></div>
        <div class="regra-linha"><div class="icone">${iconePlay}</div><div class="texto">Refazer a positivação do dia 16 a 30 + R$ 150,00</div></div>
        <div class="regra-linha"><div class="icone">${iconeDinheiro}</div><div class="texto">Total de R$ 300,00</div></div>
      </div>
    </div>`;
}

function slideGanhadoresPositivacao(campo, titulo) {
  const ganhadores = (DADOS.rcas_pilares || [])
    .filter(r => r[campo] && r[campo].premio > 0)
    .sort((a, b) => b[campo].premio - a[campo].premio);

  const corpo = ganhadores.length
    ? `<table class="tabela-comissao">
        <thead><tr><th>Codusu</th><th>Nome</th><th>Prêmio</th></tr></thead>
        <tbody>${ganhadores.map(r => `
          <tr>
            <td class="cod">${r.codigo}</td>
            <td>${r.nome} - ${r.rota}</td>
            <td class="valor">${fmtMoedaSimples(r[campo].premio)}</td>
          </tr>`).join("")}</tbody>
      </table>`
    : `<div class="sem-ganhadores">
        <div class="icone-vazio">🏆</div>
        <div class="texto-vazio">Sem ganhadores</div>
        <div class="sub-vazio">Ninguém bateu essa meta neste período</div>
      </div>`;

  return `
    <div class="slide evolucao">
      ${logosEvolucao("__LOGO_FRIATO_URI__", "__LOGO_FRIATO_URI__")}
      <div class="comissao-corpo">
        <div class="comissao-titulo"><div>${titulo}</div></div>
        ${corpo}
      </div>
    </div>`;
}

function slideVendedorDestaqueCapa() {
  return `
    <div class="slide destaque-capa">
      <div class="destaque-capa-arte">
        <div class="destaque-capa-circulo"></div>
        <img class="destaque-capa-foto" src="__VENDEDOR_TROFEU_URI__" alt="Vendedor Destaque">
      </div>
      <div class="destaque-capa-texto">
        <h1>Vendedor Destaque</h1>
        <div class="subtitulo">Melhor Perfomance 04 Pilares</div>
        <ul class="destaque-capa-lista">
          <li>Faturamento</li>
          <li>Positivação</li>
          <li>Mix Médio</li>
          <li>Margem</li>
        </ul>
        <div class="logo-friato-rodape"><img src="__LOGO_FRIATO_URI__" alt="Friato Alimentos"></div>
      </div>
    </div>`;
}

function slideJantarExclusivo() {
  return `
    <div class="slide premio-capa">
      <div class="logo-topo esq"><img src="__LOGO_FRIATO_URI__" alt="Friato Alimentos"></div>
      <div class="logo-topo dir"><img src="__LOGO_FRIATO_URI__" alt="Friato Alimentos"></div>
      <div class="premio-titulo">Jantar Exclusivo com<br>Acompanhante</div>
      <img class="premio-logo" src="__GRAMADO_URI__" alt="Gramado Churrascaria">
    </div>`;
}

function slidePremioAmbiente() {
  return `
    <div class="slide premio-grade">
      <div class="premio-grid">
        <div class="quadro"><img class="marca" src="__LOGO_FRIATO_URI__" alt="Friato Alimentos"></div>
        <div class="quadro"><img class="foto" src="__RESTAURANTE_INTERIOR_URI__" alt="Ambiente do restaurante"></div>
        <div class="quadro buffet"><img class="foto" src="__RESTAURANTE_BUFFET_URI__" alt="Buffet do restaurante"></div>
        <div class="quadro"><img class="marca" src="__LOGO_URI__" alt="T&amp;T Alimentos"></div>
      </div>
    </div>`;
}

function fmtPctResultado(v) {
  return (v * 100).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
}

function linhaResultado(label, valorMeta, valorReal, pct) {
  return `<tr><td>${label}</td><td>${valorMeta}</td><td>${valorReal}</td><td class="pct">${fmtPctResultado(pct)}</td></tr>`;
}

function tabelaResultado(vendedor) {
  const p = vendedor.pilares;
  const t = vendedor.tendencia;
  const linhas = [
    linhaResultado("Positivação", Math.round(p.positivacao.meta), Math.round(p.positivacao.real), p.positivacao.pct),
    linhaResultado("Margem", p.margem.meta.toFixed(2) + "%", p.margem.real.toFixed(2) + "%", p.margem.pct),
    linhaResultado("Mix", p.mix.meta.toFixed(2), p.mix.real.toFixed(2), p.mix.pct),
    linhaResultado("Faturamento R$ (Tendência)", fmtMoedaSimples(t.meta), fmtMoedaSimples(t.projetado), t.pct),
  ].join("");
  return `
    <table class="tabela-resultado">
      <thead><tr><th>Indicadores</th><th>Meta</th><th>Realizado</th><th>%</th></tr></thead>
      <tbody>
        ${linhas}
        <tr class="media"><td colspan="3">Média 04 Pilares</td><td class="pct">${fmtPctResultado(vendedor.media_4_pilares)}</td></tr>
      </tbody>
    </table>`;
}

function badgeVendedor(vendedor) {
  const foto = FOTOS_RCAS[normalizarNomeFoto(vendedor.nome)];
  const fotoHtml = foto
    ? `<img class="foto-vendedor" src="${foto}" alt="${vendedor.nome}">`
    : `<div class="foto-fallback">${iniciais(vendedor.nome)}</div>`;
  return `
    <div class="badge-vendedor">
      <div class="anel">
        <img class="logo-mini" src="__LOGO_URI__" alt="T&amp;T">
        ${fotoHtml}
      </div>
      <div class="legenda">Vendedor ${vendedor.nome} · RCA ${vendedor.codigo}</div>
    </div>`;
}

function resultadoCabecalho(titulo) {
  return `
    <div class="resultado-cabecalho">
      <img class="logo-tt" src="__LOGO_URI__" alt="T&amp;T Alimentos">
      <img class="logo-friato" src="__LOGO_FRIATO_URI__" alt="Friato Alimentos">
      <h1>${titulo}</h1>
    </div>`;
}

function slideResultadoDivisor() {
  return `
    <div class="slide resultado-onda-slide"><div class="resultado-onda-inner">
      ${resultadoCabecalho("Resultado")}
      <div class="resultado-onda"></div>
    </div></div>`;
}

function slideResultadoReveal(vendedor) {
  const corpo = vendedor
    ? tabelaResultado(vendedor)
    : `<div class="resultado-vazio">Ninguém bateu os 4 pilares ainda este mês</div>`;
  return `
    <div class="slide resultado-onda-slide"><div class="resultado-onda-inner">
      ${resultadoCabecalho("Resultado")}
      <div class="resultado-subtitulo">Vendedor Destaque Foi........</div>
      <div class="resultado-corpo">${corpo}</div>
      <div class="resultado-onda"></div>
    </div></div>`;
}

function slideVendedorDestaqueTabela(vendedor) {
  if (!vendedor) return "";
  return `
    <div class="slide resultado-onda-slide"><div class="resultado-onda-inner">
      ${resultadoCabecalho("Vendedor Destaque")}
      <div class="resultado-subtitulo">${vendedor.nome}</div>
      <div class="resultado-corpo">${tabelaResultado(vendedor)}${badgeVendedor(vendedor)}</div>
      <div class="resultado-onda"></div>
    </div></div>`;
}

function slideVendedorDestaqueEstrategia(vendedor) {
  if (!vendedor) return "";
  const alvo = `
    <div class="estrategia-alvo">
      <div class="anel-alvo anel-1"></div>
      <div class="anel-alvo anel-2"></div>
      <div class="anel-alvo anel-3"></div>
      <svg class="dardo" viewBox="0 0 100 30">
        <polygon points="0,15 70,8 70,22" fill="var(--accent)"/>
        <rect x="68" y="12" width="20" height="6" fill="#333"/>
        <polygon points="88,6 100,15 88,24" fill="#333"/>
      </svg>
    </div>`;
  return `
    <div class="slide resultado-onda-slide"><div class="resultado-onda-inner">
      ${resultadoCabecalho("Vendedor Destaque")}
      <div class="resultado-subtitulo">${vendedor.nome}</div>
      <div class="resultado-corpo">${badgeVendedor(vendedor)}${alvo}</div>
      <div class="resultado-onda"></div>
      <div class="resultado-banner">Estratégia do Campeão</div>
    </div></div>`;
}

function slideDestaque(chave, titulo, eImagemRca) {
  const d = DADOS[chave];
  if (!d || !d.nome) return "";
  const foto = eImagemRca ? FOTOS_RCAS[normalizarNomeFoto(d.nome)] : FOTOS_SUPERVISORES[normalizarNomeFoto(d.nome)];
  const fotoHtml = foto
    ? `<img class="destaque-foto" src="${foto}" alt="${d.nome}">`
    : `<div class="destaque-foto-fallback">${iniciais(d.nome)}</div>`;
  return `
    <div class="slide">
      <div class="trofeu">🏆</div>
      <div class="eyebrow">${titulo}</div>
      <div class="destaque-card">
        ${fotoHtml}
        <div class="destaque-nome">${d.nome}</div>
        ${d.supervisor ? `<div class="destaque-sub">Equipe ${d.supervisor}</div>` : ""}
        ${d.motivo ? `<div class="destaque-motivo">${d.motivo}</div>` : ""}
      </div>
    </div>`;
}

function montar() {
  const partes = [
    slideCapa(),
    slideCronograma(),
    slideNovosColaboradores(),
    slideEvolucaoFaturamento(),
    slideEvolucaoOperacional(),
    slideResultado4PilaresCapa(),
    ...SUPERVISORES.flatMap(slidesBlocoSupervisor),
    slideComissaoThermo(),
    slidePositivacaoDiaRegras(),
    slideGanhadoresPositivacao("positivacao_dia15", "Ganhadores Dia 15"),
    slideGanhadoresPositivacao("positivacao_dia30", "Ganhadores Dia 30"),
    slideRecompraLegenda(),
    ...SUPERVISORES.map(sup => slideRecompraEquipe(sup.chave, sup.nome)),
    slideDepartamentosCapa(),
    ...SUPERVISORES.map(sup => slideEquipeDepartamentos(sup.chave, sup.nome)),
    slideVendedorDestaqueCapa(),
    slideJantarExclusivo(),
    slidePremioAmbiente(),
    slideResultadoDivisor(),
    slideResultadoReveal(DADOS.vendedor_destaque_auto),
    slideVendedorDestaqueTabela(DADOS.vendedor_destaque_auto),
    slideVendedorDestaqueEstrategia(DADOS.vendedor_destaque_auto),
    slideDestaque("supervisor_destaque", "Supervisor Destaque", false),
  ].filter(Boolean);

  document.getElementById("slides").innerHTML = partes.join("");
  const slides = document.querySelectorAll(".slide");
  slides[0].classList.add("active");

  const dotsEl = document.getElementById("dots");
  dotsEl.innerHTML = Array.from(slides).map((_, i) => `<div class="dot ${i === 0 ? "active" : ""}" data-i="${i}"></div>`).join("");

  let atual = 0;
  function ir(i) {
    if (i < 0 || i >= slides.length) return;
    slides[atual].classList.remove("active");
    dotsEl.children[atual].classList.remove("active");
    atual = i;
    slides[atual].classList.add("active");
    dotsEl.children[atual].classList.add("active");
    document.getElementById("counter").textContent = `${atual + 1} / ${slides.length}`;
  }
  document.getElementById("counter").textContent = `1 / ${slides.length}`;

  document.getElementById("btnPrev").addEventListener("click", () => ir(atual - 1));
  document.getElementById("btnNext").addEventListener("click", () => ir(atual + 1));
  dotsEl.addEventListener("click", (e) => {
    const dot = e.target.closest(".dot");
    if (dot) ir(parseInt(dot.dataset.i));
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === " ") ir(atual + 1);
    if (e.key === "ArrowLeft") ir(atual - 1);
  });

  let touchX = null;
  document.addEventListener("touchstart", (e) => { touchX = e.touches[0].clientX; });
  document.addEventListener("touchend", (e) => {
    if (touchX === null) return;
    const dx = e.changedTouches[0].clientX - touchX;
    if (dx > 60) ir(atual - 1);
    if (dx < -60) ir(atual + 1);
    touchX = null;
  });
}

montar();
</script>
</body>
</html>
"""


def gerar_html(dados):
    html = TEMPLATE.replace("__DADOS_JSON__", json.dumps(dados, ensure_ascii=False))
    html = html.replace("__FOTOS_SUPERVISORES_JSON__", _FOTOS_SUPERVISORES_JSON)
    html = html.replace("__FOTOS_RCAS_JSON__", _FOTOS_RCAS_JSON)
    html = html.replace("__EMBLEMAS_JSON__", _EMBLEMAS_JSON)
    html = html.replace("__LOGO_URI__", _LOGO_URI)
    html = html.replace("__LOGO_FRIATO_URI__", _LOGO_FRIATO_URI)
    html = html.replace("__PRODUTOS_FRIATO_URI__", _PRODUTOS_FRIATO_URI)
    html = html.replace("__VENDEDOR_TROFEU_URI__", _VENDEDOR_TROFEU_URI)
    html = html.replace("__GRAMADO_URI__", _GRAMADO_URI)
    html = html.replace("__RESTAURANTE_INTERIOR_URI__", _RESTAURANTE_INTERIOR_URI)
    html = html.replace("__RESTAURANTE_BUFFET_URI__", _RESTAURANTE_BUFFET_URI)
    return html


if __name__ == "__main__":
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
        dados = json.load(f)

    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        f.write(gerar_html(dados))
    print(f"Painel gerado em: {CAMINHO_SAIDA}")
