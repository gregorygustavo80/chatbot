import streamlit as st
from openai import OpenAI

st.title("💬 TokenAPI")
st.write(
    "Este é um chatbot simples que usa o modelo GPT-4 da OpenAI para gerar respostas."
    "Para usar este aplicativo, você precisa fornecer uma chave de API OpenAI, que você pode obter" [aqui](https://platform.openai.com/account/api-keys). 
   
)

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Adicione sua chave de API OpenAI para continuar.", icon="🗝️")
else:

    client = OpenAI(api_key=openai_api_key)

  
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

 
    if prompt := st.chat_input("Pergunte alguma coisa"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
