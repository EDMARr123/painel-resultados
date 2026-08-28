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

# Reaproveita as fotos já cadastradas no painel_pilares.
PASTA_FOTOS_SUPERVISORES = os.path.join(PASTA_BASE, "..", "painel_pilares", "fotos_supervisores")
PASTA_FOTOS_RCAS = os.path.join(PASTA_BASE, "..", "painel_pilares", "fotos_rcas")


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

TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de Resultados — Equipe GYN</title>
<style>
:root {
  --bg: #0B0D12; --surface: #12151C; --surface-2: #191D26; --border: #262B36;
  --ink: #F2F3F5; --ink-soft: #9AA1AE; --ink-faint: #6B7280;
  --accent: #4F8CFF; --good: #2FBF71; --warn: #E0A72E; --bad: #E2685F;
  --gold: #E7B23B;
}
* { box-sizing: border-box; }
html, body { height: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink); overflow: hidden;
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
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

/* Capa */
.capa .logo { width: 72px; height: 72px; border-radius: 18px; background: var(--surface-2); display: flex; align-items: center; justify-content: center; font-size: 34px; margin-bottom: 22px; }
.capa .mes-pill { margin-top: 22px; background: var(--surface-2); border: 1px solid var(--border); border-radius: 999px; padding: 8px 22px; font-size: 16px; font-weight: 700; color: var(--accent); }

/* Ranking */
.ranking { width: 100%; max-width: 900px; display: flex; flex-direction: column; gap: 12px; }
.rank-row {
  display: grid; grid-template-columns: 34px 1fr 120px; align-items: center; gap: 16px;
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 14px 20px;
  text-align: left;
}
.rank-row .pos { font-size: 20px; font-weight: 800; color: var(--ink-faint); text-align: center; }
.rank-row.n1 .pos { color: var(--gold); }
.rank-row .nome { font-size: 17px; font-weight: 800; }
.rank-row .bar-track { height: 8px; border-radius: 999px; background: var(--surface-2); margin-top: 8px; overflow: hidden; }
.rank-row .bar-fill { height: 100%; border-radius: 999px; background: var(--accent); }
.rank-row.n1 .bar-fill { background: var(--gold); }
.rank-row .valor { font-size: 20px; font-weight: 800; text-align: right; font-variant-numeric: tabular-nums; }

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
  background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px 26px; margin-top: 10px;
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
  cursor: pointer; font-size: 20px;
}
.nav-arrow:hover { color: var(--ink); border-color: var(--accent); }
.nav-arrow.prev { left: 20px; }
.nav-arrow.next { right: 20px; }
.slide-counter { position: fixed; top: 20px; right: 24px; color: var(--ink-faint); font-size: 13px; font-weight: 700; z-index: 20; }

@media (max-width: 700px) {
  .nav-arrow { display: none; }
  .rank-row { grid-template-columns: 26px 1fr 78px; padding: 12px 14px; gap: 10px; }
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

function normalizarNomeFoto(nome) {
  return (nome || "").replace(/\s*-\s*$/, "").trim().toUpperCase();
}
function fmtPct(v) { return (v * 100).toLocaleString("pt-BR", { maximumFractionDigits: 0 }) + "%"; }
function fmtNum1(v) { return v.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }); }
function iniciais(nome) {
  return (nome || "").split(/\s+/).filter(Boolean).slice(0, 2).map(p => p[0]).join("").toUpperCase();
}

function slideCapa() {
  return `
    <div class="slide capa active">
      <div class="logo">🍗</div>
      <div class="eyebrow">T&amp;T Alimentos</div>
      <h1>Reunião de Fechamento</h1>
      <p class="sub">Resultado do mês, time por time</p>
      <div class="mes-pill">${DADOS.mes || ""}</div>
    </div>`;
}

function slideRankingPilares() {
  const linhas = DADOS.pilares_por_supervisor;
  const max = 4;
  const rows = linhas.map((s, i) => `
    <div class="rank-row ${i === 0 ? "n1" : ""}">
      <div class="pos">${i === 0 ? "🏆" : i + 1}</div>
      <div>
        <div class="nome">${s.supervisor}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${(s.pilares_media / max) * 100}%"></div></div>
      </div>
      <div class="valor">${fmtNum1(s.pilares_media)} / 4</div>
    </div>`).join("");
  return `
    <div class="slide">
      <div class="eyebrow">Resultado do Mês</div>
      <h2>4 Pilares por Supervisor</h2>
      <div class="ranking">${rows}</div>
    </div>`;
}

function slideRankingDepartamentos() {
  const linhas = DADOS.departamentos_por_supervisor;
  if (!linhas.length) return "";
  const max = linhas[0].total_categorias || 9;
  const rows = linhas.map((s, i) => `
    <div class="rank-row ${i === 0 ? "n1" : ""}">
      <div class="pos">${i === 0 ? "🏆" : i + 1}</div>
      <div>
        <div class="nome">${s.supervisor}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${(s.categorias_media / max) * 100}%"></div></div>
      </div>
      <div class="valor">${fmtNum1(s.categorias_media)} / ${max}</div>
    </div>`).join("");
  return `
    <div class="slide">
      <div class="eyebrow">Resultado do Mês</div>
      <h2>Departamentos por Supervisor</h2>
      <div class="ranking">${rows}</div>
    </div>`;
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
    slideRankingPilares(),
    slideRankingDepartamentos(),
    slideDestaque("vendedor_destaque", "Vendedor Destaque", true),
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
    return html


if __name__ == "__main__":
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
        dados = json.load(f)

    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        f.write(gerar_html(dados))
    print(f"Painel gerado em: {CAMINHO_SAIDA}")
