import streamlit as st
import google.generativeai as genai

# Configuramos la página
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

# Título de la web
st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Lengua, Mates y Cono")

# Conectamos con el cerebro de Google (usando tus secretos de Streamlit)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Configuración del modelo con instrucciones de sistema
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=st.secrets["MY_SECRET_PROMPT"]
)

# Inicializamos el historial de chat si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostramos los mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del alumno
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Generar respuesta enviando todo el contexto (historial)
        # Convertimos el historial al formato que entiende Google
        chat_session = model.start_chat(history=[])
        
        # Enviamos el mensaje
        response = model.generate_content(prompt)
        
        # Mostrar respuesta de Neo
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Guardar en historial
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"¡Ups! Neo ha tenido un pequeño despiste técnico: {e}")
        st.info("Revisa si tu API KEY en los Secrets es correcta.")
