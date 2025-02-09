import streamlit as st
import requests
import time
from docx import Document
from io import BytesIO

def generate_chapter(api_key, topic, audience, chapter_number):
    url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "Eres un asistente útil que escribe en español."},
            {"role": "user", "content": f"Escribe el capítulo {chapter_number} de un libro sobre {topic} dirigido a {audience} con 900-1200 palabras en español."}
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Error en la generación del capítulo.")

def create_word_document(chapters, title):
    doc = Document()
    doc.add_heading(title, level=1)
    for i, chapter in enumerate(chapters, 1):
        doc.add_heading(f"Capítulo {i}", level=2)
        doc.add_paragraph(chapter)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.title("Generador de Libros en HTML")
api_key = st.secrets["DASHSCOPE_API_KEY"]
topic = st.text_input("Introduce el tema del libro:")
audience = st.text_input("¿A quién va dirigido el libro?")
if st.button("Generar Libro") and topic and audience:
    chapters = []
    progress_bar = st.progress(0)
    for i in range(1, 10):
        chapter_content = generate_chapter(api_key, topic, audience, i)
        chapters.append(chapter_content)
        st.write(f"### Capítulo {i}")
        st.write(chapter_content)
        progress_bar.progress(i / 9)
        time.sleep(2)
    
    word_file = create_word_document(chapters, topic)
    st.download_button(label="Descargar en Word", data=word_file, file_name=f"{topic}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.markdown("""
    <footer style='text-align: center; padding: 10px;'>
        <a href='https://hablemosbien.org' target='_blank'>Copyright Hablemos bien</a>
    </footer>
""", unsafe_allow_html=True)
