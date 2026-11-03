import json
import re
from datetime import date, timedelta

import pandas as pd
from google import genai
from google.genai import types

import config


def carregar_dados():
    with open(config.PASTA_DATA / "perfil_investidor.json", encoding="utf-8") as f:
        perfil = json.load(f)
    with open(config.PASTA_DATA / "carteira_fundos.json", encoding="utf-8") as f:
        carteira = json.load(f)
    with open(config.PASTA_DATA / "conceitos_fundos.json", encoding="utf-8") as f:
        conceitos = json.load(f)
    historico = pd.read_csv(config.PASTA_DATA / "historico_atendimento.csv")

    return {"perfil": perfil, "carteira": carteira, "conceitos": conceitos, "historico": historico}


def faixa_ir(dias, tributacao):
    if tributacao == "acoes":
        return "15% no resgate"
    if dias <= 180:
        return "22,5%"
    if dias <= 360:
        return "20%"
    if dias <= 720:
        return "17,5%"
    return "15%"


def ultimo_dia_util(ano, mes):
    if mes == 12:
        dia = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        dia = date(ano, mes + 1, 1) - timedelta(days=1)
    while dia.weekday() >= 5:
        dia -= timedelta(days=1)
    return dia


def proximo_come_cotas(hoje):
    for ano in (hoje.year, hoje.year + 1):
        for mes in (5, 11):
            data = ultimo_dia_util(ano, mes)
            if data >= hoje:
                return data


def reais(valor):
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-R$ {texto}" if valor < 0 else f"R$ {texto}"


def montar_contexto(dados):
    perfil = dados["perfil"]
    carteira = dados["carteira"]
    hoje = date.fromisoformat(carteira["data_posicao"])

    linhas = [f"Data de referência: {hoje.strftime('%d/%m/%Y')}", ""]

    linhas.append("DADOS DO CLIENTE:")
    linhas.append(f"- Nome: {perfil['nome']}")
    linhas.append(f"- Perfil: {perfil['perfil_investidor']} | Aceita risco: {'sim' if perfil['aceita_risco'] else 'não'}")
    linhas.append(f"- Conhecimento em fundos: {perfil['conhecimento_fundos']}")
    linhas.append(f"- Objetivo principal: {perfil['objetivo_principal']}")
    linhas.append(f"- Reserva de emergência atual: {reais(perfil['reserva_emergencia_atual'])}")
    for meta in perfil["metas"]:
        linhas.append(f"- Meta: {meta['meta']} | {reais(meta['valor_necessario'])} até {meta['prazo']}")
    linhas.append("")

    linhas.append("CARTEIRA DE FUNDOS:")
    fundos_come_cotas = []
    for i, fundo in enumerate(carteira["fundos"], start=1):
        dias = (hoje - date.fromisoformat(fundo["data_aplicacao"])).days
        custo_taxa = fundo["saldo_bruto_atual"] * fundo["taxa_administracao_aa"] / 100
        resultado = fundo["saldo_bruto_atual"] - fundo["valor_aplicado"]
        taxa = f"{fundo['taxa_administracao_aa']:.2f}".replace(".", ",")

        linhas.append(f"{i}. {fundo['nome']} (classe: {fundo['classe']})")
        linhas.append(f"   - Valor aplicado: {reais(fundo['valor_aplicado'])} | Saldo bruto: {reais(fundo['saldo_bruto_atual'])} | Resultado: {reais(resultado)}")
        linhas.append(f"   - Taxa de administração: {taxa}% a.a. (cerca de {reais(custo_taxa)} por ano sobre o saldo atual)")
        linhas.append(f"   - Taxa de performance: {fundo['taxa_performance'] or 'não cobra'}")
        linhas.append(f"   - Resgate: cotização {fundo['cotizacao_resgate']} e liquidação {fundo['liquidacao_resgate']}")
        linhas.append(f"   - Aplicado há {dias} dias | Faixa de IR atual: {faixa_ir(dias, fundo['tributacao'])}")
        linhas.append(f"   - Come-cotas: {'sim' if fundo['tem_come_cotas'] else 'não'} | Uso pretendido: {fundo['uso_pretendido']}")
        if fundo["tem_come_cotas"]:
            fundos_come_cotas.append(fundo["nome"])
    linhas.append("")

    data_cc = proximo_come_cotas(hoje)
    linhas.append(
        f"PRÓXIMO COME-COTAS: {data_cc.strftime('%d/%m/%Y')} (em {(data_cc - hoje).days} dias) | "
        f"Fundos afetados: {', '.join(fundos_come_cotas)}"
    )
    linhas.append("")

    linhas.append("BASE DE CONCEITOS:")
    for c in dados["conceitos"]:
        linhas.append(f"- {c['conceito']}: {c['definicao']} Atenção: {c['ponto_de_atencao']} Exemplo: {c['exemplo']} Onde encontrar: {c['onde_encontrar']}.")
    linhas.append("")

    historico = dados["historico"]
    linhas.append("HISTÓRICO DE ATENDIMENTO:")
    for _, linha in historico.iterrows():
        linhas.append(f"- {linha['data']} ({linha['canal']}) {linha['tema']}: {linha['resumo']} | resolvido: {linha['resolvido']}")
    em_aberto = historico[historico["resolvido"] == "nao"]
    for _, linha in em_aberto.iterrows():
        linhas.append(f"DÚVIDA EM ABERTO: {linha['resumo']} (desde {linha['data']})")

    return "\n".join(linhas)


def carregar_system_prompt(contexto):
    texto = config.ARQUIVO_PROMPTS.read_text(encoding="utf-8")
    secao = texto.split("## System Prompt", 1)[1]
    bloco = re.search(r"```\s*\n(.*?)```", secao, re.DOTALL)
    if not bloco:
        raise ValueError("System prompt não encontrado em docs/03-prompts.md")
    return bloco.group(1).replace("{contexto}", contexto)


def responder(system_prompt, mensagens):
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    conteudo = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in mensagens
    ]

    resposta = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=conteudo,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
        ),
    )
    return resposta.text


def valores_nao_encontrados(resposta, contexto):
    padrao = r"R\$\s?\d[\d.]*(?:,\d{2})?"

    def normalizar(valor):
        return re.sub(r"\s", "", valor).rstrip(",")

    no_contexto = {normalizar(v) for v in re.findall(padrao, contexto)}
    no_contexto_inteiros = {v.split(",")[0] for v in no_contexto}

    suspeitos = []
    for valor in re.findall(padrao, resposta):
        v = normalizar(valor)
        if v not in no_contexto and v.split(",")[0] not in no_contexto_inteiros and valor not in suspeitos:
            suspeitos.append(valor)
    return suspeitos