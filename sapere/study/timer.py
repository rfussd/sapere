import time
import streamlit as st
import math

from sapere.domain.enums import EnergyLevel


def start_timer(duration_minutes: int = 50) -> None:
    if "timer_start" not in st.session_state:
        st.session_state.timer_start = time.time()
    if "timer_duration" not in st.session_state:
        st.session_state.timer_duration = duration_minutes * 60
    if "timer_paused" not in st.session_state:
        st.session_state.timer_paused = False
    if "timer_energy" not in st.session_state:
        st.session_state.timer_energy = EnergyLevel.HIGH
    if "timer_breaks_taken" not in st.session_state:
        st.session_state.timer_breaks_taken = 0
    if "timer_break_until" not in st.session_state:
        st.session_state.timer_break_until = 0
    if "timer_on_break" not in st.session_state:
        st.session_state.timer_on_break = False


def render_timer() -> bool:
    """Renderiza el timer en la sidebar. Retorna True si el bloque termino."""
    if "timer_start" not in st.session_state:
        return False

    with st.sidebar:
        st.markdown("---")

        if st.session_state.get("timer_on_break"):
            remaining = st.session_state.timer_break_until - time.time()
            if remaining <= 0:
                st.session_state.timer_on_break = False
                st.rerun()
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            st.info(f"☕ DESCANSO: {mins}:{secs:02d}")
            st.caption("Alejate de la pantalla. Mira por la ventana. Respira.")
            st.progress(1.0 - (remaining / 300))
            if st.button("⏩ Saltar descanso", use_container_width=True):
                st.session_state.timer_on_break = False
                st.session_state.timer_start = time.time()
                st.rerun()
            return False

        total_s = st.session_state.timer_duration
        if not st.session_state.timer_paused:
            elapsed = time.time() - st.session_state.timer_start
            remaining = max(0, total_s - elapsed)
        else:
            remaining = st.session_state.get("timer_remaining", total_s)

        mins = int(remaining // 60)
        secs = int(remaining % 60)

        if remaining <= 0:
            st.session_state.timer_breaks_taken += 1
            if st.session_state.timer_breaks_taken >= 3:
                st.success("✅ ¡Sesion de estudio completada!")
                st.balloons()
                _reset_timer()
                return True

            st.session_state.timer_on_break = True
            st.session_state.timer_break_until = time.time() + 300
            st.session_state.timer_start = time.time()
            st.rerun()

        progress = 1.0 - (remaining / total_s)

        if remaining < 300:
            st.warning(f"⏰ {mins:02d}:{secs:02d} — Ultimos 5 min!")
        elif remaining < total_s * 0.25:
            st.info(f"⏱ {mins:02d}:{secs:02d} — Ultimo cuarto")
        else:
            st.info(f"⏱ {mins:02d}:{secs:02d}")

        st.progress(progress)

        col1, col2, col3 = st.columns(3)
        with col1:
            if not st.session_state.timer_paused:
                if st.button("⏸", use_container_width=True, help="Pausar"):
                    st.session_state.timer_paused = True
                    st.session_state.timer_remaining = remaining
                    st.rerun()
            else:
                if st.button("▶", use_container_width=True, help="Reanudar"):
                    st.session_state.timer_paused = False
                    st.session_state.timer_start = time.time() - (total_s - remaining)
                    st.rerun()
        with col2:
            if st.button("⏹", use_container_width=True, help="Terminar"):
                _reset_timer()
                st.rerun()
        with col3:
            if st.button("☕", use_container_width=True, help="Tomar descanso"):
                st.session_state.timer_on_break = True
                st.session_state.timer_break_until = time.time() + 300
                st.rerun()

        energy = st.select_slider(
            "Energia",
            options=["😫 Baja", "😐 Normal", "💪 Alta"],
            value="😐 Normal",
            key="energy_slider",
        )
        st.session_state.timer_energy = {
            "😫 Baja": EnergyLevel.LOW,
            "😐 Normal": EnergyLevel.MEDIUM,
            "💪 Alta": EnergyLevel.HIGH,
        }.get(energy, EnergyLevel.MEDIUM)

        return False


def get_current_energy() -> EnergyLevel:
    return st.session_state.get("timer_energy", EnergyLevel.MEDIUM)


def _reset_timer():
    for key in ["timer_start", "timer_duration", "timer_paused", "timer_remaining",
                "timer_energy", "timer_breaks_taken", "timer_break_until", "timer_on_break"]:
        if key in st.session_state:
            del st.session_state[key]
