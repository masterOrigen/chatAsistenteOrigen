import streamlit as st
from openai import OpenAI
import time
from dotenv import load_dotenv
import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

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

# Configuración de la Vector Store
embeddings = OpenAIEmbeddings()
vector_store = FAISS.load_local("vs_VEqqVkUfZfFXnK0ALwzbTujp", embeddings, allow_dangerous_deserialization=True)

# Función para interactuar con el asistente
def interact_with_assistant(user_input):
    try:
        # Buscar información relevante en la vector store
        relevant_docs = vector_store.similarity_search(user_input, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Crear un nuevo hilo con el contexto y la pregunta del usuario
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Contexto: {context}\n\nPregunta del usuario: {user_input}"
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
    .user-input {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Interfaz de usuario de Streamlit
st.title("Asistente AI")

# Mensaje de bienvenida y lista de archivos
if not st.session_state.messages:
    welcome_message = "Bienvenido, cuéntame que información necesitas para tu estrategia y buscaré en mi base de datos la mejor selección en diversos estudios. Aquí está la lista completa de archivos en mi base de conocimiento:"
    file_list = vector_store.index_to_docstore_id.values()
    welcome_message += "\n" + "\n".join(file_list)
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
