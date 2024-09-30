import streamlit as st
from openai import OpenAI
import time
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Asistente AI", page_icon="🤖", layout="wide")

# Inicialización de la sesión de estado
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0

# Configuración de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
assistant_id = os.getenv('ASSISTANT_ID')

# Función para interactuar con el asistente
def interact_with_assistant(user_input):
    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value
    except Exception as e:
        return f"Error: {str(e)}"

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stTextArea textarea {
        background-color: transparent;
        border: none;
    }
    .stTextInput textarea {
        height: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

# Interfaz de usuario de Streamlit
st.title("Asistente AI")

# Mensaje de bienvenida y lista de archivos
if not st.session_state.messages:
    welcome_message = interact_with_assistant("Saluda de esta manera exacta: 'Bienvenido, cuéntame que información necesitas para tu estrategia y buscaré en mi base de datos la mejor selección en diversos estudios' y luego proporciona la LISTA COMPLETA DE LOS ARCHIVOS QUE TIENES EN TU BASE DE CONOCIMIENTO. Es obligatorio listar todos los archivos sin excepción.")
    st.session_state.messages.append(("assistant", welcome_message))

# Mostrar el historial de mensajes
for role, content in st.session_state.messages:
    st.session_state.message_counter += 1
    if role == "user":
        st.text_area("Tú:", value=content, key=f"user_{st.session_state.message_counter}", disabled=True, height=100)
    else:
        st.text_area("Asistente:", value=content, key=f"assistant_{st.session_state.message_counter}", disabled=True, height=200)

# Área de entrada del usuario (siempre al final)
user_input = st.text_area("Tu pregunta sobre los archivos:", key="user_input", height=100)

# Botón para enviar la pregunta
if st.button("Enviar"):
    if user_input:
        with st.spinner('El asistente está pensando...'):
            response = interact_with_assistant(user_input)
        st.session_state.messages.append(("user", user_input))
        st.session_state.messages.append(("assistant", response))
        st.rerun()
    else:
        st.warning("Por favor, ingresa una pregunta.")
