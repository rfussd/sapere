"""Sapere — Your brain's best friend."""

import streamlit as st
from datetime import datetime

from sapere.config import config
from sapere.infrastructure.database import (
    ensure_schema, get_all_subjects, get_streak_count, get_subject_progress,
    get_due_flashcards, get_subject,
)
from sapere.ui.theme import GLOBAL_CSS, PAGE_CONFIG
from sapere.study.planner import calculate_plan

st.set_page_config(**PAGE_CONFIG)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
ensure_schema()


def _go_study(subject_id):
    st.session_state.study_subject_id = subject_id
    st.rerun()

MODE = {"academic": "🎓", "language": "🌍", "tech": "💻", "code": "🐍"}
COLORS = {
    "academic": {"bg": "#1a2332", "accent": "#58a6ff", "glow": "rgba(88,166,255,0.3)"},
    "code": {"bg": "#1f1832", "accent": "#bc8cff", "glow": "rgba(188,140,255,0.3)"},
    "tech": {"bg": "#1f1a0d", "accent": "#d29922", "glow": "rgba(210,153,34,0.3)"},
    "language": {"bg": "#0d1f18", "accent": "#3fb950", "glow": "rgba(63,185,80,0.3)"},
}

if "user_settings" not in st.session_state:
    st.session_state.user_settings = {
        "wake_time": "04:00", "commute_start": "04:45",
        "home_arrival": "16:00", "study_window_start": "17:00",
        "study_window_end": "20:30", "bed_time": "21:00",
    }
if "study_subject_id" not in st.session_state:
    st.session_state.study_subject_id = None

# STUDY MODE - Full screen, minimal
if st.session_state.study_subject_id:
    with st.sidebar:
        subj = get_subject(st.session_state.study_subject_id)
        if subj:
            st.markdown(f"### 🧠 {subj.get('name', '')}")
        if st.button("← Dashboard", use_container_width=True):
            for k in ["session_active","flashcards","current_flashcard_index","show_answer",
                       "reviewed_count","study_session_id","timer_start","timer_duration",
                       "timer_breaks_taken","timer_on_break","curiosity_gap_shown"]:
                if k in st.session_state: del st.session_state[k]
            st.session_state.study_subject_id = None
            st.rerun()
        st.markdown("---")
        if "use_interleaving" not in st.session_state:
            st.session_state.use_interleaving = True
        st.session_state.use_interleaving = st.checkbox("🧬 Interleaving", st.session_state.use_interleaving)
        st.caption("Flashcards diario → Feynman 2-3x/sem → Examen finde.")
    from sapere.ui.study import show_study_page
    show_study_page(st.session_state.study_subject_id)
else:
    # DASHBOARD MODE
    nav_icons = ["🏠", "📤", "🚌", "🌙", "⚙"]
    nav_labels = ["Dashboard", "Nueva Materia", "Traslado", "Cierre", "Guia", "Ajustes"]
    with st.sidebar:
        st.markdown('<div style="text-align:center;padding:10px 0">', unsafe_allow_html=True)
        st.markdown("## 🧠 Sapere")
        streak = get_streak_count()
        if streak > 0:
            st.markdown(f'<div style="font-size:2rem;font-weight:800;color:#58a6ff;text-align:center">{streak}</div>', unsafe_allow_html=True)
            st.markdown('<div style="text-align:center;font-size:0.8rem;color:#8b949e">dias de racha 🔥</div>', unsafe_allow_html=True)
        else:
            st.caption("Inicia tu racha hoy")
        st.markdown('</div>', unsafe_allow_html=True)
        page = st.radio("", nav_labels, label_visibility="collapsed")
        st.markdown("---")
        st.caption(f"⚡ {config.gemini_model}")

    if page == "Dashboard":
        subjects = get_all_subjects()
        all_due = get_due_flashcards(subject_id=None, limit=999)
        now = datetime.now()

        # HERO
        if 4 <= now.hour < 12: greeting = "Buenos dias"
        elif 12 <= now.hour < 19: greeting = "Buenas tardes"
        else: greeting = "Buenas noches"

        plan = calculate_plan(st.session_state.user_settings.get("upiicsa_start", ""))
        days_left = plan["days_left"]

        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #131922 0%, #1a2332 50%, #131922 100%);
        border:1px solid #202835;border-radius:20px;padding:28px 32px;margin-bottom:24px;text-align:center">
        <div style="font-size:3rem;margin-bottom:8px">🧠</div>
        <div style="font-size:1.6rem;font-weight:700;color:#ffffff;margin-bottom:6px">{greeting}, Rafa</div>
        <div style="font-size:2.5rem;font-weight:800;color:#58a6ff;margin:8px 0">{days_left}</div>
        <div style="font-size:0.9rem;color:#8b949e">dias para empezar UPIICSA</div>
        <div style="margin-top:16px;display:flex;gap:24px;justify-content:center">
        <div><span style="font-size:1.4rem;font-weight:700;color:#ffffff">{len(subjects)}</span><br><span style="font-size:0.75rem;color:#8b949e">Materias</span></div>
        <div><span style="font-size:1.4rem;font-weight:700;color:#f85149">{len(all_due)}</span><br><span style="font-size:0.75rem;color:#8b949e">Pendientes</span></div>
        <div><span style="font-size:1.4rem;font-weight:700;color:#3fb950">{get_streak_count()}</span><br><span style="font-size:0.75rem;color:#8b949e">Racha 🔥</span></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        if not subjects:
            st.info("Crea tu primera materia en 'Nueva Materia'")
        else:
            # TODAY'S PLAN
            if plan["today"]:
                st.markdown("### 🎯 Hoy")
                cols = st.columns(len(plan["today"]))
                for i, item in enumerate(plan["today"]):
                    _, due, ds, mastery, s = item
                    mode = s.get("mode", "academic")
                    icon = MODE.get(mode, "🎓")
                    c = COLORS.get(mode, COLORS["academic"])
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background:{c['bg']};border:2px solid {c['accent']};border-radius:16px;padding:20px;
                        box-shadow:0 0 20px {c['glow']};text-align:center">
                        <div style="font-size:2rem;margin-bottom:8px">{icon}</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#ffffff;margin-bottom:4px">{s['name']}</div>
                        <div style="font-size:2rem;font-weight:800;color:{c['accent']}">{due}</div>
                        <div style="font-size:0.75rem;color:#8b949e">flashcards pendientes</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"▶ Estudiar {s['name']}", key=f"tp_{s['id']}", type="primary", use_container_width=True):
                            _go_study(s["id"])

                st.caption("**Despues:** " + "  ·  ".join(f"{MODE.get(i[4].get('mode','academic'),'🎓')} {i[4]['name']}" for i in plan["tomorrow"]))

            # ALL SUBJECTS
            st.markdown("---")
            st.markdown("### 📚 Todas las materias")

            cols = st.columns(4)
            for idx, item in enumerate(plan["all_subjects"]):
                col_idx = idx % 4
                mode = item["mode"]
                icon = MODE.get(mode, "🎓")
                c = COLORS.get(mode, COLORS["academic"])

                badge = "🔴" if item["due"] > 10 else "🟡" if item["due"] > 0 else "🟢"

                with cols[col_idx]:
                    pct = max(2, item["mastery"])
                    st.markdown(f"""
                    <div style="background:#131922;border:1px solid #202835;border-radius:14px;padding:16px;text-align:center;
                    cursor:pointer" onclick="void(0)">
                    <div style="font-size:1.8rem;margin-bottom:4px">{icon}</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#ffffff;margin-bottom:2px">{item['name']}</div>
                    <div style="font-size:1.3rem;font-weight:700;color:{c['accent']};margin:4px 0">{item['due']} {badge}</div>
                    <div style="height:4px;background:#202835;border-radius:2px;margin:8px 0">
                    <div style="width:{pct}%;height:100%;background:{c['accent']};border-radius:2px"></div>
                    </div>
                    <div style="font-size:0.7rem;color:#8b949e">{item['mastery']}% dominio</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"▶", key=f"subj_{item['id']}", use_container_width=True):
                        _go_study(item["id"])

    elif page == "Nueva Materia":
        from sapere.ui.upload import show_upload_page
        show_upload_page()
    elif page == "Traslado":
        from sapere.ui.mobile import show_mobile_page
        show_mobile_page()
    elif page == "Cierre":
        st.title("🌙 Cierre Nocturno")
        st.caption("Repaso ligero antes de dormir.")
        all_due = get_due_flashcards(subject_id=None, limit=10)
        if not all_due:
            st.success("✨ Sin pendientes. Buen trabajo!")
        else:
            st.write(f"🔖 {len(all_due)} flashcards para esta noche.")
            for k in ["n_active","n_idx","n_show","n_count"]:
                if k not in st.session_state: st.session_state[k] = False if "show" in k or "active" in k else 0
            if not st.session_state.n_active:
                if st.button("🌙 Iniciar", type="primary", use_container_width=True):
                    st.session_state.n_active = st.session_state.n_idx = st.session_state.n_count = 0
                    st.session_state.n_show = False; st.rerun()
            else:
                idx = st.session_state.n_idx
                if idx >= len(all_due):
                    st.success(f"🌙 {st.session_state.n_count} repasadas. A dormir!")
                    for k in ["n_active","n_idx","n_show","n_count"]: del st.session_state[k]
                else:
                    fc = all_due[idx]
                    st.progress((idx+1)/len(all_due))
                    st.markdown(f"### {fc['question']}")
                    if not st.session_state.n_show:
                        if st.button("Revelar", type="primary", use_container_width=True): st.rerun()
                    else:
                        from sapere.study.flashcard import review_flashcard
                        from sapere.domain.enums import ReviewScore
                        review_flashcard(fc["id"], ReviewScore.HARD)
                        st.session_state.n_count += 1; st.session_state.n_idx += 1
                        st.session_state.n_show = False; st.rerun()
    elif page == "Guia":
        st.title("📖 Guia de aprendizaje")
        st.caption("Como usar cada metodo segun lo que quieres aprender.")

        st.markdown("---")
        st.markdown("## 🎓 Modo Academico")
        st.markdown("*Para: materias escolares, teoria, conceptos, examenes*")
        st.markdown("""
        **Metodo principal: Active Recall + SM-2** (80% de tu tiempo)
        - 📝 Flashcards diarias: pregunta → intentas recordar → revelas → calificas 1-4
        - El algoritmo SM-2 programa automaticamente el repaso segun tu desempeno
        - Las que fallas aparecen mas seguido. Las que dominas se espacian.

        **Metodo de verificacion: Feynman** (2-3 veces por semana)
        - 🗣 Explica el tema con tus palabras, como si tuvieras 10 anios
        - La IA detecta que entendiste, que te falto, que confundiste
        - No avances al siguiente tema hasta pasar el Feynman

        **Metodo de aplicacion: Ejercicios** (cuando domines el recall)
        - ✏️ 3 niveles: basico → medio → avanzado (tipo examen)
        - Scaffolding progresivo: de ejemplo resuelto a problema sin ayuda

        **Metodo de consolidacion: Examen simulado** (finde de semana)
        - 📊 Cronometrado, sin ayudas, mezcla todos los temas
        - Simula las condiciones reales del examen de UPIICSA
        """)

        st.markdown("---")
        st.markdown("## 🌍 Modo Idiomas")
        st.markdown("*Para: vocabulario, gramatica, frases, pronunciacion*")
        st.markdown("""
        **Metodo principal: Flashcards con contexto real**
        - 📝 Nunca estudies palabras aisladas. Siempre en frases completas.
        - La pregunta muestra la frase en el idioma original
        - La respuesta muestra la traduccion + pronunciacion
        - Califica 1-4 (SM-2 se adapta automaticamente)

        **Metodo complementario: Cloze Deletion**
        - 🔤 Oraciones con huecos: "Je ___ un cafe" → "prends"
        - Forza el active recall en contexto gramatical real
        - Mas efectivo que Duolingo porque usa repeticion espaciada real

        **Metodo de verificacion: Feynman**
        - 🗣 Explica la regla gramatical como si enseniaras a alguien
        - La IA verifica si realmente entendiste la regla

        **Tips de neurociencia para idiomas:**
        - Estudia vocabulario de NOCHE (se consolida en el sueno SWS)
        - Practica speaking/pronunciacion de DIA (consolidacion REM)
        - Intervalos mas cortos al inicio (1, 3, 7 dias) para vocabulario nuevo
        """)

        st.markdown("---")
        st.markdown("## 💻 Modo Tech Skills")
        st.markdown("*Para: comandos Linux, herramientas, sintaxis, procedimientos*")
        st.markdown("""
        **Metodo principal: Flashcards de comando/sintaxis**
        - 📝 La pregunta describe un escenario o problema
        - La respuesta es el COMANDO EXACTO (ej: "ls -la")
        - El hint incluye banderas comunes o alternativas

        **Metodo complementario: Terminal Practice**
        - 🖥 Escenarios simulados reales
        - Escribe el comando como si estuvieras en una terminal real
        - Feedback inmediato: correcto o incorrecto
        - Refuerza la memoria procedimental (muscular)

        **Metodo de verificacion: Feynman tecnico**
        - 🗣 Explica el concepto como si fuera el primer dia de alguien en sistemas
        - Obligatorio para temas complejos (subnetting, permisos, etc.)

        **Tips para tech skills:**
        - Alterna estudio teorico (flashcards) con practico (terminal)
        - Usa interleaving: mezcla comandos de diferentes categorias
        - Prioriza SABER HACER sobre saber definir
        """)

        st.markdown("---")
        st.markdown("## 🐍 Modo Programacion")
        st.markdown("*Para: aprender sintaxis, conceptos de programacion, logica*")
        st.markdown("""
        **Metodo principal: Flashcards de sintaxis + concepto**
        - 📝 Preguntas practicas: "Escribe una funcion que..." o "Que hace este codigo?"
        - Respuestas con snippets de codigo real, no definiciones
        - Los hints incluyen errores comunes de principiantes

        **Metodo complementario: Practicar codigo**
        - 🐍 Ejercicios interactivos generados por IA
        - Escribe tu solucion, recibe feedback inmediato
        - "Encuentra el error": ejercicios donde debes detectar bugs

        **Metodo de verificacion: Feynman**
        - 🗣 Explica el concepto de programacion en lenguaje simple
        - Si no puedes explicarlo simplemente, no lo entiendes

        **Ruta recomendada para aprender Python:**
        1. Flashcards de sintaxis basica (20 min/dia)
        2. Practicar codigo con ejercicios generados (30 min/dia)
        3. Feynman para conceptos tecnicos (POO, herencia, decoradores)
        4. Complementa con los archivos learning/dia1.py al dia5.py
        5. Despues del dia 5: construye un proyecto propio
        """)

        st.markdown("---")
        st.markdown("## 🧠 Principios de neurociencia integrados")
        st.markdown("""
        | Principio | Como se aplica en Sapere |
        |-----------|-------------------------|
        | **Active Recall** | Intentas recordar ANTES de ver la respuesta |
        | **Spaced Repetition (SM-2)** | Algoritmo que calcula el momento exacto de repaso |
        | **Curva del Olvido (Ebbinghaus)** | Repasas justo antes de olvidar |
        | **Feynman Technique** | Explicas con tus palabras, la IA verifica |
        | **Interleaving** | Mezclas temas viejos y nuevos (60/40) |
        | **Desirable Difficulty** | Ejercicios progresivos que te sacan de la zona de confort |
        | **Curiosity Gap** | Acertijo antes de cada tema nuevo |
        | **Pre-testing** | Intentas responder antes de que te den la respuesta |
        | **Sleep Consolidation** | Cierre nocturno antes de dormir |
        | **Pomodoro** | Bloques de 50 min con breaks forzados de 5 min |
        | **Scaffolding** | Ayuda que se va retirando gradualmente |
        """)

    elif page == "Ajustes":
        st.title("⚙ Ajustes")
        s = st.session_state.user_settings
        c1, c2 = st.columns(2)
        with c1:
            s["wake_time"] = st.text_input("Despertar", s["wake_time"])
            s["home_arrival"] = st.text_input("Llegada a casa", s["home_arrival"])
        with c2:
            s["study_window_start"] = st.text_input("Inicio estudio", s["study_window_start"])
            s["bed_time"] = st.text_input("Dormir", s["bed_time"])
        if st.button("💾 Guardar", type="primary"):
            st.session_state.user_settings = s; st.success("Guardado.")
