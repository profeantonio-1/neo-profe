import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Diagnóstico Neo", page_icon="🛠️")
st.title("🛠️ Modo Diagnóstico: Buscando a Neo")

# 1. Configurar API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    st.success("✅ La API Key se ha cargado correctamente.")
except Exception as e:
    st.error(f"❌ Error al cargar la API Key: {e}")
    st.stop()

# 2. ESCANEAR MODELOS DISPONIBLES
st.write("📡 Conectando con Google para ver qué modelos tienes activos...")

try:
    # Pedimos la lista oficial a tu cuenta
    listado_modelos = list(genai.list_models())
    
    encontrados = []
    
    st.subheader("📋 Lista oficial de modelos en tu cuenta:")
    
    for m in listado_modelos:
        # Filtramos solo los que sirven para chatear (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            st.code(f"Nombre: {m.name}")
            encontrados.append(m.name)
            
    if not encontrados:
        st.error("⚠️ Tu cuenta conecta con Google, pero Google dice que NO tienes modelos de texto disponibles. (Lista vacía).")
    else:
        st.success(f"¡Éxito! Hemos encontrado {len(encontrados)} modelos posibles.")
        st.info("Antonio, copia la lista de nombres que ves arriba y pégala en el chat con la IA.")

except Exception as e:
    st.error("❌ ERROR CRÍTICO AL LISTAR MODELOS:")
    st.error(e)
    st.warning("Si sale error 404 aquí, es que la API Key no tiene permisos de 'Generative Language'.")

# Botón para recargar
if st.button("Volver a escanear"):
    st.rerun()
