import streamlit as st
import google.generativeai as genai

# Configuramos la página
st.set_page_config(page_title="Neo: Tu Profe Virtual", page_icon="🤖")

st.title("🤖 Hola, soy Neo")
st.subheader("Tu Profe Virtual de Lengua, Mates y Cono")

# Configurar la API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usamos el modelo estándar sin instrucciones de sistema aquí para evitar el error 404
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostramos el historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del alumno
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # CONSTRUIMOS EL MENSAJE CON LAS INSTRUCCIONES DENTRO
        # Esto evita el error de "v1beta" y el "404"
        instrucciones = st.secrets["MY_SECRET_PROMPT"]
        pregunta_completa = f"{instrucciones}\n\nEl alumno pregunta: {prompt}"
        
        # Generar respuesta
        response = model.generate_content(pregunta_completa)
        
        if response.text:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    except Exception as e:
        # Si el 1.5-flash falla por cuota, intentamos el 1.5-pro como último recurso
        try:
            model_pro = genai.GenerativeModel(model_name="gemini-1.5-pro")
            response = model_pro.generate_content(f"{st.secrets['MY_SECRET_PROMPT']}\n\n{prompt}")
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e2:
            st.error(f"Lo siento, Antonio. Error de conexión: {e2}")
            st.info("Por favor, dale a 'Reboot App' en el panel de Streamlit.")
