from datetime import datetime, timedelta

from sapere.infrastructure import database

DEFAULT_UPIICSA_START = datetime(2026, 8, 11)


def get_days_until_upiicsa(start_date_str: str = "") -> int:
    try:
        if start_date_str:
            target = datetime.strptime(start_date_str, "%Y-%m-%d")
        else:
            target = DEFAULT_UPIICSA_START
    except ValueError:
        target = DEFAULT_UPIICSA_START
    return max(0, (target - datetime.now()).days)


def get_last_study_date(subject_id: int) -> datetime | None:
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT MAX(started_at) FROM study_sessions WHERE subject_id = ? AND is_complete = 1",
            (subject_id,),
        ).fetchone()
        if row and row[0]:
            return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        return None
    finally:
        conn.close()


def get_days_since_study(subject_id: int) -> int:
    last = get_last_study_date(subject_id)
    if not last:
        return 7  # Cap at 7 days for new subjects
    days = (datetime.now() - last).days
    return min(days, 7)  # Cap for planning purposes


def calculate_plan(upiicsa_start: str = "") -> dict:
    subjects = database.get_all_subjects()

    scored = []
    for s in subjects:
        progress = database.get_subject_progress(s["id"])
        due = progress.get("due_flashcards", 0) or 0
        total = progress.get("total_flashcards", 0) or 0
        mastery = progress.get("avg_mastery", 0) or 0
        days_since = get_days_since_study(s["id"])
        days_since = max(0, days_since or 0)

        if total == 0:
            continue

        urgency = (due * 2) + (pow(days_since, 1.5) * 3) - (mastery * 30)
        urgency = max(0.0, urgency)

        scored.append((urgency, due, days_since, mastery, s))

    scored.sort(key=lambda x: -x[0])

    days_left = get_days_until_upiicsa(upiicsa_start)
    is_school_mode = days_left <= 0

    plan = {
        "days_left": days_left,
        "is_school_mode": is_school_mode,
        "today": [],
        "tomorrow": [],
        "next": [],
        "all_subjects": [
            {
                "name": s[4]["name"],
                "mode": s[4].get("mode", "academic"),
                "due": s[1],
                "days_since": s[2],
                "mastery": int(s[3] * 100) if s[3] else 0,
                "id": s[4]["id"],
            }
            for s in scored
        ],
    }

    if is_school_mode:
        plan["today"] = scored[:1]
        plan["tomorrow"] = scored[1:3]
        plan["next"] = scored[3:5]
        plan["tip"] = "Modo escuela: 1 materia por dia en casa + flashcards en el traslado"
    else:
        plan["today"] = scored[:2]
        plan["tomorrow"] = scored[2:4]
        plan["next"] = scored[4:6]
        plan["tip"] = "Modo vacaciones: 2 materias por dia. Aprovecha el tiempo antes de UPIICSA."

    return plan
