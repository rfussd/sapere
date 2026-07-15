import streamlit as st
import base64
import json

from sapere.infrastructure import database
from sapere.domain.enums import ReviewScore
from sapere.study.flashcard import get_due_flashcards, review_flashcard
from sapere.study.offline import generate_offline_flashcards


def show_mobile_page():
    st.title("🚌 Modo Traslado")
    st.caption("Flashcards para el celular en el camion/Metro.")

    subjects = database.get_all_subjects()
    if not subjects:
        st.warning("No hay materias. Crea una primero desde la PC.")
        return

    if "mobile_subject" not in st.session_state:
        st.session_state.mobile_subject = subjects[0]["id"]
    if "mobile_active" not in st.session_state:
        st.session_state.mobile_active = False
    if "mobile_fc" not in st.session_state:
        st.session_state.mobile_fc = []
    if "mobile_idx" not in st.session_state:
        st.session_state.mobile_idx = 0
    if "mobile_show" not in st.session_state:
        st.session_state.mobile_show = False
    if "mobile_count" not in st.session_state:
        st.session_state.mobile_count = 0

    if not st.session_state.mobile_active:
        subj_options = {s["name"]: s["id"] for s in subjects}
        selected = st.selectbox("Materia", list(subj_options.keys()), key="mobile_subj")
        st.session_state.mobile_subject = subj_options[selected]
        count = st.slider("Cuantas flashcards", 10, 50, 20)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚌 Repasar aqui", type="primary", use_container_width=True):
                _start_mobile_session(subj_options[selected], count)
        with col2:
            if st.button("📥 Exportar para el camion", use_container_width=True, help="Genera un archivo HTML que funciona SIN internet en tu celular"):
                html = generate_offline_flashcards(subject_id=subj_options[selected], limit=count)
                if html:
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(
                        f'<a href="data:text/html;base64,{b64}" download="sapere_traslado.html">'
                        f'<button style="width:100%;padding:12px;background:#238636;color:white;'
                        f'border:none;border-radius:8px;font-size:16px;cursor:pointer">'
                        f'📥 Descargar HTML</button></a>',
                        unsafe_allow_html=True,
                    )
                    st.success("Envia el archivo a tu celular (WhatsApp/Telegram) y abrilo con Chrome.")
                else:
                    st.warning("Sin flashcards pendientes.")
        return

    fcs = st.session_state.mobile_fc
    idx = st.session_state.mobile_idx

    if idx >= len(fcs):
        st.success(f"Repaso completado: {st.session_state.mobile_count} flashcards")
        st.balloons()
        for k in ["mobile_active", "mobile_fc", "mobile_idx", "mobile_show", "mobile_count"]:
            if k in st.session_state:
                del st.session_state[k]
        if st.button("🔄 Otro repaso", use_container_width=True):
            st.rerun()
        return

    fc = fcs[idx]
    st.progress((idx + 1) / len(fcs))
    st.caption(f"{idx + 1} de {len(fcs)}")

    st.markdown("---")
    st.markdown(f"### ❓ {fc['question']}")
    if fc.get("hint"):
        st.caption(f"💡 {fc['hint']}")

    if not st.session_state.mobile_show:
        if st.button("📝 REVELAR", type="primary", use_container_width=True):
            st.session_state.mobile_show = True
            st.rerun()
    else:
        st.markdown(f"### ✅ {fc['answer']}")
        st.markdown("---")
        st.markdown("**Recorde?**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔴 NI IDEA", use_container_width=True, key=f"m1_{idx}"):
                review_flashcard(fc["id"], ReviewScore.AGAIN)
                _mobile_next()
        with c2:
            if st.button("🟠 DIFICIL", use_container_width=True, key=f"m2_{idx}"):
                review_flashcard(fc["id"], ReviewScore.HARD)
                _mobile_next()
        c3, c4 = st.columns(2)
        with c3:
            if st.button("🟢 BIEN", use_container_width=True, key=f"m3_{idx}"):
                review_flashcard(fc["id"], ReviewScore.GOOD)
                _mobile_next()
        with c4:
            if st.button("🟣 FACIL", use_container_width=True, key=f"m4_{idx}"):
                review_flashcard(fc["id"], ReviewScore.EASY)
                _mobile_next()

    st.markdown("---")
    st.caption("💡 Gira el celular horizontal para botones mas grandes.")

    st.markdown("---")
    st.subheader("🔄 Sincronizar repasos offline")
    sync_data = st.text_area("Pega aqui el codigo del archivo HTML del celular:", height=100, placeholder='[{"id": 1, "score": 3}, ...]')
    if st.button("🔄 Sincronizar", use_container_width=True) and sync_data:
        try:
            data = json.loads(sync_data)
            for item in data:
                review_flashcard(item["id"], ReviewScore(item["score"]))
            st.success(f"✅ {len(data)} revisiones sincronizadas!")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}. Asegurate de pegar el JSON completo.")


def _start_mobile_session(subject_id, count):
    fcs = database.get_connection().execute(
        """SELECT f.* FROM flashcards f
           JOIN topics t ON f.topic_id = t.id
           WHERE t.subject_id = ? AND f.next_review_at <= datetime('now')
           ORDER BY f.next_review_at ASC LIMIT ?""",
        (subject_id, count),
    ).fetchall()
    database.get_connection().close()
    st.session_state.mobile_fc = [dict(f) for f in fcs]
    st.session_state.mobile_idx = 0
    st.session_state.mobile_show = False
    st.session_state.mobile_count = 0
    st.session_state.mobile_active = True
    st.rerun()


def _mobile_next():
    st.session_state.mobile_count += 1
    st.session_state.mobile_show = False
    st.session_state.mobile_idx += 1
    st.rerun()
