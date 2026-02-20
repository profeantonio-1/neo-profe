import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

# --- ESTILOS CSS (Orbe HD y Limpieza) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}

    .orb-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 40px; /* Un poco más de aire arriba */
    }
    
    /* ORBE AZUL HD (Más nítido y 3D) */
    .orb {
        width: 140px; /* Un poco más grande para que luzca */
        height: 140px;
        border-radius: 50%;
        
        /* Degradado complejo para dar efecto de esfera nítida */
        background: radial-gradient(circle at 30% 30%, #aeeeee, #00d4ff, #005aff);
        
        /* Sombra externa para el brillo (glow) sin desenfocar la bola */
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6), inset -10px -10px 20px rgba(0,0,0,0.2);
        
        /* Animación suave */
        animation: floatAndBreath 6s infinite ease-in-out;
    }

    @keyframes floatAndBreath {
        0% { transform: translateY(0px) scale(1); box-shadow: 0 0 30px rgba(0, 212, 255, 0.6); }
        50% { transform: translateY(-10px) scale(1.05); box-shadow: 0 0 50px rgba(0, 212, 255, 0.9); }
        100% { transform: translateY(0px) scale(1); box-shadow: 0 0 30px rgba(0, 212, 255, 0.6); }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. FUNCIÓN DE SEGURIDAD ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    st.title("🔐 Acceso Restringido")
    with st.form("login_form"):
        password_input = st.text_input("Introduce la clave de clase para hablar con Neo:", type="password")
        submit_button = st.form_submit_button("Entrar")
        if submit_button:
            if password_input == st.secrets["CLAVE_ACCESO"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta. Pregunta a tu maestro.")
    return False

# --- SOLO SI PASA LA SEGURIDAD, EJECUTAMOS EL RESTO ---
if check_password():
    st.title("🤖 Hola, soy Neo")
    st.subheader("Tu Profe Virtual")

    # --- ORBE AZUL (SOLO SI NO HAY MENSAJES) ---
    if not st.session_state.get("messages"):
        st.markdown('<div class="orb-container"><div class="orb"></div></div>', unsafe_allow_html=True)
        # Un pequeño mensaje de bienvenida debajo del orbe
        st.markdown("<p style='text-align: center; color: grey;'>Hazme una pregunta para empezar...</p>", unsafe_allow_html=True)

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        instrucciones_neo = st.secrets["MY_SECRET_PROMPT"]
        genai.configure(api_key=api_key)

        # Mantenemos el modelo que funciona bien
        model = genai.GenerativeModel(
            'gemini-flash-latest',
            system_instruction=instrucciones_neo 
        )
    except Exception:
        st.error("Error: No encuentro los Secrets.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    if prompt := st.chat_input("¿En qué puedo ayudarte?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generación de respuesta (SIN orbe naranja, simple y directo)
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
            
            # Forzamos recarga para que el orbe azul desaparezca si era la primera pregunta
            if len(st.session_state.messages) <= 2:
                st.rerun()
            
        except Exception as e:
            st.error("Neo está pensando...")
            st.info(f"Detalle técnico: {e}")
    
    if st.sidebar.button("Cerrar sesión de Neo"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()
