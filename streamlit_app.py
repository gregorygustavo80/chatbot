import streamlit as st
from openai import OpenAI

st.title("💬 TokenAPI")
st.write(
    "Este é um chatbot simples que usa o modelo GPT-4 da OpenAI para gerar respostas."
    "Para usar este aplicativo, você precisa fornecer uma chave de API da OpenAI, que pode ser obtida [aqui](https://platform.openai.com/account/api-keys). "
)

chave_api_openai = st.text_input("Chave da API da OpenAI", type="password")
if not chave_api_openai:
    st.info("Por favor, adicione sua chave da API da OpenAI para continuar.", icon="🗝️")
else:

    cliente = OpenAI(api_key=chave_api_openai)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for mensagem in st.session_state.messages:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    if prompt := st.chat_input("O que está acontecendo?"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        stream = cliente.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )

        with st.chat_message("assistant"):
            resposta = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
