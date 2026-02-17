import streamlit as st
import google.generativeai as genai

# Configuramos la página
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Lengua, Mates y Cono")

# Configurar la API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# MÉTODO MÁS COMPATIBLE:
# Si el modelo flash falla, probamos con una configuración más básica
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=st.secrets["MY_SECRET_PROMPT"]
    )
except Exception:
    # Si falla lo anterior, usamos el nombre antiguo/alternativo
    model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

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
        # Aquí forzamos la respuesta
        response = model.generate_content(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        # Esto nos dirá el error exacto si vuelve a fallar
        st.error(f"Error de conexión: {e}")
        st.info("Antonio, si ves esto, prueba a cambiar el nombre del modelo a 'gemini-1.5-pro' en el código.")
