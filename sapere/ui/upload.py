import streamlit as st
from pypdf import PdfReader
import io

from sapere.llm.gemini import GeminiFlash
from sapere.llm.base import LLMProvider
from sapere.extractor.syllabus import process_syllabus
from sapere.infrastructure import database

MODE_INFO = {
    "academic": {
        "icon": "🎓",
        "label": "Academico",
        "description": "Materias de la escuela. Flashcards con taxonomia de Bloom, metodo Feynman, SM-2.",
        "examples": "Calculo, Fisica, Administracion, Etica...",
    },
    "language": {
        "icon": "🌍",
        "label": "Idiomas",
        "description": "Aprende idiomas con contexto real. Frases completas, pronunciacion, cloze deletion.",
        "examples": "Ingles, Frances, Japones, Aleman...",
    },
    "tech": {
        "icon": "💻",
        "label": "Tech Skills",
        "description": "Programacion, comandos Linux, ciberseguridad. Flashcards practicas con sintaxis real.",
        "examples": "Python, Linux, Hacking Etico, AWS, Docker...",
    },
    "code": {
        "icon": "🐍",
        "label": "Programacion",
        "description": "Aprende a programar desde cero. Flashcards con snippets de codigo, ejercicios interactivos.",
        "examples": "Python, JavaScript, C, SQL...",
    },
}


def show_upload_page():
    st.header("📤 Crear nueva materia")

    st.markdown("### 🎯 ¿Que quieres aprender?")
    st.caption("Elige el tipo de contenido. Esto cambia como la IA genera las flashcards.")

    cols = st.columns(4)
    selected_mode = "academic"

    for i, (mode_key, info) in enumerate(MODE_INFO.items()):
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"### {info['icon']} {info['label']}")
                st.caption(info["description"])
                st.caption(f"*Ej: {info['examples']}*")
                if st.button(f"Seleccionar {info['label']}", key=f"mode_{mode_key}", use_container_width=True):
                    st.session_state.upload_mode = mode_key
                    st.rerun()

    if "upload_mode" not in st.session_state:
        st.session_state.upload_mode = "academic"

    mode = st.session_state.upload_mode
    mode_info = MODE_INFO[mode]

    st.markdown("---")
    st.markdown(f"**Modo seleccionado:** {mode_info['icon']} {mode_info['label']} — {mode_info['description']}")

    llm_provider = LLMProvider(primary=GeminiFlash())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📎 Subir PDF")
        uploaded = st.file_uploader("Selecciona tu documento PDF", type=["pdf"])
        if uploaded is not None:
            reader = PdfReader(io.BytesIO(uploaded.read()))
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            st.success(f"PDF leido: {len(text)} caracteres")
            st.text_area("Vista previa", text[:800], height=150)

            subject_name = st.text_input("Nombre", value=uploaded.name.replace(".pdf", ""))

            if st.button(f"{mode_info['icon']} Analizar con IA", type="primary", use_container_width=True, key="pdf_btn"):
                if not text.strip():
                    st.error("No se pudo extraer texto del PDF.")
                    return
                _process_syllabus(llm_provider, subject_name, text, mode)

    with col2:
        st.subheader("📝 Pegar contenido")
        raw_text = st.text_area(f"Describe que quieres aprender ({mode_info['label']})", height=200, key="manual_text")
        subject_name_manual = st.text_input("Nombre", key="manual_name")

        if st.button(f"{mode_info['icon']} Analizar contenido", type="primary", use_container_width=True, key="manual_btn"):
            if not raw_text.strip():
                st.error("Escribe el contenido primero.")
                return
            _process_syllabus(llm_provider, subject_name_manual or "Sin nombre", raw_text, mode)

    st.markdown("---")
    st.subheader("💡 Ejemplos rapidos por modo")

    if mode == "language":
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🇬🇧 Ingles Basico", use_container_width=True):
                _process_syllabus(
                    llm_provider, "Ingles Basico",
                    "Vocabulario esencial: saludos, numeros, colores, familia, comida, ropa, transporte, clima, "
                    "trabajo. Verbos basicos en presente: to be, to have, to go, to do, to make, to say. "
                    "Estructura de oraciones simples. Preguntas basicas. Pronombres personales. Adjetivos comunes.",
                    "language",
                )
        with col_b:
            if st.button("🇫🇷 Frances Basico", use_container_width=True):
                _process_syllabus(
                    llm_provider, "Frances Basico",
                    "Salutations, presentaciones, verbes etre/avoir, les nombres, la famille, nourriture, "
                    "vetements, couleurs. Articles definis/indefinis. Genre masculin/feminin. "
                    "Phrases de base. Conjugaison present.",
                    "language",
                )

    elif mode == "tech":
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🐧 Linux Fundamentals", use_container_width=True):
                _process_syllabus(
                    llm_provider, "Linux Fundamentals",
                    "Comandos basicos: ls, cd, pwd, mkdir, rm, cp, mv, cat, grep, find, chmod, chown, sudo. "
                    "Sistema de archivos. Permisos. Procesos (ps, kill, top). Redireccion y pipes. "
                    "Variables de entorno. Scripts bash basicos. Usuarios y grupos.",
                    "tech",
                )
        with col_b:
            if st.button("🛡 Hacking Etico", use_container_width=True):
                _process_syllabus(
                    llm_provider, "Hacking Etico",
                    "Fases del pentesting: reconocimiento, escaneo, explotacion. "
                    "Herramientas: nmap, metasploit, burp suite, wireshark, john the ripper, hydra, sqlmap. "
                    "Tipos de ataques: SQL injection, XSS, CSRF, buffer overflow, phishing. "
                    "OWASP Top 10. Escalada de privilegios. Post-explotacion.",
                    "tech",
                )

    elif mode == "academic":
        st.caption("Simplemente pega tu temario arriba o describe la materia.")

    elif mode == "code":
        st.subheader("🐍 Aprender a programar")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🐍 Python Basico", use_container_width=True):
                _process_syllabus(
                    llm_provider, "Python Basico",
                    "Variables y tipos de datos (int, float, str, bool). print() e input(). "
                    "Condicionales if/elif/else. Ciclos for y while. Listas y diccionarios. "
                    "Funciones: def, parametros, return. Manejo de archivos. "
                    "Try/except para errores. Modulos e imports.",
                    "code",
                )
        with col_b:
            if st.button("🐍 Python Intermedio", use_container_width=True):
                _process_syllabus(
                    llm_provider, "Python Intermedio",
                    "Clases y objetos (POO). Herencia y polimorfismo. Decoradores. "
                    "Generadores e iteradores. Context managers (with). "
                    "Type hints. Dataclasses. Archivos JSON y CSV. "
                    "Requests/APIs. SQLite basico. Testing con pytest.",
                    "code",
                )


def _process_syllabus(llm_provider, subject_name, raw_text, mode):
    with st.spinner(f"Generando flashcards con IA en modo {MODE_INFO[mode]['label']}..."):
        try:
            result = process_syllabus(
                llm=llm_provider,
                subject_name=subject_name,
                raw_text=raw_text,
                mode=mode,
            )
            st.success(
                f"Listo! {result['topics_created']} temas y {result['flashcards_created']} flashcards creadas."
            )
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
