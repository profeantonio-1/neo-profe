import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")
st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Primaria")

# --- CONEXIÓN ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usamos el modelo 2.5-flash-lite de tu lista. 
# Es rápido, moderno y suele tener la cuota gratuita abierta.
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Metemos las instrucciones del Secret directamente en el mensaje
        instrucciones = st.secrets["MY_SECRET_PROMPT"]
        mensaje_para_google = f"{instrucciones}\n\nPregunta del alumno: {prompt}"
        
        response = model.generate_content(mensaje_para_google)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error("Neo está tomando un café... espera unos segundos.")
        st.info(f"Nota técnica: {e}")
