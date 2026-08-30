r"""
Monta os dados do "Painel de Resultados" (estilo apresentação de fechamento
mensal) a partir de dados que JÁ existem — não lê planilha nenhuma direto,
só cruza o que o painel_pilares e o painel_departamentos já extraíram, mais
o config_mes.json (editado à mão todo mês com Vendedor/Supervisor Destaque).

Precisa rodar DEPOIS de painel_pilares/extrair_dados.py e
painel_departamentos/extrair_dados.py (pega o dados.json mais recente dos
dois).
"""

import datetime
import json
import os

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "dados.json")
CAMINHO_CONFIG = os.path.join(PASTA_BASE, "config_mes.json")

CAMINHO_PILARES = r"c:\AutomacaoMaxGestao\painel_pilares\dados.json"
CAMINHO_TOTAIS_GERENTE = r"c:\AutomacaoMaxGestao\painel_pilares\totais_gerais.json"
CAMINHO_DEPARTAMENTOS = r"c:\AutomacaoMaxGestao\painel_departamentos\dados.json"
CAMINHO_HISTORICO = os.path.join(PASTA_BASE, "historico_evolucao.json")


def _media(lista):
    return sum(lista) / len(lista) if lista else 0


def _ler_rcas_pilares():
    with open(CAMINHO_PILARES, "r", encoding="utf-8") as f:
        return json.load(f)


def _resumo_pilares():
    rcas = _ler_rcas_pilares()
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


def _ler_rcas_departamentos():
    if not os.path.exists(CAMINHO_DEPARTAMENTOS):
        return []
    with open(CAMINHO_DEPARTAMENTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def _resumo_departamentos():
    rcas = _ler_rcas_departamentos()
    if not rcas:
        return []

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


def _melhor_vendedor(rcas):
    """Vendedor Destaque = mesma regra da coluna 'VENDEDOR DESTAQUE' que o
    Edmar mantém na planilha SOMA NAO SALVA ENCIMA.xlsx (aba SOMAR 4
    PILARES): bateu Positivação, Margem e Mix (real/meta) E a Tendência de
    fechamento do Financeiro >= 100% — não o financeiro realizado até
    agora, que só bate perto do fim do mês (a coluna 'PILAR' da planilha
    não conta o financeiro do mesmo jeito, por isso não usamos ela aqui).
    Entre quem bate os 4, pega a maior média dos 4 percentuais."""
    def bateu_tudo(r):
        p = r["pilares"]
        return (
            p["positivacao"]["pct"] >= 1
            and p["margem"]["pct"] >= 1
            and p["mix"]["pct"] >= 1
            and r["tendencia"]["pct"] >= 1
        )

    elegiveis = [r for r in rcas if bateu_tudo(r)]
    if not elegiveis:
        return None

    def media_4(r):
        p = r["pilares"]
        return (r["tendencia"]["pct"] + p["margem"]["pct"] + p["mix"]["pct"] + p["positivacao"]["pct"]) / 4

    melhor = max(elegiveis, key=media_4)
    return {
        "codigo": melhor["codigo"],
        "nome": melhor["nome"],
        "rota": melhor.get("rota", ""),
        "supervisor": melhor["supervisor"],
        "pilares": melhor["pilares"],
        "tendencia": melhor["tendencia"],
        "media_4_pilares": media_4(melhor),
    }


def _ler_config():
    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def _ler_historico():
    with open(CAMINHO_HISTORICO, "r", encoding="utf-8") as f:
        return json.load(f)


def _dados_painel_gerente():
    """Le o Painel do Gerente (painel_pilares) — a mesma fonte que o
    gerente ja usa pra acompanhar o mes. Financeiro e somado RCA a RCA
    (dados.json); Margem, Cli. Atendidos, Peso e Preço Médio vem prontos
    do totais_gerais.json (Peso/Preço Médio adicionados 30/08)."""
    with open(CAMINHO_PILARES, "r", encoding="utf-8") as f:
        rcas = json.load(f)
    meta_financeiro = sum(r["pilares"]["financeiro"]["meta"] for r in rcas)
    real_financeiro = sum(r["pilares"]["financeiro"]["real"] for r in rcas)

    margem_pct = None
    cli_atendidos = None
    peso = None
    preco_medio = None
    if os.path.exists(CAMINHO_TOTAIS_GERENTE):
        with open(CAMINHO_TOTAIS_GERENTE, "r", encoding="utf-8") as f:
            totais = json.load(f)
        margem_pct = totais.get("margem", {}).get("real")
        cli_atendidos = totais.get("realizado_clientes")
        peso = totais.get("peso", {}).get("real")
        preco_medio = totais.get("preco_medio", {}).get("real")

    return {
        "meta_financeiro": meta_financeiro,
        "real_financeiro": real_financeiro,
        "margem_pct": margem_pct,
        "cli_atendidos": cli_atendidos,
        "peso": peso,
        "preco_medio": preco_medio,
    }


MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _mes_vigente():
    """O mes vigente — o que aparece 'ao vivo' na tabela de Evolução Anual,
    com o realizado parcial do Painel do Gerente — é sempre o mes real de
    hoje (calendário), independente do texto da capa (config_mes.json),
    que o usuário pode ajustar livremente sem bagunçar os dados ao vivo."""
    return MESES_PT[datetime.date.today().month - 1]


def _preencher_mes_com_gerente(historico):
    """O mes fechado (config_mes.json) ja tem os numeros finais arquivados
    — nao mexe. O mes vigente (o mes seguinte, ainda em andamento) sempre
    mostra o realizado PARCIAL de hoje, direto do Painel do Gerente — por
    isso é sobrescrito a cada execução, nunca só 'se estiver em branco'.
    Peso e Preço Médio vêm do totais_gerais.json (30/08); Variação e
    Cresc. Mensal são calculados automaticamente a partir deles."""
    mes_vigente = _mes_vigente()
    gerente = _dados_painel_gerente()
    mudou = False

    for linha in historico.get("faturamento", []):
        if linha["mes"] == mes_vigente:
            nova_meta = gerente["meta_financeiro"] or linha.get("meta")
            novo_fat = gerente["real_financeiro"]
            novo_pct = (novo_fat / nova_meta - 1) if nova_meta else None
            novo_saldo = (novo_fat - nova_meta) if nova_meta is not None else None
            if (linha.get("faturamento"), linha.get("pct_meta"), linha.get("saldo_meta")) != (novo_fat, novo_pct, novo_saldo):
                linha["meta"] = nova_meta
                linha["faturamento"] = novo_fat
                linha["pct_meta"] = novo_pct
                linha["saldo_meta"] = novo_saldo
                mudou = True

    operacional = historico.get("operacional", [])
    for i, linha in enumerate(operacional):
        if linha["mes"] == mes_vigente:
            if gerente["margem_pct"] is not None and linha.get("margem_pct") != gerente["margem_pct"]:
                linha["margem_pct"] = gerente["margem_pct"]
                mudou = True
            if gerente["cli_atendidos"] is not None and linha.get("cli_atendidos") != gerente["cli_atendidos"]:
                linha["cli_atendidos"] = gerente["cli_atendidos"]
                mudou = True
            if gerente["peso"] is not None and linha.get("peso") != gerente["peso"]:
                linha["peso"] = gerente["peso"]
                mudou = True
            if gerente["preco_medio"] is not None and linha.get("preco_medio") != gerente["preco_medio"]:
                linha["preco_medio"] = gerente["preco_medio"]
                mudou = True
            # Cresc. Mensal = Cli. Atendidos do mes vigente - do mes anterior;
            # Variação = Preço Médio do mes vigente vs do mes anterior
            # (mesma conta que o resto da tabela já usa).
            if i > 0 and linha.get("cli_atendidos") is not None and operacional[i - 1].get("cli_atendidos") is not None:
                novo_cresc = linha["cli_atendidos"] - operacional[i - 1]["cli_atendidos"]
                if linha.get("cresc_mensal") != novo_cresc:
                    linha["cresc_mensal"] = novo_cresc
                    mudou = True
            if i > 0 and linha.get("preco_medio") is not None and operacional[i - 1].get("preco_medio"):
                nova_variacao = linha["preco_medio"] / operacional[i - 1]["preco_medio"] - 1
                if linha.get("variacao_pct") != nova_variacao:
                    linha["variacao_pct"] = nova_variacao
                    mudou = True

    if mudou:
        with open(CAMINHO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)

    return historico


def main():
    config = _ler_config()
    historico = _ler_historico()
    historico = _preencher_mes_com_gerente(historico)
    rcas_pilares = _ler_rcas_pilares()

    saida = {
        "mes": config.get("mes", ""),
        "vendedor_destaque": config.get("vendedor_destaque", {}),
        "vendedor_destaque_auto": _melhor_vendedor(rcas_pilares),
        "supervisor_destaque": config.get("supervisor_destaque", {}),
        "pilares_por_supervisor": _resumo_pilares(),
        "departamentos_por_supervisor": _resumo_departamentos(),
        "rcas_pilares": rcas_pilares,
        "rcas_departamentos": _ler_rcas_departamentos(),
        "evolucao_faturamento": historico.get("faturamento", []),
        "evolucao_total_faturamento": historico.get("total_faturamento", {}),
        "evolucao_operacional": historico.get("operacional", []),
        "evolucao_total_operacional": historico.get("total_operacional", {}),
    }
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print(f"Dados do Painel de Resultados montados. Salvo em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
