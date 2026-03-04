import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

# --- ESTILOS CSS BASE ---
# Inicializamos el estado del modo investigador para el CSS dinámico
if "modo_investigador" not in st.session_state:
    st.session_state.modo_investigador = False

# Definimos los colores del Orbe dependiendo del modo
if st.session_state.modo_investigador:
    # MODO INVESTIGADOR: Tonos Naranja/Fuego y borde en el chat
    color_orbe = "radial-gradient(circle at 30% 30%, #ffeba3, #ff9800, #e65100)"
    sombra_orbe = "0 0 30px rgba(255, 152, 0, 0.6)"
    sombra_fuerte = "0 0 50px rgba(255, 152, 0, 0.9)"
    borde_chat = """
    .stChatInputContainer {
        border: 2px solid #ff9800 !important;
        box-shadow: 0 0 15px rgba(255, 152, 0, 0.2) !important;
        border-radius: 10px !important;
    }
    """
else:
    # MODO NORMAL: Tonos Azules originales
    color_orbe = "radial-gradient(circle at 30% 30%, #aeeeee, #00d4ff, #005aff)"
    sombra_orbe = "0 0 30px rgba(0, 212, 255, 0.6)"
    sombra_fuerte = "0 0 50px rgba(0, 212, 255, 0.9)"
    borde_chat = "" # Sin borde extra en modo normal

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stAppDeployButton {{display:none;}}

    .orb-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 40px; 
    }}
    
    .orb {{
        width: 140px; 
        height: 140px;
        border-radius: 50%;
        background: {color_orbe};
        box-shadow: {sombra_orbe}, inset -10px -10px 20px rgba(0,0,0,0.2);
        animation: floatAndBreath 6s infinite ease-in-out;
    }}

    @keyframes floatAndBreath {{
        0% {{ transform: translateY(0px) scale(1); box-shadow: {sombra_orbe}; }}
        50% {{ transform: translateY(-10px) scale(1.05); box-shadow: {sombra_fuerte}; }}
        100% {{ transform: translateY(0px) scale(1); box-shadow: {sombra_orbe}; }}
    }}
    
    {borde_chat}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAR MEMORIA DE CURSO ---
if "curso_alumno" not in st.session_state:
    st.session_state.curso_alumno = "5º o 6º de Primaria"

def actualizar_curso(texto):
    texto_min = texto.lower()
    if "1º" in texto_min or "primero" in texto_min: 
        st.session_state.curso_alumno = "1º de Primaria"
    elif "2º" in texto_min or "segundo" in texto_min: 
        st.session_state.curso_alumno = "2º de Primaria"
    elif "3º" in texto_min or "tercero" in texto_min: 
        st.session_state.curso_alumno = "3º de Primaria"
    elif "4º" in texto_min or "cuarto" in texto_min: 
        st.session_state.curso_alumno = "4º de Primaria"
    elif "eso" in texto_min: 
        st.session_state.curso_alumno = "Secundaria (ESO)"

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
    
    # --- CABECERA Y BOTÓN MODO INVESTIGADOR ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 Hola, soy Neo")
        st.subheader("Tu Profe Virtual")
    with col2:
        st.write("") # Espaciador para alinear el botón
        st.write("")
        # El botón de palanca en la derecha
        modo_investigador = st.toggle("🕹️ Modo Investigador", value=st.session_state.modo_investigador)
        
        # Si el interruptor cambia, recargamos la web para aplicar el cambio de color
        if modo_investigador != st.session_state.modo_investigador:
            st.session_state.modo_investigador = modo_investigador
            st.rerun()

    # --- ORBE (Se muestra si no hay mensajes) ---
    if not st.session_state.get("messages"):
        st.markdown('<div class="orb-container"><div class="orb"></div></div>', unsafe_allow_html=True)
        if st.session_state.modo_investigador:
             st.markdown("<p style='text-align: center; color: #ff9800; font-weight: bold;'>Modo Investigador Activado. ¿Qué quieres descubrir hoy?</p>", unsafe_allow_html=True)
        else:
             st.markdown("<p style='text-align: center; color: grey;'>Hazme una pregunta para empezar...</p>", unsafe_allow_html=True)

    # --- CONFIGURACIÓN DEL MODELO Y PROMPT DINÁMICO ---
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        instrucciones_base = st.secrets["MY_SECRET_PROMPT"]
        
        if st.session_state.modo_investigador:
            instrucciones_finales = instrucciones_base + f"""
            ESTÁS EN MODO INVESTIGADOR (ENCICLOPEDIA).
            NIVEL OBJETIVO: {st.session_state.curso_alumno}.
            - Tu prioridad es dar datos exactos, climas, fauna, flora y descripciones técnicas.
            - Si el nivel es 5º/6º (tu nivel base), usa lenguaje académico de primaria.
            - Si el alumno ha dicho que es de un curso inferior, simplifica drásticamente.
            - Usa listas y negritas. No hagas preguntas, ¡da respuestas!
            """
        else:
            instrucciones_finales = instrucciones_base + f"""
            ESTÁS EN MODO TUTOR SOCRÁTICO.
            - NO des la respuesta directa.
            - Adáptate al nivel de la pregunta del alumno de forma automática.
            - Ten en cuenta que el alumno dice ser de {st.session_state.curso_alumno}, pero prioriza la complejidad de su lenguaje actual para responder.
            """

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-flash-lite-latest',
            system_instruction=instrucciones_finales 
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

    # --- ZONA DE ENTRADA DE DATOS (SOLO TEXTO) ---
    prompt_texto = st.chat_input("¿En qué puedo ayudarte?")
    
    if prompt_texto:
        # 1. Actualizamos el curso por si el alumno lo menciona
        actualizar_curso(prompt_texto)
        
        # 2. Mostramos el mensaje en pantalla
        st.session_state.messages.append({"role": "user", "content": prompt_texto})
        with st.chat_message("user"):
            st.markdown(prompt_texto)

        # 3. Procesamos la respuesta con Neo
        try:
            historial_para_google = []
            for mensaje in st.session_state.messages:
                rol = "user" if mensaje["role"] == "user" else "model"
                if mensaje["content"] != prompt_texto: 
                    historial_para_google.append({"role": rol, "parts": [mensaje["content"]]})

            chat = model.start_chat(history=historial_para_google)
            response = chat.send_message(prompt_texto)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Recarga para quitar el orbe en el primer mensaje
            if len(st.session_state.messages) <= 2:
                st.rerun()
            
        except Exception as e:
            st.error("Neo está pensando y tuvo un pequeño lapsus...")
            st.info(f"Detalle técnico: {e}")
    
    # --- BARRA LATERAL (Cerrar sesión e info) ---
    with st.sidebar:
        st.write(f"📍 Nivel actual guardado: **{st.session_state.curso_alumno}**")
      # --- NUEVO CHIVATO VISUAL DE MODO ---
        st.write("") # Pequeño espacio
        if st.session_state.modo_investigador:
            st.markdown("""
            <div style='background-color: #ff9800; padding: 10px; border-radius: 8px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <b>🔍 MODO INVESTIGADOR ACTIVADO</b>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background-color: #005aff; padding: 10px; border-radius: 8px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <b>🧠 MODO TUTOR (Socrático)</b>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        if st.button("Cerrar sesión de Neo"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.rerun()
            # --- SELLO DE AUTORÍAS Y PROTECCIÓN ---
        st.write("") 
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666666; font-size: 0.85rem; line-height: 1.4;'>
                <p style='margin-bottom: 5px;'>© 2026 <b>NEO, tu profe virutal</b></p>
                <p style='margin-bottom: 5px;'>Propiedad Intelectual de:<br>
                <span style='color: #005aff; font-weight: bold;'>Antonio M. López Martí</span></p>
                <p style='font-size: 0.75rem; font-style: italic;'>Uso educativo restringido.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
