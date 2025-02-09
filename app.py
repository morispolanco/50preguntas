import streamlit as st
import requests
from docx import Document
import time
from streamlit_extras.progress_bar import ProgressBar

# Configuración de la página
st.set_page_config(page_title="Generador de Libros", page_icon="📚", layout="wide")

# Footer personalizado
def add_footer():
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f8f9fa;
            padding: 10px 0;
            text-align: center;
            font-size: 14px;
        }
        </style>
        <div class="footer">
            Copyright © <a href="https://hablemosbien.org" target="_blank">Hablemos Bien</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Función para generar contenido usando Qwen
def generate_chapter(api_key, topic, chapter_number):
    url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    prompt = f"Escribe un capítulo de un libro sobre el tema '{topic}'. El capítulo debe tener entre 900 y 1200 palabras. Este es el capítulo número {chapter_number}."
    data = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Error al generar el capítulo: {response.text}")
        return None

# Función para guardar el libro en formato Word
def save_to_word(chapters, title):
    doc = Document()
    doc.add_heading(title, level=1)
    for i, chapter in enumerate(chapters, start=1):
        doc.add_heading(f"Capítulo {i}", level=2)
        doc.add_paragraph(chapter)
    filename = f"{title.replace(' ', '_')}.docx"
    doc.save(filename)
    return filename

# Interfaz de usuario
st.title("📚 Generador de Libros")
st.write("Proporcione un tema y genere automáticamente un libro de 9 capítulos.")

# Input del usuario
topic = st.text_input("Tema del libro:")
generate_button = st.button("Generar Libro")

if generate_button and topic:
    # Obtener la API Key desde los secrets de Streamlit
    api_key = st.secrets["API_KEY"]

    if not api_key:
        st.error("Por favor, configure su API Key en los secrets de Streamlit.")
    else:
        # Inicializar variables
        chapters = []
        progress_bar = ProgressBar(9, "Generando capítulos...")

        # Generar los capítulos
        for i in range(1, 10):
            chapter_content = generate_chapter(api_key, topic, i)
            if chapter_content:
                chapters.append(chapter_content)
                progress_bar.progress(i)
                time.sleep(1)  # Pausa entre capítulos

        # Guardar el libro en formato Word
        book_title = f"Libro sobre {topic}"
        word_filename = save_to_word(chapters, book_title)

        # Descargar el archivo Word
        with open(word_filename, "rb") as file:
            st.download_button(
                label="Descargar Libro en Word",
                data=file,
                file_name=word_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

# Añadir el footer
add_footer()
