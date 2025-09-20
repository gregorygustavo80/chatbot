import streamlit as st
from openai import OpenAI
import time

st.set_page_config(page_title="Chatbot GPT", page_icon="💬", layout="wide")

st.title("💬 Chatbot GPT")
st.caption("Escolha seu modelo, converse e deixe a IA organizar os títulos das conversas!")

# Sidebar com configurações
with st.sidebar:
    st.subheader("⚙️ Configurações")

    openai_api_key = st.text_input("OpenAI API Key", type="password")

    # Modelos organizados do menos potente para o mais potente
    available_models = [
        "gpt-3",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-instruct",
        "gpt-4",
        "gpt-4-32k",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-turbo-32k",
        "gpt-4.1",
        "gpt-5"
    ]
    model = st.selectbox("Escolha o modelo GPT", available_models)

    # Inicializa sessões
    if "sessions" not in st.session_state:
        st.session_state.sessions = {"Sessão 1": []}
        st.session_state.current_session = "Sessão 1"

    # Selecionar sessão
    session_names = list(st.session_state.sessions.keys())
    selected_session = st.selectbox(
        "Escolha a sessão",
        session_names,
        index=session_names.index(st.session_state.current_session)
    )

    # Criar nova sessão
    if st.button("➕ Nova sessão"):
        new_name = f"Sessão {len(st.session_state.sessions)+1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
        st.rerun()

    # Botão para limpar histórico da sessão atual
    if st.button("🗑️ Limpar histórico"):
        st.session_state.sessions[selected_session] = []


# Função para gerar título automaticamente
def gerar_titulo(client, model, primeira_mensagem):
    prompt_titulo = f"""
    Crie um título curto (máx 5 palavras) para uma conversa cujo primeiro usuário disse:
    '{primeira_mensagem}'
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um gerador de títulos curtos e descritivos."},
                {"role": "user", "content": prompt_titulo}
            ],
            max_tokens=20,
        )
        titulo = response.choices[0].message.content.strip()
        return titulo
    except:
        return "Nova Sessão"


if not openai_api_key:
    st.info("🔑 Por favor, adicione sua OpenAI API Key na barra lateral.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    # Obtém a sessão atual
    messages = st.session_state.sessions[selected_session]

    # Layout principal: duas colunas
    col1, col2 = st.columns([1, 2])

    # Coluna da esquerda: histórico
    with col1:
        st.subheader("📜 Histórico")
        if messages:
            for m in messages:
                role = "👤 Usuário" if m["role"] == "user" else "🤖 Assistente"
                st.markdown(f"**{role}:** {m['content']}")
        else:
            st.write("Nenhuma mensagem nesta sessão ainda.")

    # Coluna da direita: conversa em tempo real
    with col2:
        st.subheader("💬 Conversa")

        # Exibe mensagens anteriores
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Campo de entrada do usuário
        if prompt := st.chat_input("Digite sua mensagem:"):
            messages.append({"role": "user", "content": prompt})

            # Se for a primeira mensagem da sessão, IA gera título automaticamente
            if len(messages) == 1:
                titulo = gerar_titulo(client, model, prompt)
                # Renomeia sessão no dicionário
                st.session_state.sessions[titulo] = st.session_state.sessions.pop(selected_session)
                st.session_state.current_session = titulo
                selected_session = titulo
                messages = st.session_state.sessions[selected_session]

            # Mostra a mensagem do usuário
            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                # Chamada streaming
                stream = client.chat.completions.create(
                    model=model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                    stream=True,
                )

                with st.chat_message("assistant"):
                    full_response = ""
                    message_placeholder = st.empty()
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            delta = chunk.choices[0].delta.content
                            full_response += delta
                            message_placeholder.markdown(full_response)
                            time.sleep(0.01)  # efeito de digitação

                messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"❌ Erro: {e}")
