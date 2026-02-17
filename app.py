import streamlit as st
import google.generativeai as genai

# Configuramos la página
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Lengua, Mates y Cono")

# Configurar la API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usamos el modelo 1.5-flash que es el que tiene CUOTA GRATUITA real
# El 2.0 o 3.0 a veces da "limit 0" en cuentas nuevas
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    system_instruction=st.secrets["MY_SECRET_PROMPT"]
)

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
        response = model.generate_content(prompt)
        
        if response.text:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("Antonio, prueba a esperar 10 segundos y recarga la página.")
