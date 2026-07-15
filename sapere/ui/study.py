import streamlit as st

from sapere.infrastructure import database
from sapere.domain.enums import ReviewScore
from sapere.study.flashcard import get_due_flashcards, get_interleaved_flashcards, review_flashcard
from sapere.study.feynman import evaluate_explanation
from sapere.study.exercises import generate_exercises, generate_curiosity_gap
from sapere.study.timer import start_timer, render_timer, get_current_energy, adjust_next_block_duration
from sapere.llm.gemini import GeminiFlash
from sapere.llm.base import LLMProvider


MODE_ICONS = {"academic": "🎓", "language": "🌍", "tech": "💻"}
MODE_LABELS = {"academic": "Academico", "language": "Idiomas", "tech": "Tech"}


def show_study_page(subject_id: int):
    subject = database.get_subject(subject_id)
    if not subject:
        st.error("Materia no encontrada.")
        return

    mode = subject.get("mode", "academic")

    st.header(f"{MODE_ICONS.get(mode, '🎓')} {subject['name']}")
    st.caption(f"Modo {MODE_LABELS.get(mode, 'Academico')}")

    progress = database.get_subject_progress(subject_id)
    due = progress.get("due_flashcards", 0) or 0
    total = progress.get("total_flashcards", 0) or 0
    mastery = int(progress.get("avg_mastery", 0) * 100) if progress.get("avg_mastery") else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dominio", f"{mastery}%")
    col2.metric("Pendientes", due)
    col3.metric("Total", total)
    col4.metric("Energia", {"LOW": "😫", "MEDIUM": "😐", "HIGH": "💪"}.get(
        get_current_energy().name if hasattr(get_current_energy(), 'name') else "MEDIUM", "😐"
    ))

    st.markdown("---")

    tab_names = ["📝 Flashcards", "✏️ Ejercicios", "🗣 Feynman", "📊 Examen"]
    if mode == "language":
        tab_names = ["📝 Flashcards", "🔤 Cloze", "🗣 Feynman", "📊 Examen"]
    elif mode == "tech":
        tab_names = ["📝 Flashcards", "🖥 Terminal", "🗣 Feynman", "📊 Examen"]

    tabs = st.tabs(tab_names)

    with tabs[0]:
        _show_flashcard_tab(subject_id, subject, due, mode)

    with tabs[1]:
        if mode == "language":
            _show_cloze_tab(subject_id)
        elif mode == "tech":
            _show_terminal_tab(subject_id)
        else:
            _show_exercises_tab(subject_id, subject, mode)

    with tabs[2]:
        _show_feynman_tab(subject_id, mode)

    with tabs[3]:
        _show_exam_tab(subject_id, subject, mode)

    render_timer()


def _init_flashcard_session():
    defaults = {
        "study_session_id": None,
        "current_flashcard_index": 0,
        "flashcards": [],
        "show_answer": False,
        "reviewed_count": 0,
        "session_active": False,
        "confidence_score": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _show_flashcard_tab(subject_id: int, subject: dict, due: int, mode: str):
    _init_flashcard_session()

    show_timer_controls()

    if due == 0 and not st.session_state.session_active:
        st.success("Sin flashcards pendientes. ¡Revisa ejercicios o el modo examen!")
        return

    if not st.session_state.session_active:
        use_interleaving = st.checkbox("🧬 Interleaving (mezclar temas viejos)", value=True, help="Combina 60% tema actual + 40% repaso de otros temas")
        label = "▶ Iniciar sesion de estudio"
        if st.button(label, type="primary", use_container_width=True):
            if use_interleaving:
                st.session_state.flashcards = get_interleaved_flashcards(subject_id=subject_id, limit=20)
            else:
                st.session_state.flashcards = get_due_flashcards(subject_id=subject_id, limit=20)
            st.session_state.current_flashcard_index = 0
            st.session_state.show_answer = False
            st.session_state.reviewed_count = 0
            st.session_state.session_active = True
            st.session_state.confidence_score = None
            st.session_state.study_session_id = database.start_study_session(subject_id=subject_id, energy_start=3)
            start_timer(50)
            st.rerun()
        return

    if st.session_state.current_flashcard_index == 0 and st.session_state.reviewed_count == 0:
        st.markdown("---")
        if "curiosity_gap_shown" not in st.session_state:
            st.session_state.curiosity_gap_shown = False
        if not st.session_state.curiosity_gap_shown:
            topics = database.get_topics_for_subject(subject_id)[:3]
            if topics:
                with st.spinner("🧠 Preparando tu cerebro para aprender..."):
                    try:
                        llm_gap = LLMProvider(primary=GeminiFlash())
                        gap = generate_curiosity_gap(
                            llm_gap,
                            topics[0]["name"],
                            topics[0].get("description", ""),
                        )
                        st.markdown("### 🧠 Curiosity Gap")
                        st.info(gap)
                        st.caption("No necesitas responder. Solo deja que la pregunta active tu curiosidad. Tu cerebro ahora esta listo para absorber.")
                    except Exception:
                        st.info(f"🧠 **Antes de empezar:** hoy veras temas como: {', '.join(t['name'] for t in topics)}. Piensa: ¿que sabes ya de esto?")
                st.session_state.curiosity_gap_shown = True
                if st.button("✅ Empezar flashcards", use_container_width=True):
                    st.rerun()
            return

    flashcards = st.session_state.flashcards
    idx = st.session_state.current_flashcard_index

    if idx >= len(flashcards):
        _end_session()
        return

    fc = flashcards[idx]
    st.progress((idx + 1) / len(flashcards))
    st.caption(f"Flashcard {idx + 1} de {len(flashcards)}")

    st.markdown("---")

    if mode == "language":
        st.markdown(f"### 🌍 {fc['question']}")
        if fc.get("hint"):
            st.caption(f"🔊 {fc['hint']}")
    elif mode == "tech":
        st.markdown(f"### 💻 {fc['question']}")
        if fc.get("hint"):
            st.caption(f"💡 {fc['hint']}")
    else:
        st.markdown(f"### ❓ {fc['question']}")
        if fc.get("hint"):
            st.caption(f"💡 {fc['hint']}")

    if not st.session_state.show_answer:
        if st.button("📝 Revelar respuesta", type="primary", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    else:
        if mode == "tech":
            st.code(fc["answer"])
        else:
            st.markdown(f"#### ✅ {fc['answer']}")

        st.markdown("---")
        st.markdown("**¿Que tan facil fue recordar?**")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔴 Ni idea", use_container_width=True):
                _process_review(fc["id"], ReviewScore.AGAIN, None)
        with col2:
            if st.button("🟠 Dificil", use_container_width=True):
                _process_review(fc["id"], ReviewScore.HARD, None)
        with col3:
            if st.button("🟢 Bien", use_container_width=True):
                _process_review(fc["id"], ReviewScore.GOOD, None)
        with col4:
            if st.button("🟣 Facil", use_container_width=True):
                _process_review(fc["id"], ReviewScore.EASY, None)


def show_timer_controls():
    with st.expander("⏱ Control de sesion", expanded=False):
        cols = st.columns(3)
        with cols[0]:
            if st.button("⏸ Pausa rapida", use_container_width=True):
                st.info("⏸ Tomate 3 respiraciones profundas... luego continua.")


def _process_review(flashcard_id: int, score: ReviewScore, confidence: int | None):
    review_flashcard(
        flashcard_id=flashcard_id,
        score=score,
        session_id=st.session_state.study_session_id,
    )
    st.session_state.reviewed_count += 1
    st.session_state.show_answer = False
    st.session_state.current_flashcard_index += 1
    st.rerun()


def _end_session():
    st.success(f"¡Sesion completada! {st.session_state.reviewed_count} flashcards.")
    if st.session_state.study_session_id:
        energy = get_current_energy()
        database.end_study_session(st.session_state.study_session_id, energy_end=int(energy))
        database.record_daily_streak(minutes=st.session_state.reviewed_count * 2, sessions=1, topics=st.session_state.reviewed_count)
    for key in ["session_active", "flashcards", "current_flashcard_index", "show_answer", "reviewed_count", "study_session_id"]:
        if key in st.session_state:
            del st.session_state[key]
    st.balloons()


def _show_exercises_tab(subject_id: int, subject: dict, mode: str):
    st.subheader("✏️ Ejercicios progresivos")
    st.caption("Fading worked examples: de ejemplo resuelto a problema sin ayuda.")

    topics = database.get_topics_for_subject(subject_id)
    if not topics:
        st.info("No hay temas para esta materia.")
        return

    topic_names = {t["name"]: t for t in topics}
    selected = st.selectbox("Tema", list(topic_names.keys()), key="ex_topic")

    level_map = {"Basico": 1, "Medio": 2, "Avanzado": 3}
    level = st.radio("Nivel", list(level_map.keys()), horizontal=True, key="ex_level")

    scaffold_map = {"Todo resuelto": 1, "Faltan 2 pasos": 2, "Solo 1er paso": 3, "Solo respuesta": 4, "Sin ayuda": 5}
    scaffold = st.select_slider("Ayuda", list(scaffold_map.keys()), value="Solo 1er paso", key="ex_scaffold")

    if "exercises" not in st.session_state:
        st.session_state.exercises = []
    if "ex_index" not in st.session_state:
        st.session_state.ex_index = 0
    if "ex_show_answer" not in st.session_state:
        st.session_state.ex_show_answer = False
    if "ex_loading" not in st.session_state:
        st.session_state.ex_loading = False

    if not st.session_state.exercises:
        if st.button("🎲 Generar ejercicios", type="primary", use_container_width=True):
            st.session_state.ex_loading = True
            with st.spinner("Gemini esta creando ejercicios..."):
                try:
                    llm = LLMProvider(primary=GeminiFlash())
                    exs = generate_exercises(
                        llm, selected, level=ExerciseLevel(level_map[level]),
                        scaffolding=scaffold_map[scaffold], count=3,
                        context=topics[0].get("description", "") if topics else "",
                    )
                    st.session_state.exercises = exs
                    st.session_state.ex_index = 0
                    st.session_state.ex_show_answer = False
                except Exception as e:
                    st.error(f"Error: {e}")
            st.session_state.ex_loading = False
            st.rerun()
        return

    exs = st.session_state.exercises
    idx = st.session_state.ex_index

    if idx >= len(exs):
        st.success("¡Ejercicios completados!")
        if st.button("🎲 Nuevos ejercicios", use_container_width=True):
            st.session_state.exercises = []
            st.session_state.ex_index = 0
            st.rerun()
        return

    ex = exs[idx]
    st.markdown("---")
    st.markdown(f"**Ejercicio {idx + 1} de {len(exs)}**")
    st.info(ex.get("question", ""))

    if not st.session_state.ex_show_answer:
        user_answer = st.text_area("Tu respuesta:", key=f"ex_answer_{idx}", height=150)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Ver solucion", use_container_width=True):
                st.session_state.ex_show_answer = True
                st.rerun()
        with col2:
            if user_answer and st.button("🧠 Comparar", use_container_width=True):
                st.session_state.ex_show_answer = True
                st.rerun()
    else:
        if ex.get("answer"):
            st.markdown("### Solucion")
            st.code(ex["answer"])
        if ex.get("explanation"):
            st.markdown("#### 📝 Paso a paso")
            st.markdown(ex["explanation"])

        st.markdown("---")
        st.markdown("**¿Que tan seguro estabas de tu respuesta?**")
        conf_cols = st.columns(5)
        for i, label in enumerate(["😰 Adivine", "🤔 Dude", "🙂 Algo seguro", "😎 Seguro", "💯 Dominado"], 1):
            with conf_cols[i - 1]:
                if st.button(label, key=f"conf_{idx}_{i}", use_container_width=True):
                    st.session_state.ex_index += 1
                    st.session_state.ex_show_answer = False
                    st.rerun()


def _show_feynman_tab(subject_id: int, mode: str):
    st.subheader("🗣 Metodo Feynman — Explica para aprender")
    tips = {"academic": "Explica este concepto como si yo tuviera 10 anios.", "language": "Explica la regla gramatical como si fuera mi primera clase.", "tech": "Explica este concepto como si fuera mi primer dia en sistemas."}
    st.caption(tips.get(mode, tips["academic"]))

    topics = database.get_topics_for_subject(subject_id)
    if not topics:
        st.info("Sin temas disponibles.")
        return

    selected = st.selectbox("Tema", [t["name"] for t in topics], key="feyn_topic")
    topic = next(t for t in topics if t["name"] == selected)

    for key in ["feynman_result", "feynman_loading"]:
        if key not in st.session_state:
            st.session_state[key] = None if key == "feynman_result" else False

    user_explanation = st.text_area("Tu explicacion:", height=200, key=f"feynman_{topic['id']}", placeholder="Escribe aqui...")

    if st.button("🧠 Evaluar", type="primary", use_container_width=True, disabled=st.session_state.feynman_loading):
        if not user_explanation.strip():
            st.error("Escribe tu explicacion primero.")
            return
        st.session_state.feynman_loading = True
        with st.spinner("Evaluando..."):
            try:
                llm = LLMProvider(primary=GeminiFlash())
                result = evaluate_explanation(llm, topic["id"], topic["name"], user_explanation)
                st.session_state.feynman_result = result
            except Exception as e:
                st.error(f"Error: {e}")
        st.session_state.feynman_loading = False
        st.rerun()

    result = st.session_state.feynman_result
    if result:
        st.markdown("---")
        if result["passed"]:
            st.success("✅ ¡Aprobaste el Feynman!")
            st.balloons()
        else:
            st.error("❌ Aun hay vacios.")
        st.metric("Claridad", f"{result.get('clarity_score', 0)}/10")
        for label, key in [("✅ Entendiste", "understood"), ("❌ Falto", "missing"), ("⚠️ Confundiste", "confused")]:
            items = result.get(key, [])
            if items:
                st.markdown(f"**{label}:**")
                for item in items:
                    st.markdown(f"- {item if isinstance(item, str) else item.get('correction', str(item))}")
        if not result["passed"]:
            if st.button("🔄 Intentar de nuevo", use_container_width=True):
                st.session_state.feynman_result = None
                st.rerun()


def _show_exam_tab(subject_id: int, subject: dict, mode: str):
    st.subheader("📊 Simulacro de examen")
    st.caption("Cronometrado, sin ayudas, preguntas tipo examen real.")

    if "exam_active" not in st.session_state:
        st.session_state.exam_active = False
    if "exam_questions" not in st.session_state:
        st.session_state.exam_questions = []
    if "exam_index" not in st.session_state:
        st.session_state.exam_index = 0
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}
    if "exam_results" not in st.session_state:
        st.session_state.exam_results = None
    if "exam_time_left" not in st.session_state:
        st.session_state.exam_time_left = 0

    if not st.session_state.exam_active:
        st.info("El modo examen mezcla TODOS los temas de la materia, cronometrado y sin pistas.")
        num_q = st.slider("Numero de preguntas", 5, 20, 10)
        if st.button("🚀 Iniciar simulacro", type="primary", use_container_width=True):
            st.session_state.exam_active = True
            st.session_state.exam_index = 0
            st.session_state.exam_answers = {}
            st.session_state.exam_results = None
            topic_list = database.get_topics_for_subject(subject_id)
            topic_names = [t["name"] for t in topic_list[:5]]
            with st.spinner("Generando preguntas de examen..."):
                try:
                    llm = LLMProvider(primary=GeminiFlash())
                    prompt = f"""Eres un profesor universitario del IPN. Genera un examen de {subject['name']} 
con {num_q} preguntas tipo examen real. Cubre estos temas: {', '.join(topic_names)}.

Las preguntas deben ser de nivel ANALISIS y EVALUACION (Bloom 4-5). Mezcla:
- Preguntas de opcion multiple con trampas sutiles
- Problemas que requieran aplicar conceptos combinados
- Preguntas de "explica por que"
- Alguna pregunta sorpresa con contexto inesperado

Devuelve JSON:
{{{{"questions": [{{{{"question": "...", "type": "multiple_choice|open", "options": ["A", "B", "C", "D"], "answer": "B", "explanation": "..."}}}}]}}}}

Responde SOLO con JSON."""
                    response = llm.call_with_json(prompt)
                    from sapere.utils.json_parser import robust_json_parse
                    data = robust_json_parse(response)
                    st.session_state.exam_questions = data.get("questions", [])[:num_q]
                    import time as _t
                    st.session_state.exam_start_time = _t.time()
                except Exception as e:
                    st.error(f"Error generando examen: {e}")
                    st.session_state.exam_active = False
            st.rerun()
        return

    questions = st.session_state.exam_questions
    idx = st.session_state.exam_index
    elapsed = time.time() - st.session_state.get("exam_start_time", time.time())

    if idx >= len(questions):
        _show_exam_results(len(questions))
        return

    q = questions[idx]
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)

    st.markdown(f"**Pregunta {idx + 1} de {len(questions)}** | ⏱ {mins}:{secs:02d}")
    st.progress((idx + 1) / len(questions))
    st.markdown("---")
    st.markdown(f"### {q.get('question', '')}")

    if q.get("type") == "multiple_choice" and q.get("options"):
        for opt in q["options"]:
            st.markdown(f"**{opt}**")
        user_ans = st.radio("Selecciona:", q["options"], key=f"exam_{idx}", index=None)
    else:
        user_ans = st.text_area("Tu respuesta:", key=f"exam_{idx}", height=150)

    if st.button("✅ Responder y continuar", use_container_width=True, type="primary"):
        if user_ans:
            st.session_state.exam_answers[idx] = user_ans
            st.session_state.exam_index += 1
            st.rerun()


def _show_exam_results(total: int):
    st.success("¡Simulacro completado!")
    st.markdown("---")
    correct = 0
    for i, q in enumerate(st.session_state.exam_questions):
        user = st.session_state.exam_answers.get(i, "Sin respuesta")
        correct_ans = q.get("answer", "")
        is_correct = str(user).strip().upper() == str(correct_ans).strip().upper()
        if is_correct:
            correct += 1

    score = int((correct / total) * 100) if total > 0 else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Correctas", f"{correct}/{total}")
    col2.metric("Calificacion", f"{score}%")
    col3.metric("Tiempo", f"{int(time.time() - st.session_state.exam_start_time) // 60} min")

    for key in ["exam_active", "exam_questions", "exam_index", "exam_answers", "exam_start_time"]:
        if key in st.session_state:
            del st.session_state[key]

    if st.button("🔄 Nuevo simulacro", use_container_width=True):
        st.rerun()


def _show_cloze_tab(subject_id: int):
    st.subheader("🔤 Cloze Deletion")
    st.caption("Completa la palabra faltante en la oracion.")

    for key in ["cloze_data", "cloze_answer_shown", "cloze_loading"]:
        if key not in st.session_state:
            st.session_state[key] = None if key == "cloze_data" else False

    topics = database.get_topics_for_subject(subject_id)
    if not topics:
        st.info("Sin temas.")
        return

    selected = st.selectbox("Tema", [t["name"] for t in topics], key="cloze_topic")

    if st.button("🎲 Generar oracion", type="primary", use_container_width=True):
        st.session_state.cloze_loading = True
        st.session_state.cloze_answer_shown = False
        with st.spinner("Generando..."):
            try:
                llm = LLMProvider(primary=GeminiFlash())
                response = llm.call_with_json(f"""Genera una oracion con UN hueco (___) en el idioma del tema "{selected}".
Devuelve: {{{{"sentence": "La oracion con ___", "answer": "palabra", "hint": "pista en espanol"}}}}""")
                from sapere.utils.json_parser import robust_json_parse
                st.session_state.cloze_data = robust_json_parse(response)
            except Exception as e:
                st.error(f"Error: {e}")
        st.session_state.cloze_loading = False
        st.rerun()

    if st.session_state.cloze_data:
        d = st.session_state.cloze_data
        st.markdown("---")
        st.markdown(f"### 🌍 {d.get('sentence', '')}")
        if d.get("hint") and not st.session_state.cloze_answer_shown:
            st.caption(f"💡 {d['hint']}")
        if not st.session_state.cloze_answer_shown:
            if st.button("✅ Revelar", use_container_width=True):
                st.session_state.cloze_answer_shown = True
                st.rerun()
        else:
            st.markdown(f"#### ✅ {d.get('answer', '')}")
            if st.button("🎲 Nueva", use_container_width=True):
                st.session_state.cloze_data = None
                st.session_state.cloze_answer_shown = False
                st.rerun()


def _show_terminal_tab(subject_id: int):
    st.subheader("🖥 Terminal Practice")
    st.caption("Escribe el comando correcto para el escenario.")

    for key in ["terminal_data", "terminal_answer_shown", "terminal_loading"]:
        if key not in st.session_state:
            st.session_state[key] = None if key == "terminal_data" else False

    topics = database.get_topics_for_subject(subject_id)
    if not topics:
        st.info("Sin temas.")
        return

    selected = st.selectbox("Tema", [t["name"] for t in topics], key="term_topic")

    if st.button("🎲 Generar desafio", type="primary", use_container_width=True):
        st.session_state.terminal_loading = True
        st.session_state.terminal_answer_shown = False
        with st.spinner("Generando..."):
            try:
                llm = LLMProvider(primary=GeminiFlash())
                response = llm.call_with_json(f"""Escenario practico para el tema "{selected}". 
Devuelve: {{{{"scenario": "...", "command": "...", "explanation": "..."}}}}""")
                from sapere.utils.json_parser import robust_json_parse
                st.session_state.terminal_data = robust_json_parse(response)
            except Exception as e:
                st.error(f"Error: {e}")
        st.session_state.terminal_loading = False
        st.rerun()

    if st.session_state.terminal_data:
        d = st.session_state.terminal_data
        st.markdown("---")
        st.info(f"**Escenario:** {d.get('scenario', '')}")
        if not st.session_state.terminal_answer_shown:
            user_cmd = st.text_input("$", key="term_cmd", placeholder="Escribe el comando...")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Revelar", use_container_width=True):
                    st.session_state.terminal_answer_shown = True
                    st.rerun()
            with col2:
                if user_cmd and st.button("🧠 Verificar", use_container_width=True):
                    if user_cmd.strip() == d.get("command", "").strip():
                        st.success("✅ Correcto!")
                        st.balloons()
                    else:
                        st.error("❌ Incorrecto")
                        st.code(d.get("command", ""))
        else:
            st.code(d.get("command", ""))
            st.caption(d.get("explanation", ""))
            if st.button("🎲 Nuevo", use_container_width=True):
                st.session_state.terminal_data = None
                st.session_state.terminal_answer_shown = False
                st.rerun()


import time
from sapere.domain.enums import ExerciseLevel
