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
        
        instruction = ("Por favor, proporciona una respuesta lo más extensa y detallada posible. "
                       "Asegúrate de que la información sea precisa y basada en hechos. "
                       "Si es relevante, incluye ejemplos o datos específicos de los documentos en tu base de conocimiento. "
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
        return messages.data[0].content[0].text.value
    except Exception as e:
        return f"Error: {str(e)}"

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
        background-color: #0f52ba;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
        flex-shrink: 0;
    }
    .stChatMessage .content {
        flex-grow: 1;
    }
    .user-input-container {
        display: flex;
        align-items: center;
    }
    .user-input {
        flex-grow: 1;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-right: 10px;
    }
    .send-button {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

# Interfaz de usuario de Streamlit
st.title("Asistente AI")

# Mensaje de bienvenida
if not st.session_state.messages:
    welcome_message = interact_with_assistant("Saluda brevemente y menciona que tienes acceso a una base de conocimiento. Luego, di 'Estos son algunos de los archivos en mi base de conocimiento:' y lista SOLO algunos de los archivos que realmente están en tu base de vectores, sin inventar ninguno.")
    st.session_state.messages.append(("assistant", welcome_message))

# Mostrar el historial de mensajes
for role, content in st.session_state.messages:
    st.session_state.message_counter += 1
    if role == "assistant":
        st.markdown(f"""
        <div class="stChatMessage">
            <div class="avatar">AI</div>
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

# Área de entrada del usuario con botón de envío integrado
col1, col2 = st.columns([6,1])
with col1:
    user_input = st.text_area("Tu pregunta:", key="user_input", height=100)
with col2:
    send_button = st.button("➤")

# Lógica para enviar la pregunta
if send_button and user_input:
    with st.spinner('El asistente está pensando...'):
        response = interact_with_assistant(user_input)
    st.session_state.messages.append(("user", user_input))
    st.session_state.messages.append(("assistant", response))
    st.rerun()
elif send_button:
    st.warning("Por favor, ingresa una pregunta.")
