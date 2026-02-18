import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

# --- OCULTAR ELEMENTOS DE STREAMLIT ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 1. FUNCIÓN DE SEGURIDAD (ACTUALIZADA CON INTRO) ---
def check_password():
    """Devuelve True si el usuario introdujo la contraseña correcta."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Si no está autenticado, muestra el formulario
    st.title("🔐 Acceso Restringido")
    
    # Usamos un formulario para que funcione la tecla Intro
    with st.form("login_form"):
        password_input = st.text_input("Introduce la clave de clase para hablar con Neo:", type="password")
        submit_button = st.form_submit_button("Entrar")
        
        if submit_button:
            if password_input == st.secrets["CLAVE_ACCESO"]:
                st.session_state.authenticated = True
                st.rerun() # Refresca para mostrar el chat
            else:
                st.error("❌ Clave incorrecta. Pregunta a tu maestro.")
    
    return False

# --- SOLO SI PASA LA SEGURIDAD, EJECUTAMOS EL RESTO ---
if check_password():
    # --- AQUÍ EMPIEZA TU CÓDIGO ORIGINAL (SIN CAMBIOS) ---
    st.title("🤖 Hola, soy Neo")
    st.subheader("Tu Profe Virtual")

    # Recuperamos la API Key y Prompt
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        instrucciones_neo = st.secrets["MY_SECRET_PROMPT"]
    except Exception:
        st.error("Error: No encuentro los Secrets.")
        st.stop()

    genai.configure(api_key=api_key)

    # MANTENEMOS TU MODELO Y CONFIGURACIÓN
    model = genai.GenerativeModel(
        'gemini-2.5-flash-lite',
        system_instruction=instrucciones_neo 
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
            historial_para_google = []
            for mensaje in st.session_state.messages:
                rol = "user" if mensaje["role"] == "user" else "model"
                if mensaje["content"] != prompt: 
                    historial_para_google.append({"role": rol, "parts": [mensaje["content"]]})

            chat = model.start_chat(history=historial_para_google)
            response = chat.send_message(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("Neo está pensando...")
            st.info(f"Detalle técnico: {e}")
    
    # Botón opcional para cerrar sesión (salir)
    if st.sidebar.button("Cerrar sesión de Neo"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()
