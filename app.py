import streamlit as st
import google.generativeai as genai

# Configuramos la página
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

# Título de la web
st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Lengua, Mates y Cono")

# Conectamos con el cerebro de Google (usando tus secretos)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash', 
                              system_instruction=st.secrets["MY_SECRET_PROMPT"])

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del alumno
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta de Neo
    response = model.generate_content(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
