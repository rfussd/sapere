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
        "wake_time": "04:00",
        "commute_start": "04:45",
        "school_start": "07:00",
        "school_end": "13:00",
        "home_arrival": "16:00",
        "study_window_start": "17:00",
        "study_window_end": "20:30",
        "bed_time": "21:00",
    }

if "onboarding_done" not in st.session_state:
    st.session_state.onboarding_done = False


def _get_priority(mastery: int, due: int, total: int) -> tuple[str, str, str]:
    if mastery < 40 or (total > 0 and due > total * 0.5):
        return "🔴 ALTA", "A", "red"
    elif mastery < 70 or (total > 0 and due > total * 0.3):
        return "🟡 MEDIA", "B", "yellow"
    else:
        return "🟢 BAJA", "C", "green"


with st.sidebar:
    st.title("🧠 Sapere")
    streak = get_streak_count()
    st.metric("🔥 Racha", f"{streak} dias")
    st.markdown("---")

    page = st.radio(
        "Navegacion",
        ["Inicio", "Subir Temario", "🚌 Modo Traslado", "🌙 Cierre Nocturno", "⚙ Configuracion"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption(f"Modelo: {config.gemini_model}")

if page == "Inicio":
    st.title("🧠 Sapere")
    st.caption("Tu tutor cognitivo de elite — neurociencia + IA para aprender al maximo.")

    subjects = get_all_subjects()
    if not subjects:
        st.info("No tienes materias todavia. Ve a 'Subir Temario' para empezar.")
    else:
        subjects_a, subjects_b, subjects_c = [], [], []
        icon_map = {"academic": "🎓", "language": "🌍", "tech": "💻", "code": "🐍"}

        for s in subjects:
            p = get_subject_progress(s["id"])
            mastery = int(p.get("avg_mastery", 0) * 100) if p.get("avg_mastery") else 0
            due = p.get("due_flashcards", 0) or 0
            total = p.get("total_flashcards", 0) or 0
            _, level, _ = _get_priority(mastery, due, total)
            item = (s, p, mastery, due, total)
            if level == "A":
                subjects_a.append(item)
            elif level == "B":
                subjects_b.append(item)
            else:
                subjects_c.append(item)

        for label, lst in [("🔴 Prioridad ALTA — Enfocate aqui", subjects_a), ("🟡 Prioridad MEDIA — Manten al dia", subjects_b), ("🟢 Prioridad BAJA — Repaso ligero", subjects_c)]:
            if not lst:
                continue
            st.markdown(f"### {label}")
            for s, p, mastery, due, total in lst:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        icon = icon_map.get(s.get("mode", "academic"), "🎓")
                        st.write(f"{icon} **{s['name']}**")
                    with col2:
                        st.metric("Dominio", f"{mastery}%")
                    with col3:
                        st.write(f"📝 {due} pend.")
                    with col4:
                        if total > 0:
                            if st.button("▶ Estudiar", key=f"sbj_{s['id']}"):
                                st.session_state.study_subject_id = s["id"]
                                st.rerun()

    st.markdown("---")
    st.subheader("📊 Resumen semanal")
    total_due = sum(get_subject_progress(s["id"]).get("due_flashcards", 0) or 0 for s in get_all_subjects())
    total_all = sum(get_subject_progress(s["id"]).get("total_flashcards", 0) or 0 for s in get_all_subjects())
    c1, c2, c3 = st.columns(3)
    c1.metric("Materias", len(subjects) if subjects else 0)
    c2.metric("Pendientes hoy", total_due)
    c3.metric("Total flashcards", total_all)

elif page == "Subir Temario":
    from sapere.ui.upload import show_upload_page
    show_upload_page()

elif page == "🚌 Modo Traslado":
    from sapere.ui.mobile import show_mobile_page
    show_mobile_page()

elif page == "🌙 Cierre Nocturno":
    st.title("🌙 Cierre Nocturno")
    st.caption("Sesion ligera antes de dormir. Las flashcards mas debiles del dia. Sin presion.")
    now = datetime.now()
    if now.hour < 20:
        st.info("El cierre nocturno es mas efectivo entre 8-10 PM, justo antes de dormir.")
    all_due = get_due_flashcards(subject_id=None, limit=10)
    if not all_due:
        st.success("Sin flashcards pendientes. Buen trabajo!")
        st.balloons()
    else:
        st.write(f"🔖 {len(all_due)} flashcards fragiles para esta noche.")
        for key in ["night_active", "night_idx", "night_show", "night_count"]:
            if key not in st.session_state:
                st.session_state[key] = False if "show" in key or "active" in key else 0

        if not st.session_state.night_active:
            if st.button("🌙 Iniciar cierre nocturno", type="primary", use_container_width=True):
                st.session_state.night_active = True
                st.session_state.night_idx = 0
                st.session_state.night_show = False
                st.session_state.night_count = 0
                st.rerun()
        else:
            idx = st.session_state.night_idx
            if idx >= len(all_due):
                st.success(f"🌙 {st.session_state.night_count} flashcards. A dormir!")
                st.balloons()
                for k in ["night_active", "night_idx", "night_show", "night_count"]:
                    del st.session_state[k]
            else:
                fc = all_due[idx]
                st.progress((idx + 1) / len(all_due))
                st.markdown("---")
                st.markdown(f"### 🌙 {fc['question']}")
                if not st.session_state.night_show:
                    if st.button("Revelar", type="primary", use_container_width=True):
                        st.session_state.night_show = True
                        st.rerun()
                else:
                    st.markdown(f"#### {fc['answer']}")
                    st.caption("Cierra los ojos, repite mentalmente la respuesta.")
                    from sapere.study.flashcard import review_flashcard
                    from sapere.domain.enums import ReviewScore
                    review_flashcard(fc["id"], ReviewScore.HARD)
                    st.session_state.night_count += 1
                    st.session_state.night_idx += 1
                    st.session_state.night_show = False
                    st.rerun()

elif page == "⚙ Configuracion":
    st.title("⚙ Configuracion")
    st.caption("Ajusta tus horarios. Sapere se adapta automaticamente.")

    st.subheader("⏰ Horario personal")

    settings = st.session_state.user_settings

    col1, col2 = st.columns(2)
    with col1:
        settings["wake_time"] = st.text_input("Hora de despertar", settings["wake_time"])
        settings["commute_start"] = st.text_input("Salida de casa", settings["commute_start"])
        settings["school_start"] = st.text_input("Entrada a clase", settings["school_start"])
        settings["home_arrival"] = st.text_input("Llegada a casa", settings["home_arrival"])
    with col2:
        settings["study_window_start"] = st.text_input("Inicio estudio en casa", settings["study_window_start"])
        settings["study_window_end"] = st.text_input("Fin estudio en casa", settings["study_window_end"])
        settings["bed_time"] = st.text_input("Hora de dormir", settings["bed_time"])

    st.subheader("🤖 IA")
    st.write(f"Modelo: **{config.gemini_model}**")
    st.write(f"API Key: {'Configurada ✅' if config.gemini_api_key else 'Falta ❌'}")

    st.subheader("📊 Estadisticas")
    from sapere.infrastructure.database import get_db_path
    db_path = get_db_path()
    if __import__("os").path.exists(db_path):
        db_size = __import__("os").path.getsize(db_path) / 1024
        st.write(f"Base de datos: `{db_path}` ({db_size:.1f} KB)")
    else:
        st.write("Base de datos: No creada aun")

    if st.button("💾 Guardar configuracion", type="primary", use_container_width=True):
        st.session_state.user_settings = settings
        st.success("Configuracion guardada.")
        st.balloons()

if "study_subject_id" in st.session_state and st.session_state.study_subject_id:
    with st.sidebar:
        if st.button("← Volver al inicio"):
            st.session_state.study_subject_id = None
            st.rerun()
    from sapere.ui.study import show_study_page
    show_study_page(st.session_state.study_subject_id)
