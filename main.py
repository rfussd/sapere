"""Sapere — Tutores de estudio con IA. Dark theme premium, clean layout."""

import streamlit as st
from datetime import datetime

from sapere.config import config
from sapere.infrastructure.database import (
    ensure_schema, get_all_subjects, get_streak_count, get_subject_progress,
    get_due_flashcards,
)
from sapere.ui.theme import GLOBAL_CSS, PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

ensure_schema()

if "user_settings" not in st.session_state:
    st.session_state.user_settings = {
        "wake_time": "04:00", "commute_start": "04:45",
        "home_arrival": "16:00", "study_window_start": "17:00",
        "study_window_end": "20:30", "bed_time": "21:00",
    }

MODE = {"academic": "🎓", "language": "🌍", "tech": "💻", "code": "🐍"}
MODE_COLORS = {"academic": "#58a6ff", "language": "#7ee787", "tech": "#d29922", "code": "#bc8cff"}

with st.sidebar:
    st.markdown('<div style="text-align:center;padding:12px 0">', unsafe_allow_html=True)
    st.markdown("### 🧠 Sapere")
    streak = get_streak_count()
    if streak > 0:
        st.metric("🔥 Racha", f"{streak} días")
    else:
        st.caption("Comienza tu racha hoy")
    st.markdown('</div>', unsafe_allow_html=True)

    page = st.radio("", ["🏠 Dashboard", "📤 Nueva Materia", "🚌 Traslado", "🌙 Cierre", "⚙ Ajustes"], label_visibility="collapsed")

    st.markdown("---")
    st.caption(f"⚡ {config.gemini_model}")

if page == "🏠 Dashboard":
    subjects = get_all_subjects()
    all_due = get_due_flashcards(subject_id=None, limit=999)

    st.markdown('<div style="max-width:960px;margin:0 auto">', unsafe_allow_html=True)

    now = datetime.now()
    hour = now.hour
    if 4 <= hour < 12:
        greeting = "Buenos días"
    elif 12 <= hour < 19:
        greeting = "Buenas tardes"
    else:
        greeting = "Buenas noches"

    st.markdown(f"## {greeting} 👋")

    c1, c2, c3, c4 = st.columns(4)
    total_all = sum(get_subject_progress(s["id"]).get("total_flashcards", 0) or 0 for s in subjects)
    total_due = len(all_due)
    with c1:
        st.metric("📚 Materias", len(subjects))
    with c2:
        st.metric("📝 Pendientes", total_due)
    with c3:
        st.metric("🗂 Total", total_all)
    with c4:
        st.metric("🔥 Racha", f"{streak} d")

    st.markdown("---")

    if not subjects:
        st.info("🎉 Bienvenido a Sapere. Ve a 'Nueva Materia' para crear tu primera materia.")
    else:
        st.subheader("Tus materias")

        for s in subjects:
            p = get_subject_progress(s["id"])
            mastery = int(p.get("avg_mastery", 0) * 100) if p.get("avg_mastery") else 0
            due = p.get("due_flashcards", 0) or 0
            total = p.get("total_flashcards", 0) or 0
            mode = s.get("mode", "academic")
            color = MODE_COLORS.get(mode, "#58a6ff")
            icon = MODE.get(mode, "🎓")

            if mastery >= 80:
                priority_color = "#7ee787"
                priority_badge = "Dominado"
            elif mastery >= 50:
                priority_color = "#d29922"
                priority_badge = "En progreso"
            elif total > 0:
                priority_color = "#f85149"
                priority_badge = "Prioritario"
            else:
                priority_color = "#8b949e"
                priority_badge = "Nuevo"

            with st.container(border=True):
                r1_cols = st.columns([4, 1, 1, 1])
                with r1_cols[0]:
                    st.markdown(f"### {icon} {s['name']}")
                with r1_cols[1]:
                    st.metric("Dominio", f"{mastery}%")
                with r1_cols[2]:
                    st.markdown(f"<span style='background:{priority_color}20;color:{priority_color};padding:4px 10px;border-radius:8px;font-size:13px;font-weight:600'>{priority_badge}</span>", unsafe_allow_html=True)
                with r1_cols[3]:
                    st.write(f"📝 {due}" if due > 0 else "✅")

                if total > 0:
                    pct = mastery / 100 if mastery > 0 else 0.01
                    st.markdown(f"""<div style="height:4px;background:#21262d;border-radius:2px;margin:4px 0 8px">
                    <div style="width:{pct*100}%;height:100%;background:{color};border-radius:2px;transition:width 0.5s"></div></div>""", unsafe_allow_html=True)

                btn_cols = st.columns([1, 1, 1, 3])
                with btn_cols[0]:
                    if total > 0 and st.button("📝 Estudiar", key=f"go_{s['id']}", use_container_width=True):
                        st.session_state.study_subject_id = s["id"]
                        st.rerun()
                with btn_cols[1]:
                    if due < 5 and total > 0:
                        st.caption("Al día")
                with btn_cols[2]:
                    topics = __import__("sapere.infrastructure.database", fromlist=[""]).get_topics_for_subject(s["id"])
                    st.caption(f"{len(topics)} temas")

        st.markdown("---")
        st.caption(f"💡 {total_due} flashcards pendientes. Cada 20 min de estudio = ~15 flashcards. Tardarías ~{max(1, total_due // 15) * 20} min en ponerlas al día.")

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "📤 Nueva Materia":
    from sapere.ui.upload import show_upload_page
    show_upload_page()

elif page == "🚌 Traslado":
    from sapere.ui.mobile import show_mobile_page
    show_mobile_page()

elif page == "🌙 Cierre":
    st.title("🌙 Cierre Nocturno")
    st.caption("Repaso ligero antes de dormir. Sin presión, sin ejercicios.")
    now = datetime.now()
    if now.hour < 20:
        st.info("Más efectivo entre 8-10 PM, justo antes de dormir.")
    all_due = get_due_flashcards(subject_id=None, limit=10)
    if not all_due:
        st.success("✨ Sin pendientes. ¡Excelente día!")
        st.balloons()
    else:
        st.write(f"🔖 {len(all_due)} flashcards para esta noche.")
        for k in ["n_active", "n_idx", "n_show", "n_count"]:
            if k not in st.session_state:
                st.session_state[k] = False if "show" in k or "active" in k else 0
        if not st.session_state.n_active:
            if st.button("🌙 Iniciar", type="primary", use_container_width=True):
                st.session_state.n_active = True; st.session_state.n_idx = 0
                st.session_state.n_show = False; st.session_state.n_count = 0
                st.rerun()
        else:
            idx = st.session_state.n_idx
            if idx >= len(all_due):
                st.success(f"🌙 {st.session_state.n_count} repasadas. ¡A dormir!")
                st.balloons()
                for k in ["n_active", "n_idx", "n_show", "n_count"]: del st.session_state[k]
            else:
                fc = all_due[idx]
                st.progress((idx+1)/len(all_due))
                st.markdown(f"### 🌙 {fc['question']}")
                if not st.session_state.n_show:
                    if st.button("Revelar", type="primary", use_container_width=True):
                        st.session_state.n_show = True; st.rerun()
                else:
                    st.markdown(f"#### {fc['answer']}")
                    from sapere.study.flashcard import review_flashcard
                    from sapere.domain.enums import ReviewScore
                    review_flashcard(fc["id"], ReviewScore.HARD)
                    st.session_state.n_count += 1; st.session_state.n_idx += 1
                    st.session_state.n_show = False; st.rerun()

elif page == "⚙ Ajustes":
    st.title("⚙ Ajustes")
    st.caption("Tus horarios. Sapere se adapta.")
    s = st.session_state.user_settings
    c1, c2 = st.columns(2)
    with c1:
        s["wake_time"] = st.text_input("Despertar", s["wake_time"])
        s["commute_start"] = st.text_input("Salida", s["commute_start"])
        s["home_arrival"] = st.text_input("Llegada", s["home_arrival"])
    with c2:
        s["study_window_start"] = st.text_input("Inicio estudio", s["study_window_start"])
        s["study_window_end"] = st.text_input("Fin estudio", s["study_window_end"])
        s["bed_time"] = st.text_input("Dormir", s["bed_time"])
    st.caption(f"Modelo: {config.gemini_model}")
    if st.button("💾 Guardar", type="primary"):
        st.session_state.user_settings = s
        st.success("Guardado.")

if "study_subject_id" in st.session_state and st.session_state.study_subject_id:
    with st.sidebar:
        if st.button("← Dashboard", use_container_width=True):
            st.session_state.study_subject_id = None; st.rerun()
    from sapere.ui.study import show_study_page
    show_study_page(st.session_state.study_subject_id)
