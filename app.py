import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")
st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Primaria")

# --- CONEXIÓN ---
# Recuperamos la API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    instrucciones_neo = st.secrets["MY_SECRET_PROMPT"]
except Exception:
    st.error("Error: No encuentro los Secrets (API Key o Prompt).")
    st.stop()

genai.configure(api_key=api_key)

# --- CONFIGURACIÓN DEL MODELO ---
# MANTENEMOS TU MODELO EXACTO: 'gemini-2.5-flash-lite'
# CAMBIO IMPORTANTE 1: Metemos las instrucciones AQUÍ, en la configuración inicial.
# Así Neo "nace" sabiendo que es un profe y no se le olvida.
model = genai.GenerativeModel(
    'gemini-2.5-flash-lite',
    system_instruction=instrucciones_neo 
)

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostramos lo que ya se ha hablado en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DE INTERACCIÓN ---
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    
    # 1. Guardamos y mostramos tu pregunta
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # CAMBIO IMPORTANTE 2: CREAR LA MEMORIA
        # Convertimos el chat de Streamlit al formato que entiende Google
        historial_para_google = []
        for mensaje in st.session_state.messages:
            # Traducimos 'user'/'assistant' a 'user'/'model'
            rol = "user" if mensaje["role"] == "user" else "model"
            # Omitimos el último mensaje del usuario para enviarlo con send_message después
            # (Esto evita duplicarlo si la lógica de chat lo requiere, pero
            # la forma más segura es cargar el historial previo y enviar el nuevo).
            if mensaje["content"] != prompt: 
                historial_para_google.append({"role": rol, "parts": [mensaje["content"]]})

        # Iniciamos el chat con el historial PREVIO (Memoria)
        chat = model.start_chat(history=historial_para_google)
        
        # Enviamos el mensaje NUEVO
        response = chat.send_message(prompt)
        
        # 2. Mostramos la respuesta de Neo
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # 3. Guardamos la respuesta en el historial
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error("Neo está pensando... (o ha ocurrido un error de conexión).")
        st.info(f"Detalle técnico: {e}")
