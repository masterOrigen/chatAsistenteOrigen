import streamlit as st
from openai import OpenAI
import time
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Asistente AI", page_icon="🤖")

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
        # Crear un nuevo hilo
        thread = client.beta.threads.create()

        # Añadir el mensaje del usuario al hilo
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Ejecutar el asistente
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # Esperar a que el asistente complete la tarea
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Obtener la respuesta del asistente
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = messages.data[0].content[0].text.value

        return assistant_message

    except Exception as e:
        return f"Error: {str(e)}"

# Interfaz de usuario de Streamlit
st.title("Asistente AI")

# Área de entrada del usuario
user_input = st.text_input("Tu pregunta:", key="user_input")

# Botón para enviar la pregunta
if st.button("Enviar"):
    if user_input:
        with st.spinner('El asistente está pensando...'):
            response = interact_with_assistant(user_input)
        st.session_state.messages.append(("user", user_input))
        st.session_state.messages.append(("assistant", response))
    else:
        st.warning("Por favor, ingresa una pregunta.")

# Mostrar el historial de mensajes
for role, content in st.session_state.messages:
    st.session_state.message_counter += 1
    if role == "user":
        st.text_input("Tú:", value=content, key=f"user_{st.session_state.message_counter}", disabled=True)
    else:
        st.text_area("Asistente:", value=content, key=f"assistant_{st.session_state.message_counter}", disabled=True)
