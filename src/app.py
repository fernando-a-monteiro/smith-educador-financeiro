import streamlit as st
from google.genai import errors

import agente
import config

st.set_page_config(page_title="Smith | Educador de Fundos", page_icon="🎓")
st.title("🎓 Smith")
st.caption("Educador financeiro de fundos de investimento. Não faz recomendação de investimento. Dados fictícios.")

if not config.GEMINI_API_KEY:
    st.error("Chave da API não encontrada. Crie o arquivo .env na raiz do projeto com GEMINI_API_KEY=sua_chave")
    st.stop()

if "system_prompt" not in st.session_state:
    dados = agente.carregar_dados()
    st.session_state.contexto = agente.montar_contexto(dados)
    st.session_state.system_prompt = agente.carregar_system_prompt(st.session_state.contexto)
    st.session_state.mensagens = []

with st.sidebar:
    st.header("📂 Contexto do Smith")
    st.text(st.session_state.contexto.split("BASE DE CONCEITOS:")[0])
if not st.session_state.mensagens:
    with st.spinner("Smith está analisando sua carteira..."):
        try:
            abertura = agente.responder(
                st.session_state.system_prompt,
                [{"role": "user", "content": "Olá! Acabei de abrir o chat."}],
            )
        except errors.APIError:
            st.warning("O Smith está com muitos acessos no momento. Aguarde alguns instantes e recarregue a página.")
            st.stop()
    st.session_state.mensagens.append({"role": "assistant", "content": abertura})
        
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"].replace("$", "\\$"))

pergunta = st.chat_input("Pergunte sobre seus fundos...")
if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            historico = [{"role": "user", "content": "Olá! Acabei de abrir o chat."}] + st.session_state.mensagens
            try:
                resposta = agente.responder(st.session_state.system_prompt, historico)
            except errors.APIError:
                st.session_state.mensagens.pop()
                st.warning("O Smith não conseguiu responder agora. Aguarde alguns instantes e envie a pergunta de novo.")
                st.stop()
        st.markdown(resposta.replace("$", "\\$"))


        suspeitos = agente.valores_nao_encontrados(resposta, st.session_state.contexto)
        if suspeitos:
              st.warning(f"⚠️ Valores não encontrados na base de conhecimento: {', '.join(suspeitos)}. Confira antes de usar.")

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})