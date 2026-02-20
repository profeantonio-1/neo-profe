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
        padding: 40px; 
    }
    
    .orb {
        width: 140px; 
        height: 140px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #aeeeee, #00d4ff, #005aff);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6), inset -10px -10px 20px rgba(0,0,0,0.2);
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

    if not st.session_state.get("messages"):
        st.markdown('<div class="orb-container"><div class="orb"></div></div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: grey;'>Escríbeme o usa el micrófono para hablar...</p>", unsafe_allow_html=True)

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        instrucciones_neo = st.secrets["MY_SECRET_PROMPT"]
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            'gemini-flash-lite-latest',
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

    # --- ZONA DE ENTRADA DE DATOS ---
    mensaje_usuario = None

    # 1. Entrada por Micrófono (Lo más limpio posible ocultando la etiqueta)
    audio_value = st.audio_input("Audio", label_visibility="collapsed")
    
    # 2. Entrada por Teclado
    prompt_texto = st.chat_input("¿En qué puedo ayudarte?")
    
    if prompt_texto:
        mensaje_usuario = prompt_texto

    # Si hay un audio nuevo
    if audio_value and st.session_state.get('ultimo_audio') != audio_value:
        st.session_state.ultimo_audio = audio_value
        
        with st.spinner("Neo está escuchando..."):
            try:
                audio_data = {"mime_type": "audio/wav", "data": audio_value.getvalue()}
                respuesta_transcripcion = model.generate_content([
                    audio_data, 
                    "Transcribe exactamente lo que se dice en este audio. Escribe solo el texto de la transcripción, sin añadir ninguna otra palabra tuya."
                ])
                mensaje_usuario = f"🎤 {respuesta_transcripcion.text}"
                
            except Exception as e:
                st.error("Neo no ha podido escuchar bien el audio. Prueba a hablar más cerca.")

    # --- PROCESAMIENTO DE LA PREGUNTA ---
    if mensaje_usuario:
        st.session_state.messages.append({"role": "user", "content": mensaje_usuario})
        with st.chat_message("user"):
            st.markdown(mensaje_usuario)

        try:
            historial_para_google = []
            for mensaje in st.session_state.messages:
                rol = "user" if mensaje["role"] == "user" else "model"
                if mensaje["content"] != mensaje_usuario: 
                    historial_para_google.append({"role": rol, "parts": [mensaje["content"]]})

            chat = model.start_chat(history=historial_para_google)
            response = chat.send_message(mensaje_usuario)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            if len(st.session_state.messages) <= 2:
                st.rerun()
            
        except Exception as e:
            st.error("Neo está pensando y tuvo un pequeño lapsus...")
            st.info(f"Detalle técnico: {e}")
    
    if st.sidebar.button("Cerrar sesión de Neo"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.session_state.ultimo_audio = None
        st.rerun()
