import streamlit as st
import google.generativeai as genai

# Configuramos la página
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Lengua, Mates y Cono")

# Configurar la API Key desde los Secrets de Streamlit
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- CONFIGURACIÓN DEL MODELO (ACTUALIZADO 2026) ---
# Intentamos conectar con Gemini 3 Flash, que es el que ves en tu panel
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash", 
        system_instruction=st.secrets["MY_SECRET_PROMPT"]
    )
except Exception:
    # Si el anterior falla, probamos con el nombre alternativo de la versión 3
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.0-flash-preview",
            system_instruction=st.secrets["MY_SECRET_PROMPT"]
        )
    except Exception:
        # Último recurso por si la API aún usa el nombre 1.5 en tu región
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=st.secrets["MY_SECRET_PROMPT"]
        )

# --- LÓGICA DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del alumno
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Generar la respuesta de Neo
        response = model.generate_content(prompt)
        
        if response.text:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        else:
            st.warning("Neo está pensando... pero no ha salido nada. Intenta preguntar otra vez.")
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("Antonio, si el error persiste, revisa que la API KEY en los Secrets sea la del 'Nuevo Proyecto' que creamos.")
