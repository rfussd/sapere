import time
import streamlit as st

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


def render_timer() -> bool:
    """Renderiza el timer en la sidebar. Retorna True si el tiempo termino."""
    if "timer_start" not in st.session_state:
        return False

    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⏱ Bloque de estudio")

        total_s = st.session_state.timer_duration

        if not st.session_state.timer_paused:
            elapsed = time.time() - st.session_state.timer_start
            remaining = max(0, total_s - elapsed)
        else:
            remaining = st.session_state.get("timer_remaining", total_s)

        mins = int(remaining // 60)
        secs = int(remaining % 60)

        if remaining <= 0:
            st.success("⏰ ¡Bloque completado!")
            st.balloons()
            _reset_timer()
            return True

        if remaining < 300:
            st.warning(f"⏰ {mins:02d}:{secs:02d} — ¡Ultimos 5 minutos!")
        else:
            st.info(f"⏱ {mins:02d}:{secs:02d} restantes")

        progress = 1.0 - (remaining / total_s)
        st.progress(progress)

        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.timer_paused:
                if st.button("⏸ Pausar", use_container_width=True):
                    st.session_state.timer_paused = True
                    st.session_state.timer_remaining = remaining
                    st.rerun()
            else:
                if st.button("▶ Reanudar", use_container_width=True):
                    st.session_state.timer_paused = False
                    st.session_state.timer_start = time.time() - (total_s - remaining)
                    st.rerun()
        with col2:
            if st.button("⏹ Terminar", use_container_width=True):
                _reset_timer()
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


def adjust_next_block_duration(current_energy: EnergyLevel) -> int:
    if current_energy == EnergyLevel.LOW:
        return 25
    elif current_energy == EnergyLevel.MEDIUM:
        return 40
    else:
        return 50


def _reset_timer():
    for key in ["timer_start", "timer_duration", "timer_paused", "timer_remaining", "timer_energy"]:
        if key in st.session_state:
            del st.session_state[key]
