import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")
st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Primaria")

# 1. Configurar la API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. BUSCADOR DE MODELOS (Para evitar el error 404)
@st.cache_resource
def get_working_model():
    # Buscamos en tu cuenta qué modelos tienes permitidos
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Prioridad: Gemini 3 -> Gemini 2 -> Gemini 1.5
    for target in ["models/gemini-3-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash"]:
        if target in available_models:
            return genai.GenerativeModel(model_name=target)
    # Si no encuentra ninguno de esos, coge el primero que funcione
    return genai.GenerativeModel(model_name=available_models[0])

try:
    model = get_working_model()
except Exception as e:
    st.error(f"No se pudo conectar con el cerebro de Google: {e}")
    st.stop()

# 3. Lógica del Chat
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
        # Enviamos las instrucciones junto con la pregunta
        full_prompt = f"{st.secrets['MY_SECRET_PROMPT']}\n\nPregunta del alumno: {prompt}"
        response = model.generate_content(full_prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"Error al responder: {e}")
