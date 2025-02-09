import streamlit as st
import requests
import time
import docx
from docx.shared import Pt
import os

# Configuración de la API
API_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]

# Función para generar el contenido de un capítulo
def generar_capitulo(tema, capitulo_num):
    prompt = f"Escribe un capítulo de entre 900 y 1200 palabras sobre {tema}. Este es el capítulo número {capitulo_num}."
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen-plus",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Error al generar el capítulo {capitulo_num}: {response.status_code}")
        return None

# Función para crear un archivo Word
def crear_word(tema, capitulos):
    doc = docx.Document()
    doc.add_heading(tema, 0)
    for i, capitulo in enumerate(capitulos, 1):
        doc.add_heading(f"Capítulo {i}", level=1)
        doc.add_paragraph(capitulo)
    return doc

# Interfaz de Streamlit
st.title("Generador de Libros")
tema = st.text_input("Introduce el tema del libro:")

if tema:
    st.write(f"Generando un libro sobre: {tema}")
    capitulos = []
    progress_bar = st.progress(0)
    for i in range(1, 10):
        st.write(f"Generando capítulo {i}...")
        capitulo = generar_capitulo(tema, i)
        if capitulo:
            capitulos.append(capitulo)
            progress_bar.progress(i / 9)
            time.sleep(2)  # Pausa entre capítulos
        else:
            break

    if len(capitulos) == 9:
        st.success("¡Libro generado con éxito!")
        
        # Mostrar el libro en HTML
        st.write("## Libro Generado")
        for i, capitulo in enumerate(capitulos, 1):
            st.write(f"### Capítulo {i}")
            st.write(capitulo)

        # Crear y ofrecer descarga del archivo Word
        doc = crear_word(tema, capitulos)
        doc_path = f"{tema}.docx"
        doc.save(doc_path)
        with open(doc_path, "rb") as f:
            st.download_button(
                label="Descargar libro en formato Word",
                data=f,
                file_name=doc_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        os.remove(doc_path)

# Footer
st.markdown("---")
st.markdown("© [Hablemos bien](https://hablemosbien.org)")
