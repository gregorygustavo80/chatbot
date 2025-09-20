import streamlit as st
from openai import OpenAI
import time

st.title("💬 Chatbot GPT")
st.subheader("Escolha seu modelo GPT favorito e começe a usar!")

# Input da API Key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Por favor, adicione sua OpenAI API Key.", icon="🗝️")
else:
    # Inicializa o cliente OpenAI
    client = OpenAI(api_key=openai_api_key)

    # Lista de modelos
    available_models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-32k",
        "gpt-4-turbo",
        "gpt-4-turbo-32k",
        "gpt-4o",
        "gpt-5"
    ]
    model = st.selectbox("Escolha o modelo GPT", available_models)

    # Inicializa histórico de mensagens
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Botão para limpar histórico
    if st.button("🗑️ Limpar histórico"):
        st.session_state.messages = []

    # Exibe mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Campo de entrada para o usuário
    if prompt := st.chat_input("Digite sua mensagem:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Gera a resposta via API OpenAI em streaming
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )

            with st.chat_message("assistant"):
                full_response = ""
                message_placeholder = st.empty()
                for chunk in stream:
                    delta = chunk.choices[0].delta.get("content", "")
                    full_response += delta
                    # Atualiza a resposta em tempo real
                    message_placeholder.markdown(full_response)
                    time.sleep(0.01)  # simula efeito de digitação

            # Adiciona a resposta ao histórico
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Ocorreu um erro (modelo pode não estar disponível ou API Key inválida): {e}")
