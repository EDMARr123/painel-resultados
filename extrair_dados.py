r"""
Monta os dados do "Painel de Resultados" (estilo apresentação de fechamento
mensal) a partir de dados que JÁ existem — não lê planilha nenhuma direto,
só cruza o que o painel_pilares e o painel_departamentos já extraíram, mais
o config_mes.json (editado à mão todo mês com Vendedor/Supervisor Destaque).

Precisa rodar DEPOIS de painel_pilares/extrair_dados.py e
painel_departamentos/extrair_dados.py (pega o dados.json mais recente dos
dois).
"""

import json
import os

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "dados.json")
CAMINHO_CONFIG = os.path.join(PASTA_BASE, "config_mes.json")

CAMINHO_PILARES = r"c:\AutomacaoMaxGestao\painel_pilares\dados.json"
CAMINHO_DEPARTAMENTOS = r"c:\AutomacaoMaxGestao\painel_departamentos\dados.json"


def _media(lista):
    return sum(lista) / len(lista) if lista else 0


def _resumo_pilares():
    with open(CAMINHO_PILARES, "r", encoding="utf-8") as f:
        rcas = json.load(f)

    supervisores = sorted({r["supervisor"] for r in rcas})
    resumo = []
    for sup in supervisores:
        do_sup = [r for r in rcas if r["supervisor"] == sup]
        resumo.append({
            "supervisor": sup,
            "rcas": len(do_sup),
            "pilares_media": _media([r["pilares_atingidos"] for r in do_sup]),
            "financeiro_pct": _media([r["pilares"]["financeiro"]["pct"] for r in do_sup]),
            "positivacao_pct": _media([r["pilares"]["positivacao"]["pct"] for r in do_sup]),
            "margem_pct": _media([r["pilares"]["margem"]["pct"] for r in do_sup]),
            "mix_pct": _media([r["pilares"]["mix"]["pct"] for r in do_sup]),
            "recompra_pct": _media([r["recompra_pct"] for r in do_sup]),
        })
    resumo.sort(key=lambda s: s["pilares_media"], reverse=True)
    return resumo


def _resumo_departamentos():
    if not os.path.exists(CAMINHO_DEPARTAMENTOS):
        return []
    with open(CAMINHO_DEPARTAMENTOS, "r", encoding="utf-8") as f:
        rcas = json.load(f)

    supervisores = sorted({r["supervisor"] for r in rcas})
    resumo = []
    for sup in supervisores:
        do_sup = [r for r in rcas if r["supervisor"] == sup]
        resumo.append({
            "supervisor": sup,
            "categorias_media": _media([r["categorias_atingidas"] for r in do_sup]),
            "total_categorias": do_sup[0]["total_categorias"] if do_sup else 0,
            "bateram": sum(1 for r in do_sup if r["bateu"]),
            "rcas": len(do_sup),
        })
    resumo.sort(key=lambda s: s["categorias_media"], reverse=True)
    return resumo


def _ler_config():
    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = _ler_config()
    saida = {
        "mes": config.get("mes", ""),
        "vendedor_destaque": config.get("vendedor_destaque", {}),
        "supervisor_destaque": config.get("supervisor_destaque", {}),
        "pilares_por_supervisor": _resumo_pilares(),
        "departamentos_por_supervisor": _resumo_departamentos(),
    }
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print(f"Dados do Painel de Resultados montados. Salvo em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
