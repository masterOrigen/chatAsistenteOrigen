import streamlit as st
from openai import OpenAI
import time
from dotenv import load_dotenv
import os
import re

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Asistente AI", page_icon="🤖", layout="wide")

# Inicialización de la sesión de estado
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0
if 'thinking' not in st.session_state:
    st.session_state.thinking = False

# Configuración de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
assistant_id = os.getenv('ASSISTANT_ID')

# Función para interactuar con el asistente
def interact_with_assistant(user_input):
    try:
        thread = client.beta.threads.create()
        
        instruction = ("Por favor, proporciona una respuesta lo más extensa y detallada posible. "
                       "Asegúrate de que la información sea precisa y basada únicamente en los datos de la base de vectores vs_VEqqVkUfZfFXnK0ALwzbTujp. "
                       "No uses información de ninguna otra fuente. "
                       "Si es relevante, incluye ejemplos o datos específicos de los documentos en esta base de conocimiento. "
                       "Si hay múltiples aspectos en la pregunta, abórdalos todos de manera exhaustiva.")
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"{instruction}\n\nPregunta del usuario: {user_input}"
        )
        
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value
        
        # Eliminar el texto "【4:0†source】" de la respuesta
        response = re.sub(r'【\d+:\d+†source】', '', response)
        
        return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Función para limpiar el chat
def clear_chat():
    st.session_state.messages = []
    st.session_state.message_counter = 0
    st.session_state.thinking = False

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stChatMessage {
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: flex-start;
    }
    .stChatMessage .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
        flex-shrink: 0;
        overflow: hidden;
    }
    .stChatMessage .avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .stChatMessage .content {
        flex-grow: 1;
    }
    .button-container {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Interfaz de usuario de Streamlit
st.title("Asistente AI")

# Mensaje de bienvenida
if not st.session_state.messages:
    welcome_message = "Bienvenido, cuéntame que información necesitas para tu estrategia y buscaré en mi base de datos la mejor selección en diversos estudios."
    st.session_state.messages.append(("assistant", welcome_message))

# Mostrar el historial de mensajes
for role, content in st.session_state.messages:
    st.session_state.message_counter += 1
    if role == "assistant":
        st.markdown(f"""
        <div class="stChatMessage">
            <div class="avatar">
                <img src="http://brainstorm.origenmedios.cl/wp-content/uploads/2024/09/favicoBrainstormOK2.png" alt="AI Avatar">
            </div>
            <div class="content">
                <p>{content}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="stChatMessage">
            <div class="avatar">Tú</div>
            <div class="content">
                <p>{content}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Mostrar el mensaje "El asistente está pensando" y el indicador de carga
if st.session_state.thinking:
    with st.spinner('El asistente está pensando...'):
        st.empty()

# Área de entrada del usuario
user_input = st.text_area("Tu pregunta:", key="text_input_1", height=100)

# Contenedor para los botones
st.markdown('<div class="button-container">', unsafe_allow_html=True)

# Columnas para los botones
col1, col2, col3 = st.columns([1, 10, 1])

with col1:
    # Botón Limpiar
    if st.button('Limpiar', key='limpiar'):
        clear_chat()
        st.rerun()

with col3:
    # Botón Enviar
    if st.button('Enviar', key='enviar'):
        if user_input:
            st.session_state.thinking = True
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Procesar la respuesta del asistente
if st.session_state.thinking and user_input:
    response = interact_with_assistant(user_input)
    st.session_state.messages.append(("user", user_input))
    st.session_state.messages.append(("assistant", response))
    st.session_state.thinking = False
    st.rerun()
