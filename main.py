"""Sapere — Tu tutor cognitivo de elite."""

import streamlit as st
from datetime import datetime

from sapere.config import config
from sapere.infrastructure.database import (
    ensure_schema, get_all_subjects, get_streak_count, get_subject_progress,
    get_due_flashcards,
)
from sapere.ui.theme import GLOBAL_CSS, PAGE_CONFIG
from sapere.study.planner import calculate_plan

st.set_page_config(**PAGE_CONFIG)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
ensure_schema()

MODE = {"academic": "🎓", "language": "🌍", "tech": "💻", "code": "🐍"}
MODE_COLORS = {"academic": "#58a6ff", "language": "#7ee787", "tech": "#d29922", "code": "#bc8cff"}

if "user_settings" not in st.session_state:
    st.session_state.user_settings = {
        "wake_time": "04:00", "commute_start": "04:45",
        "home_arrival": "16:00", "study_window_start": "17:00",
        "study_window_end": "20:30", "bed_time": "21:00",
    }
if "study_subject_id" not in st.session_state:
    st.session_state.study_subject_id = None

# Study mode: full-screen clean view
if st.session_state.study_subject_id:
    with st.sidebar:
        subj = get_subject(st.session_state.study_subject_id)
        st.markdown("### 🧠 Sapere")
        if subj:
            st.caption(f"Estudiando: {subj.get('name', '')}")
        if st.button("← Volver al Dashboard", use_container_width=True):
            for k in ["session_active", "flashcards", "current_flashcard_index", "show_answer",
                       "reviewed_count", "study_session_id", "timer_start", "timer_duration",
                       "timer_breaks_taken", "timer_on_break", "curiosity_gap_shown"]:
                if k in st.session_state: del st.session_state[k]
            st.session_state.study_subject_id = None
            st.rerun()
    from sapere.ui.study import show_study_page
    show_study_page(st.session_state.study_subject_id)

else:
    # Dashboard mode
    with st.sidebar:
        st.markdown('<div style="text-align:center;padding:12px 0">', unsafe_allow_html=True)
        st.markdown("### 🧠 Sapere")
        streak = get_streak_count()
        if streak > 0:
            st.metric("🔥 Racha", f"{streak} días")
        else:
            st.caption("Comienza tu racha")
        st.markdown('</div>', unsafe_allow_html=True)

        page = st.radio("", ["🏠 Dashboard", "📤 Nueva Materia", "🚌 Traslado", "🌙 Cierre", "⚙ Ajustes"], label_visibility="collapsed")
        st.markdown("---")
        st.caption(f"⚡ {config.gemini_model}")

    if page == "🏠 Dashboard":
        subjects = get_all_subjects()
        all_due = get_due_flashcards(subject_id=None, limit=999)

        st.markdown('<div style="max-width:960px;margin:0 auto">', unsafe_allow_html=True)

        now = datetime.now()
        if 4 <= now.hour < 12: greeting = "Buenos días"
        elif 12 <= now.hour < 19: greeting = "Buenas tardes"
        else: greeting = "Buenas noches"
        st.markdown(f"## {greeting} 👋")

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("📚 Materias", len(subjects))
        with c2: st.metric("📝 Pendientes", len(all_due))
        with c3: st.metric("🗂 Total", sum(get_subject_progress(s["id"]).get("total_flashcards", 0) or 0 for s in subjects))
        with c4: st.metric("🔥 Racha", f"{streak} d")

        st.markdown("---")

        if not subjects:
            st.info("Crea tu primera materia en 'Nueva Materia'")
        else:
            plan = calculate_plan(st.session_state.user_settings.get("upiicsa_start", ""))
            days_left = plan["days_left"]

            if days_left > 0:
                cd = "#f85149" if days_left <= 7 else "#d29922" if days_left <= 14 else "#58a6ff"
                st.markdown(f"""<div style="text-align:center;margin:4px 0"><span style="font-size:13px;color:#8b949e">Dias para UPIICSA:</span><span style="font-size:28px;font-weight:700;color:{cd};margin-left:8px">{days_left}</span></div>""", unsafe_allow_html=True)
            else:
                st.info("🎒 Modo UPIICSA. 1 materia/dia + traslados.")

            st.markdown("---")
            st.subheader("🎯 Plan de hoy")

            if not plan["today"]:
                st.success("Sin pendientes. Repasa ejercicios o modo examen.")
            else:
                today_cols = st.columns(len(plan["today"]))
                for i, item in enumerate(plan["today"]):
                    u, due, ds, mastery, s = item
                    icon = MODE.get(s.get("mode", "academic"), "🎓")
                    with today_cols[i]:
                        st.markdown(f"""<div style="background:#131820;border:1px solid #f85149;border-radius:12px;padding:16px">
                        <div style="font-size:12px;color:#f85149;margin-bottom:4px">🔴 PRIORITARIO · {due} pend.</div>
                        <div style="font-size:18px;font-weight:700">{icon} {s['name']}</div>
                        <div style="font-size:12px;color:#8b949e;margin-top:4px">{int(mastery*100) if mastery else 0}% · {ds}d sin estudiar</div></div>""", unsafe_allow_html=True)
                        if st.button(f"▶ Estudiar", key=f"plan_{s['id']}", use_container_width=True):
                            st.session_state.study_subject_id = s["id"]
                            st.rerun()

            if plan["tomorrow"]:
                st.caption("**Mañana:** " + " · ".join(f"{MODE.get(i[4].get('mode','academic'),'🎓')} {i[4]['name']}" for i in plan["tomorrow"]))

            st.markdown("---")
            st.subheader("Todas las materias")

            for item in plan["all_subjects"]:
                color = MODE_COLORS.get(item["mode"], "#58a6ff")
                icon = MODE.get(item["mode"], "🎓")
                badge_color, badge_text = ("#7ee787", "Dominado") if item["mastery"] >= 80 else ("#d29922", "Progreso") if item["mastery"] >= 50 else ("#f85149", "Prioritario") if item["due"] > 0 else ("#8b949e", "Nuevo")

                with st.container(border=True):
                    r1 = st.columns([3, 1, 1, 0.8])
                    r1[0].markdown(f"### {icon} {item['name']}")
                    r1[1].markdown(f"<span style='background:{badge_color}20;color:{badge_color};padding:2px 8px;border-radius:6px;font-size:12px;font-weight:600'>{badge_text}</span>", unsafe_allow_html=True)
                    r1[1].caption(f"{item['mastery']}% · {item['days_since']}d")
                    if item["due"] > 0:
                        r1[2].markdown(f"<span style='color:#f85149;font-size:14px;font-weight:600'>📝 {item['due']}</span>", unsafe_allow_html=True)
                    else:
                        r1[2].markdown("<span style='color:#7ee787'>✅</span>", unsafe_allow_html=True)
                    if r1[3].button("▶", key=f"g_{item['id']}", help=f"Estudiar"):
                        st.session_state.study_subject_id = item["id"]
                        st.rerun()
                    if item["due"] > 0 or item["mastery"] > 0:
                        pct = max(0.02, item["mastery"] / 100)
                        st.markdown(f"""<div style="height:3px;background:#1e2733;border-radius:2px;margin:2px 0"><div style="width:{pct*100}%;height:100%;background:{color};border-radius:2px"></div></div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    elif page == "📤 Nueva Materia":
        from sapere.ui.upload import show_upload_page
        show_upload_page()

    elif page == "🚌 Traslado":
        from sapere.ui.mobile import show_mobile_page
        show_mobile_page()

    elif page == "🌙 Cierre":
        st.title("🌙 Cierre Nocturno")
        st.caption("Repaso ligero antes de dormir.")
        if datetime.now().hour < 20:
            st.info("Mas efectivo entre 8-10 PM, antes de dormir.")
        all_due = get_due_flashcards(subject_id=None, limit=10)
        if not all_due:
            st.success("✨ Sin pendientes. Buen trabajo!")
            st.balloons()
        else:
            st.write(f"🔖 {len(all_due)} flashcards para esta noche.")
            for k in ["n_active", "n_idx", "n_show", "n_count"]:
                if k not in st.session_state: st.session_state[k] = False if "show" in k or "active" in k else 0
            if not st.session_state.n_active:
                if st.button("🌙 Iniciar", type="primary", use_container_width=True):
                    st.session_state.n_active = st.session_state.n_idx = st.session_state.n_count = 0
                    st.session_state.n_show = False
                    st.rerun()
            else:
                idx = st.session_state.n_idx
                if idx >= len(all_due):
                    st.success(f"🌙 {st.session_state.n_count} repasadas. A dormir!")
                    st.balloons()
                    for k in ["n_active", "n_idx", "n_show", "n_count"]: del st.session_state[k]
                else:
                    fc = all_due[idx]
                    st.progress((idx+1)/len(all_due))
                    st.markdown(f"### {fc['question']}")
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
        s = st.session_state.user_settings
        c1, c2 = st.columns(2)
        with c1:
            s["wake_time"] = st.text_input("Despertar", s["wake_time"])
            s["commute_start"] = st.text_input("Salida", s["commute_start"])
            s["home_arrival"] = st.text_input("Llegada", s["home_arrival"])
            s["upiicsa_start"] = st.text_input("Inicio UPIICSA (YYYY-MM-DD)", s.get("upiicsa_start", ""))
        with c2:
            s["study_window_start"] = st.text_input("Inicio estudio", s["study_window_start"])
            s["study_window_end"] = st.text_input("Fin estudio", s["study_window_end"])
            s["bed_time"] = st.text_input("Dormir", s["bed_time"])
        if st.button("💾 Guardar", type="primary"):
            st.session_state.user_settings = s
            st.success("Guardado.")
