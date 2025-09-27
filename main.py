import streamlit as st
from openai import OpenAI
import time

st.set_page_config(page_title="Chatbot GPT", page_icon="💬", layout="wide")

st.title("💬 Chatbot GPT")
st.subheader("Escolha seu modelo e comece a usar!")

# Sidebar com configurações
with st.sidebar:
    st.subheader("⚙️ Configurações")

    openai_api_key = st.text_input("OpenAI API Key", type="password")

    # Modelos organizados do menos potente para o mais potente
    available_models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4.1",
        "gpt-5"
    ]
    model = st.selectbox("Escolha o modelo GPT", available_models)

    # Inicializa sessões
    if "sessions" not in st.session_state:
        st.session_state.sessions = {"": []}
        st.session_state.current_session = ""

    # Selecionar sessão
    session_names = list(st.session_state.sessions.keys())
    selected_session = st.selectbox(
        "Chats",
        session_names,
        index=session_names.index(st.session_state.current_session)
    )

    # Criar nova sessão
    if st.button("➕ Novo chat"):
        new_name = f"chat {len(st.session_state.sessions)+1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
        st.rerun()

    # Botão para limpar histórico da sessão atual
    if st.button("🗑️ Limpar página"):
        st.session_state.sessions[selected_session] = []
        
    if st.button("🗑️ Excluir todos os chats"):
        st.session_state.sessions = {"": []}
        st.session_state.current_session = ""
        st.rerun()

# Função para gerar título automaticamente
def gerar_titulo(client, model, primeira_mensagem):
    prompt_titulo = f"""
    Crie um título curto (máx 5 palavras) em português para uma conversa cujo primeiro usuário disse:
    '{primeira_mensagem}'
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um gerador de títulos curtos e descritivos. Sempre responda em português do Brasil."},
                {"role": "user", "content": prompt_titulo}
            ],
            max_tokens=20,
        )
        titulo = response.choices[0].message.content.strip()
        return titulo
    except:
        return "Novo chat"

if not openai_api_key:
    st.info(" Por favor, adicione sua OpenAI API Key na barra lateral.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    # Obtém a sessão atual
    messages = st.session_state.sessions[selected_session]

    # Exibe mensagens anteriores
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Botão de upload de arquivo ---
    uploaded_file = st.file_uploader("📎 Adicionar arquivos:", type=["txt", "pdf", "csv", "docx", "mp3", "mp4" "wav", "opus"])
    file_content = ""
    if uploaded_file:
        file_content = uploaded_file.read()
        st.info(f"Arquivo '{uploaded_file.name}' carregado com sucesso!")

    # Campo de entrada do usuário
    if prompt := st.chat_input("Digite sua mensagem:"):
        # Se houver arquivo, anexa o conteúdo à mensagem
        if uploaded_file:
            try:
                # Tenta decodificar como texto
                file_text = file_content.decode('utf-8', errors='ignore')
            except:
                file_text = "<conteúdo binário não exibido>"
            prompt = f"{prompt}\n\nConteúdo do arquivo:\n{file_text}"

        messages.append({"role": "user", "content": prompt})

        # Se for a primeira mensagem da sessão, IA gera título automaticamente
        if len(messages) == 1:
            titulo = gerar_titulo(client, model, prompt)
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
                messages=[
                    {"role": "system", "content": "Você é um assistente útil que SEMPRE responde em português do Brasil, de forma clara e natural."},
                    *[{"role": m["role"], "content": m["content"]} for m in messages],
                ],
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
                        time.sleep(0.01)

            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"❌ Erro: {e}")
