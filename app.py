import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")
st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Primaria")

# --- CONEXIÓN ---
# 1. Configurar la API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Configurar el modelo "Caballo de Batalla" (1.5 Flash)
# IMPORTANTE: No ponemos system_instruction aquí para evitar el Error 404
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DE RESPUESTA ---
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    # 1. Guardar y mostrar lo que escribe el alumno
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generar respuesta
    try:
        # TRUCO DEL ALMENDRUCO:
        # En lugar de configurar el sistema aparte, lo pegamos todo junto.
        # Esto evita que Google se líe con versiones beta.
        instrucciones = st.secrets["MY_SECRET_PROMPT"]
        mensaje_completo = f"{instrucciones}\n\nIMPORTANTE: Responde al alumno que te dice: {prompt}"
        
        response = model.generate_content(mensaje_completo)
        
        # 3. Mostrar respuesta de Neo
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        # Si falla, mostramos el error limpio
        st.error("¡Vaya! Neo se ha mareado un poco.")
        st.code(f"Error técnico: {e}")
        st.info("Intenta esperar 30 segundos y pregunta de nuevo.")
