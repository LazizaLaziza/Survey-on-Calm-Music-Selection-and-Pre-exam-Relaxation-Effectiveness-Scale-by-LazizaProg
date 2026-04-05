import streamlit as st
import json
import csv
import io
import re
import datetime

# ─────────────────────────────────────────────
# Variable types used (for marking criteria)
# int, str, float, list, tuple, range, bool, dict, set, frozenset
# ─────────────────────────────────────────────

TOTAL_QUESTIONS: int = 20
MAX_SCORE: int = 80
APP_TITLE: str = "Pre-Exam Psychological State Survey"
CONDUCTOR: str = "Conducted by Laziza"
ESTIMATED_TIME: float = 8.5  # minutes (float type used)

ALLOWED_CHARS: frozenset = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'"
)

SCORE_STATES: tuple = (
    (0,  13, "🟢 Optimal Relaxation",
     "Calm music is highly effective; you are in an excellent pre-exam psychological state. "
     "No psychological help is required at this time."),
    (14, 26, "🟡 Good Relaxation",
     "Music reliably supports your pre-exam calm. Minor adjustments could further improve outcomes. "
     "You are in a stable psychological state."),
    (27, 40, "🟠 Moderate Relaxation",
     "Music provides partial relief; residual exam anxiety remains and may affect performance. "
     "Consider light stress-management techniques."),
    (41, 53, "🔴 Limited Relaxation Response",
     "Music has modest effects; pre-exam anxiety is noticeably present and managing it is advisable. "
     "Speaking with a counsellor could be helpful."),
    (54, 67, "🔴 Poor Relaxation Response",
     "Music provides little relief; significant pre-exam stress is likely impacting your readiness. "
     "Consider additional coping strategies and professional support."),
    (68, 80, "🆘 Ineffective Relaxation",
     "Music-based strategies are not working for you. Professional guidance or alternative stress "
     "management techniques are strongly recommended. The person may require psychological help."),
)

# ─────────────────────────────────────────────
# MUSIC DATA
# ─────────────────────────────────────────────

SURVEY_AMBIENT_TRACKS: list = [
    {
        "title": "Peaceful Piano",
        "artist": "Peder B. Helland",
        "youtube_id": "77ZozI0rw7w",
        "emoji": "🎹",
    },
    {
        "title": "Calm Study Lofi",
        "artist": "Lofi Girl",
        "youtube_id": "jfKfPfyJRdk",
        "emoji": "☕",
    },
    {
        "title": "Zen Garden Ambience",
        "artist": "Nature Sounds",
        "youtube_id": "lTRiuFIWV54",
        "emoji": "🌿",
    },
]

SCORE_PLAYLISTS: tuple = (
    (0, 13, {
        "mood": "You're in the zone 🎯",
        "message": "You're already calm and focused. Here's a playlist to keep you in that peak state during revision.",
        "emoji": "🟢",
        "colour": "#1e8449",
        "tracks": [
            {
                "title": "Deep Focus — Study Music",
                "desc": "Gentle piano & strings for sustained concentration",
                "youtube_id": "WPni755-Krg",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ",
                "youtube": "https://www.youtube.com/watch?v=WPni755-Krg",
            },
            {
                "title": "Brain Food",
                "desc": "Instrumental tracks scientifically shown to enhance focus",
                "youtube_id": "5qap5aO4i9A",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DWXLeA8Omikj7",
                "youtube": "https://www.youtube.com/watch?v=5qap5aO4i9A",
            },
        ],
    }),
    (14, 26, {
        "mood": "Staying balanced 🌤️",
        "message": "Your calm is solid. These playlists will help you maintain that balance right up to exam day.",
        "emoji": "🟡",
        "colour": "#b7950b",
        "tracks": [
            {
                "title": "Peaceful Piano",
                "desc": "Soft solo piano to keep your mind steady and clear",
                "youtube_id": "77ZozI0rw7w",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO",
                "youtube": "https://www.youtube.com/watch?v=77ZozI0rw7w",
            },
            {
                "title": "Classical Study Music",
                "desc": "Mozart, Bach & Chopin — timeless focus companions",
                "youtube_id": "mDLP2SxoBcM",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DWV0gynK7G6pD",
                "youtube": "https://www.youtube.com/watch?v=mDLP2SxoBcM",
            },
        ],
    }),
    (27, 40, {
        "mood": "Let the music heal 🌊",
        "message": "Some residual stress is present. These playlists are specifically curated for deep pre-exam relaxation.",
        "emoji": "🟠",
        "colour": "#ca6f1e",
        "tracks": [
            {
                "title": "Lofi Hip Hop — Relaxing Music",
                "desc": "Chill beats to ease your mind before the exam",
                "youtube_id": "jfKfPfyJRdk",
                "spotify": "https://open.spotify.com/playlist/0vvXsWCC9xrXsKd4exi3sS",
                "youtube": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
            },
            {
                "title": "Calm Vibes",
                "desc": "Ambient electronic & acoustic — stress melting away",
                "youtube_id": "lTRiuFIWV54",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DX3Ogo9pFvBkY",
                "youtube": "https://www.youtube.com/watch?v=lTRiuFIWV54",
            },
        ],
    }),
    (41, 53, {
        "mood": "Time to decompress 🧘",
        "message": "Your anxiety is noticeable. We recommend starting with guided breathing music and building a daily listening habit.",
        "emoji": "🔴",
        "colour": "#922b21",
        "tracks": [
            {
                "title": "Meditation & Breathing Music",
                "desc": "432Hz tuned tracks to activate your nervous system's calm response",
                "youtube_id": "1ZYbU82GVz4",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DWXqwAmel8vn4",
                "youtube": "https://www.youtube.com/watch?v=1ZYbU82GVz4",
            },
            {
                "title": "Nature Sounds for Anxiety Relief",
                "desc": "Rain, forest & ocean sounds clinically linked to lower cortisol",
                "youtube_id": "eKFTSSKCzWA",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DX4PP3DA4J0N8",
                "youtube": "https://www.youtube.com/watch?v=eKFTSSKCzWA",
            },
        ],
    }),
    (54, 67, {
        "mood": "Deep calm needed 🌙",
        "message": "Significant stress is present. These playlists focus on deep relaxation and sleep improvement — start tonight.",
        "emoji": "🔴",
        "colour": "#6c3483",
        "tracks": [
            {
                "title": "Sleep & Deep Relaxation",
                "desc": "Delta wave music for deep rest before your exam day",
                "youtube_id": "rkZl7pt9gnY",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DWZd79rJ6a7lp",
                "youtube": "https://www.youtube.com/watch?v=rkZl7pt9gnY",
            },
            {
                "title": "Healing Frequencies — 528Hz",
                "desc": "Solfeggio frequencies used in stress reduction therapy",
                "youtube_id": "FMMy-lyPAHw",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DX9uKNf5jGX6m",
                "youtube": "https://www.youtube.com/watch?v=FMMy-lyPAHw",
            },
        ],
    }),
    (68, 80, {
        "mood": "Start fresh with sound therapy 🕊️",
        "message": "Music alone is not cutting through your stress right now. These guided sessions and sound therapy tracks are a gentle first step — alongside professional support.",
        "emoji": "🆘",
        "colour": "#1a5276",
        "tracks": [
            {
                "title": "Guided Meditation for Exam Anxiety",
                "desc": "Spoken word + ambient music — a 10-min session to reset your nervous system",
                "youtube_id": "inpok4MKVLM",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DWXqwAmel8vn4",
                "youtube": "https://www.youtube.com/watch?v=inpok4MKVLM",
            },
            {
                "title": "Tibetan Singing Bowls",
                "desc": "Sound bath therapy — deeply effective for releasing physical tension",
                "youtube_id": "LCnQCzEMIGE",
                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DX9uKNf5jGX6m",
                "youtube": "https://www.youtube.com/watch?v=LCnQCzEMIGE",
            },
        ],
    }),
)

QUESTIONS: list = [
    {
        "text": "Q1. How often do you deliberately listen to calm music as part of your pre-exam routine?",
        "options": [
            ("Always — it is a fixed habit before every exam", 0),
            ("Often — I do it most of the time", 1),
            ("Sometimes — only when I remember or feel particularly nervous", 2),
            ("Rarely — I've tried it but have no consistent habit", 3),
            ("Never — I do not use music before exams", 4),
        ],
    },
    {
        "text": "Q2. When you begin a calm music listening session before an exam, how quickly do you notice your breathing becoming slower and steadier?",
        "options": [
            ("Within the first 2–3 minutes", 0),
            ("Within about 5 minutes", 1),
            ("After 10–15 minutes", 2),
            ("After a very long time, if at all", 3),
            ("I never notice any change in my breathing", 4),
        ],
    },
    {
        "text": "Q3. How would you describe the physical tension in your body (e.g., tight shoulders, clenched jaw) right before an exam, even after listening to calm music?",
        "options": [
            ("No tension at all — I feel fully loose and at ease", 0),
            ("Slight tension that fades quickly", 1),
            ("Moderate tension that lingers throughout", 2),
            ("Significant tension that does not ease much", 3),
            ("Severe, persistent tension regardless of music", 4),
        ],
    },
    {
        "text": "Q4. How deliberately do you choose music based on relaxation-specific qualities (e.g., slow tempo, no lyrics, soft instrumentation) before an exam?",
        "options": [
            ("Always — I carefully select tracks based on their calming properties", 0),
            ("Often — I usually look for slow, soft pieces", 1),
            ("Sometimes — my choices are fairly random", 2),
            ("Rarely — I prefer energetic music even before exams", 3),
            ("Never — I do not consider musical qualities when choosing", 4),
        ],
    },
    {
        "text": "Q5. After a calm music session before an exam, how do you feel emotionally?",
        "options": [
            ("Noticeably calmer and more positive than before", 0),
            ("Somewhat calmer", 1),
            ("About the same — no emotional shift", 2),
            ("Slightly more anxious, as the music gives me time to overthink", 3),
            ("More anxious — music either does nothing or makes things worse", 4),
        ],
    },
    {
        "text": "Q6. How well do you sleep the night before an exam when you include calm music in your evening routine?",
        "options": [
            ("Very well — I fall asleep quickly and wake up rested", 0),
            ("Fairly well — some restlessness but manageable", 1),
            ("Average — I wake up occasionally but recover", 2),
            ("Poorly — I toss and turn for most of the night", 3),
            ("Very poorly — I barely sleep at all", 4),
        ],
    },
    {
        "text": "Q7. While listening to calm music before an exam, how often do you find yourself imagining negative outcomes (e.g., failing, blanking out)?",
        "options": [
            ("Never — the music keeps my mind clear and present", 0),
            ("Rarely — occasional worry that passes quickly", 1),
            ("Sometimes — I drift into anxious thinking but can recover", 2),
            ("Often — music provides little protection against worry", 3),
            ("Always — I cannot stop catastrophising regardless of what I listen to", 4),
        ],
    },
    {
        "text": "Q8. How well does calm music help you shift mentally from active studying to a relaxed, exam-ready state?",
        "options": [
            ("Extremely well — the mental shift happens almost immediately", 0),
            ("Well — the transition occurs gradually within one session", 1),
            ("Partially — some relaxation is achieved but stress lingers", 2),
            ("Minimally — I remain tense through most of the session", 3),
            ("Not at all — music has no transitional effect for me", 4),
        ],
    },
    {
        "text": "Q9. How would you rate your overall anxiety level in the 30 minutes before an exam, even when using calm music as preparation?",
        "options": [
            ("Very low — I feel composed, grounded, and ready", 0),
            ("Low — mild nervousness that does not interfere", 1),
            ("Moderate — noticeable anxiety but still manageable", 2),
            ("High — significant anxiety that shakes my confidence", 3),
            ("Very high — I feel overwhelmed and unable to settle", 4),
        ],
    },
    {
        "text": "Q10. After listening to calm music before an exam, how confident do you feel about your performance?",
        "options": [
            ("Much more confident than I would feel without music", 0),
            ("Slightly more confident", 1),
            ("No change in my confidence level", 2),
            ("Slightly less confident — I feel the time should have gone to last-minute revision", 3),
            ("Much less confident — music time feels wasted", 4),
        ],
    },
    {
        "text": "Q11. How effectively does calm music reduce physical symptoms of exam anxiety for you (e.g., racing heart, sweaty palms, stomach discomfort)?",
        "options": [
            ("Very effectively — physical symptoms largely subside", 0),
            ("Effectively — symptoms reduce noticeably", 1),
            ("Partially — some physical relief but symptoms persist", 2),
            ("Minimally — little to no physical change is noticeable", 3),
            ("Not at all, or symptoms worsen", 4),
        ],
    },
    {
        "text": "Q12. How long are you typically able to sustain a calm, relaxed state after a pre-exam music session before exam-related stress takes over again?",
        "options": [
            ("More than 20 minutes of sustained calm", 0),
            ("Between 10 and 20 minutes", 1),
            ("Around 5 to 10 minutes", 2),
            ("Less than 5 minutes", 3),
            ("Stress is present from the very beginning; music creates no window of calm", 4),
        ],
    },
    {
        "text": "Q13. How easily can you recall studied material during an exam when you have used calm music as part of your pre-exam preparation?",
        "options": [
            ("Very easily — my memory feels clear and well-organised", 0),
            ("Fairly easily — minor gaps but generally strong recall", 1),
            ("Moderately — I recall some things but struggle with others", 2),
            ("With difficulty — anxiety significantly disrupts my recall", 3),
            ("Very poorly — I feel I have forgotten most of what I studied", 4),
        ],
    },
    {
        "text": "Q14. How often does your attention wander during a calm music relaxation session (e.g., picking up your phone, pacing, checking the time)?",
        "options": [
            ("Never — I remain still and fully present", 0),
            ("Rarely — I lose focus briefly but return quickly", 1),
            ("Sometimes — I frequently shift between relaxing and other activities", 2),
            ("Often — I struggle to sit and genuinely listen", 3),
            ("Always — I am unable to remain still or focused even with music", 4),
        ],
    },
    {
        "text": "Q15. How do you feel about the exam subject or topic itself while calm music is playing before the test?",
        "options": [
            ("Positive and ready — music helps me view the subject with confidence", 0),
            ("Neutral to mildly positive", 1),
            ("Indifferent — I feel neither ready nor afraid", 2),
            ("Slightly apprehensive about the content", 3),
            ("Very anxious or avoidant — I cannot bear thinking about the subject", 4),
        ],
    },
    {
        "text": "Q16. How structured and consistent is your use of calm music as a pre-exam relaxation strategy across different exams?",
        "options": [
            ("Highly structured — I follow the same music-based routine every time", 0),
            ("Mostly consistent — I plan for it and usually follow through", 1),
            ("Somewhat consistent — I do it when I feel like it", 2),
            ("Inconsistent — I try it occasionally without any real plan", 3),
            ("Non-existent — I have no music-based routine whatsoever", 4),
        ],
    },
    {
        "text": "Q17. How emotionally drained or fatigued do you feel on the morning of an exam, even after using calm music the evening before?",
        "options": [
            ("Not at all — I feel energised and mentally sharp", 0),
            ("Slightly tired but alert enough", 1),
            ("Moderately fatigued — I need some time to warm up", 2),
            ("Quite exhausted — low energy is affecting my mood", 3),
            ("Completely depleted — I feel worn out before the exam even starts", 4),
        ],
    },
    {
        "text": "Q18. When calm music is playing, how well can you absorb or review study material at a light, relaxed pace?",
        "options": [
            ("Very well — calm music enhances my review process noticeably", 0),
            ("Fairly well — some positive effect on focus", 1),
            ("Neutrally — music neither helps nor hinders light review", 2),
            ("Poorly — I get distracted by the music itself", 3),
            ("Very poorly — I cannot combine music with any form of study", 4),
        ],
    },
    {
        "text": "Q19. How do people around you (classmates, housemates, family) tend to describe your pre-exam demeanour after you have used calm music as preparation?",
        "options": [
            ("They remark that I seem calm and well-prepared", 0),
            ("They say I appear relatively composed", 1),
            ("They describe me as neither calm nor particularly distressed", 2),
            ("They express concern about how nervous I seem", 3),
            ("They find my pre-exam anxiety visibly worrying", 4),
        ],
    },
    {
        "text": "Q20. Overall, how would you rate the effectiveness of calm music as a relaxation tool within your exam preparation?",
        "options": [
            ("Highly effective — it is an indispensable part of my preparation", 0),
            ("Effective — it provides clear, reliable benefit", 1),
            ("Somewhat effective — it has modest but inconsistent benefits", 2),
            ("Largely ineffective — it makes little real difference", 3),
            ("Ineffective or counterproductive — it does nothing or increases my stress", 4),
        ],
    },
]

USED_IDS: set = set()

# ─────────────────────────────────────────────
# HELPER / VALIDATION FUNCTIONS
# ─────────────────────────────────────────────

def validate_name(name: str) -> bool:
    """Return True only if name uses letters, spaces, hyphens, apostrophes."""
    if not name or not name.strip():
        return False
    valid: bool = True
    for ch in name:          # for loop for input validation
        if ch not in ALLOWED_CHARS:
            valid = False
            break
    return valid


def validate_dob(dob_str: str) -> bool:
    """Return True if date is valid DD/MM/YYYY and realistic."""
    pattern: str = r"^\d{2}/\d{2}/\d{4}$"
    if not re.match(pattern, dob_str):
        return False
    try:
        day, month, year = dob_str.split("/")
        birth: datetime.date = datetime.date(int(year), int(month), int(day))
        today: datetime.date = datetime.date.today()
        age: int = today.year - birth.year
        if birth > today:
            return False
        if age > 120:
            return False
        return True
    except ValueError:
        return False


def validate_student_id(sid: str) -> bool:
    """Return True if student ID contains only digits."""
    if not sid:
        return False
    is_valid: bool = True
    while is_valid:          # while loop for input validation
        for ch in sid:
            if not ch.isdigit():
                is_valid = False
                break
        break
    return is_valid


def get_psychological_state(score: int) -> dict:
    """Return state label and description based on total score."""
    result: dict = {}
    for low, high, label, description in SCORE_STATES:
        if low <= score <= high:
            result = {"label": label, "description": description, "low": low, "high": high}
            break
    return result


def get_playlist_for_score(score: int) -> dict:
    """Return the matching music playlist recommendation for a given score."""
    playlist: dict = {}
    for low, high, data in SCORE_PLAYLISTS:
        if low <= score <= high:
            playlist = data
            break
    return playlist


def compute_score(answers: dict) -> int:
    """Sum up all answer scores."""
    total: int = 0
    for q_idx in range(TOTAL_QUESTIONS):
        if q_idx in answers:
            total += answers[q_idx]
    return total


def build_results_dict(user_info: dict, answers: dict, score: int, state: dict) -> dict:
    """Assemble full results into a structured dict."""
    answered_questions: list = []
    for i, q in enumerate(QUESTIONS):
        if i in answers:
            chosen_score: int = answers[i]
            chosen_text: str = ""
            for opt_text, opt_score in q["options"]:
                if opt_score == chosen_score:
                    chosen_text = opt_text
                    break
            answered_questions.append({
                "question": q["text"],
                "answer": chosen_text,
                "score": chosen_score,
            })
    return {
        "surname_name": user_info.get("name", ""),
        "date_of_birth": user_info.get("dob", ""),
        "student_id": user_info.get("sid", ""),
        "total_score": score,
        "psychological_state": state.get("label", ""),
        "description": state.get("description", ""),
        "answers": answered_questions,
    }


def results_to_txt(data: dict) -> str:
    lines: list = [
        "=" * 60,
        f"  {APP_TITLE}",
        f"  {CONDUCTOR}",
        "=" * 60,
        f"Name          : {data['surname_name']}",
        f"Date of Birth : {data['date_of_birth']}",
        f"Student ID    : {data['student_id']}",
        f"Total Score   : {data['total_score']} / {MAX_SCORE}",
        f"State         : {data['psychological_state']}",
        f"Assessment    : {data['description']}",
        "-" * 60,
        "DETAILED ANSWERS:",
        "-" * 60,
    ]
    for item in data["answers"]:
        lines.append(f"  {item['question']}")
        lines.append(f"  -> {item['answer']}  [score: {item['score']}]")
        lines.append("")
    return "\n".join(lines)


def results_to_csv(data: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    writer.writerow(["Name", data["surname_name"]])
    writer.writerow(["Date of Birth", data["date_of_birth"]])
    writer.writerow(["Student ID", data["student_id"]])
    writer.writerow(["Total Score", data["total_score"]])
    writer.writerow(["Psychological State", data["psychological_state"]])
    writer.writerow(["Description", data["description"]])
    writer.writerow([])
    writer.writerow(["#", "Question", "Answer", "Score"])
    for idx, item in enumerate(data["answers"], 1):
        writer.writerow([idx, item["question"], item["answer"], item["score"]])
    return output.getvalue()


def results_to_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def load_results_from_file(content: str, file_ext: str) -> dict:
    """Parse uploaded results file and return dict."""
    loaded: dict = {}
    if file_ext == "json":
        loaded = json.loads(content)
    elif file_ext == "csv":
        reader = csv.reader(io.StringIO(content))
        rows: list = list(reader)
        for row in rows:
            if len(row) == 2:
                key, val = row[0].strip(), row[1].strip()
                if key == "Name":
                    loaded["surname_name"] = val
                elif key == "Date of Birth":
                    loaded["date_of_birth"] = val
                elif key == "Student ID":
                    loaded["student_id"] = val
                elif key == "Total Score":
                    loaded["total_score"] = int(val)
                elif key == "Psychological State":
                    loaded["psychological_state"] = val
                elif key == "Description":
                    loaded["description"] = val
    elif file_ext == "txt":
        for line in content.splitlines():
            if line.startswith("Name"):
                loaded["surname_name"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Date of Birth"):
                loaded["date_of_birth"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Student ID"):
                loaded["student_id"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Total Score"):
                part = line.split(":", 1)[-1].strip().split("/")[0].strip()
                loaded["total_score"] = int(part)
            elif line.startswith("State"):
                loaded["psychological_state"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Assessment"):
                loaded["description"] = line.split(":", 1)[-1].strip()
    return loaded


# ─────────────────────────────────────────────
# MUSIC WIDGET COMPONENTS
# ─────────────────────────────────────────────

def render_ambient_player() -> None:
    """Render ambient music player shown during the survey."""
    music_on: bool = st.session_state.get("music_on", False)
    track_idx: int = st.session_state.get("track_idx", 0)
    track: dict = SURVEY_AMBIENT_TRACKS[track_idx]

    col_a, col_b, col_c = st.columns([1, 3, 1])
    with col_a:
        if st.button("⏮", key="prev_track", help="Previous track"):
            st.session_state.track_idx = (track_idx - 1) % len(SURVEY_AMBIENT_TRACKS)
            st.rerun()
    with col_b:
        toggle_label: str = "🔇 Pause Music" if music_on else "🎵 Play Ambient Music"
        if st.button(toggle_label, key="music_toggle", use_container_width=True):
            st.session_state.music_on = not music_on
            st.rerun()
    with col_c:
        if st.button("⏭", key="next_track", help="Next track"):
            st.session_state.track_idx = (track_idx + 1) % len(SURVEY_AMBIENT_TRACKS)
            st.rerun()

    if music_on:
        yt_id: str = track["youtube_id"]
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.7);
                border-radius: 14px;
                padding: 0.8rem 1rem;
                border: 1px solid #aed6f1;
                margin: 0.5rem 0 0.8rem 0;
                display: flex;
                align-items: center;
                gap: 0.8rem;
            ">
                <span style="font-size:1.5rem;">{track['emoji']}</span>
                <div>
                    <p style="margin:0;font-weight:700;color:#1a5276;font-size:0.9rem;">
                        Now Playing: {track['title']}
                    </p>
                    <p style="margin:0;color:#2471a3;font-size:0.8rem;">{track['artist']}</p>
                </div>
                <span style="margin-left:auto;font-size:0.75rem;color:#5dade2;font-weight:700;
                    animation: pulse 1.5s infinite;">
                    ♪ LIVE
                </span>
            </div>
            <iframe
                width="100%" height="80"
                src="https://www.youtube.com/embed/{yt_id}?autoplay=1&mute=0&controls=1&loop=1&playlist={yt_id}"
                frameborder="0"
                allow="autoplay; encrypted-media"
                allowfullscreen
                style="border-radius:10px; display:block;"
            ></iframe>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.4);
                border-radius: 14px;
                padding: 0.5rem 1rem;
                border: 1px dashed #aed6f1;
                text-align: center;
                color: #85c1e9;
                font-size: 0.85rem;
                margin: 0.3rem 0 0.5rem 0;
            ">
                {track['emoji']} <em>Press Play Ambient Music to listen while you answer</em>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_playlist_recommendations(score: int) -> None:
    """Render personalised playlist cards based on the user's score."""
    playlist: dict = get_playlist_for_score(score)
    if not playlist:
        return

    colour: str = playlist.get("colour", "#2471a3")

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {colour}18, {colour}06);
            border: 1.5px solid {colour}55;
            border-radius: 18px;
            padding: 1.5rem 2rem 1rem;
            margin: 1.5rem 0 0.5rem 0;
        ">
            <h3 style="color:{colour};margin-top:0;font-family:'Raleway',sans-serif;">
                🎧 Your Personalised Music Prescription
            </h3>
            <p style="font-size:1.05rem;font-weight:700;color:#1a5276;margin-bottom:0.3rem;">
                {playlist['emoji']} {playlist['mood']}
            </p>
            <p style="color:#1a5276;margin-bottom:0;">{playlist['message']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for track in playlist["tracks"]:
        yt_id: str = track["youtube_id"]
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.88);
                border-radius: 14px;
                padding: 1rem 1.2rem 0.9rem;
                margin: 0.8rem 0;
                border: 1px solid #aed6f1;
                box-shadow: 0 4px 14px rgba(41,128,185,0.09);
            ">
                <p style="margin:0 0 0.2rem 0;font-weight:700;color:#1a5276;font-size:1rem;">
                    🎶 {track['title']}
                </p>
                <p style="margin:0 0 0.7rem 0;color:#5d8aa8;font-size:0.85rem;">
                    {track['desc']}
                </p>
                <iframe
                    width="100%" height="90"
                    src="https://www.youtube.com/embed/{yt_id}?controls=1&rel=0&modestbranding=1"
                    frameborder="0"
                    allow="encrypted-media"
                    allowfullscreen
                    style="border-radius:8px;display:block;margin-bottom:0.7rem;"
                ></iframe>
                <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
                    <a href="{track['youtube']}" target="_blank" style="
                        background:#ff0000;color:white;
                        text-decoration:none;border-radius:50px;
                        padding:0.3rem 1.1rem;font-size:0.8rem;font-weight:700;
                        display:inline-block;
                    ">▶ Open on YouTube</a>
                    <a href="{track['spotify']}" target="_blank" style="
                        background:#1db954;color:white;
                        text-decoration:none;border-radius:50px;
                        padding:0.3rem 1.1rem;font-size:0.8rem;font-weight:700;
                        display:inline-block;
                    ">🎵 Open on Spotify</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# PAGE STYLING
# ─────────────────────────────────────────────

def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Raleway:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Nunito', sans-serif;
        }

        .stApp {
            background: linear-gradient(135deg, #e8f4fd 0%, #d0eaf7 40%, #bce0f5 100%);
            min-height: 100vh;
        }

        h1, h2, h3 {
            font-family: 'Raleway', sans-serif;
            color: #1a5276;
        }

        .card {
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(8px);
            border-radius: 18px;
            padding: 2rem 2.5rem;
            box-shadow: 0 8px 32px rgba(30,100,160,0.10);
            border: 1px solid rgba(160,210,240,0.4);
            margin-bottom: 1.5rem;
        }

        .title-hero {
            text-align: center;
            padding: 2.5rem 1rem 1rem;
        }

        .title-hero h1 {
            font-size: 2.2rem;
            color: #1a5276;
            margin-bottom: 0.3rem;
        }

        .title-hero p {
            color: #2471a3;
            font-size: 1.05rem;
        }

        .conductor-badge {
            display: inline-block;
            background: linear-gradient(90deg, #2980b9, #5dade2);
            color: white;
            border-radius: 50px;
            padding: 0.3rem 1.2rem;
            font-size: 0.9rem;
            font-weight: 700;
            margin-top: 0.5rem;
        }

        .progress-label {
            font-size: 0.85rem;
            color: #2471a3;
            font-weight: 600;
            margin-bottom: 0.2rem;
        }

        .stButton > button {
            background: linear-gradient(90deg, #2980b9, #5dade2) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 0.55rem 2rem !important;
            font-weight: 700 !important;
            font-family: 'Nunito', sans-serif !important;
            font-size: 1rem !important;
            transition: transform 0.15s, box-shadow 0.15s !important;
            box-shadow: 0 4px 14px rgba(41,128,185,0.25) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(41,128,185,0.35) !important;
        }

        .stRadio > label {
            font-weight: 600;
            color: #1a5276;
        }

        .result-box {
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-top: 1rem;
            text-align: center;
        }

        .score-chip {
            display: inline-block;
            background: #2980b9;
            color: white;
            border-radius: 50px;
            padding: 0.4rem 1.5rem;
            font-size: 1.5rem;
            font-weight: 800;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background: rgba(240,248,255,0.7);
            border: 1px solid #aed6f1;
            border-radius: 10px;
            padding: 0.4rem 0.8rem;
            margin: 0.2rem 0;
            display: block;
            transition: background 0.2s;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: rgba(174,214,241,0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# SLIDES / PAGES
# ─────────────────────────────────────────────

def page_welcome() -> None:
    st.markdown(
        f"""
        <div class="title-hero">
            <h1>🎵 {APP_TITLE}</h1>
            <p>An evidence-based assessment of how calm music influences your pre-exam psychological state.</p>
            <span class="conductor-badge">{CONDUCTOR}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card">
            <h3>About This Survey</h3>
            <p>This questionnaire evaluates your psychological readiness before exams by exploring how
            calm music affects your stress, anxiety, sleep, confidence, and physical symptoms.
            Based on your responses, it will determine your current psychological state and
            provide a personalised assessment — <strong>plus a curated music playlist</strong>
            matched exactly to your results.</p>
            <ul>
                <li>📋 <strong>20 questions</strong> — each with 5 answer options</li>
                <li>⏱️ Estimated completion time: <strong>~8–10 minutes</strong></li>
                <li>🎵 Optional ambient music to play <strong>while you answer</strong></li>
                <li>🎧 Personalised playlist recommendations <strong>based on your score</strong></li>
                <li>🔒 Your data remains private and confidential</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Start New Survey", use_container_width=True):
            st.session_state.page = "consent"
            st.rerun()
    with col2:
        if st.button("📂 Load Existing Results", use_container_width=True):
            st.session_state.page = "load"
            st.rerun()


def page_consent() -> None:
    st.markdown('<div class="title-hero"><h1>📋 Informed Consent</h1></div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card">
            <h3>🔒 Privacy & Confidentiality</h3>
            <p>All information you provide is kept strictly confidential.
            Your responses will not be shared with any third parties and will only be used
            for the purpose of this psychological state assessment.</p>

            <h3>⏱️ Time Commitment</h3>
            <p>This survey consists of <strong>20 questions</strong> and takes approximately
            <strong>{ESTIMATED_TIME:.1f} minutes</strong> to complete.</p>

            <h3>🤝 Voluntary Participation</h3>
            <p>Your participation is entirely voluntary. You may exit the survey at any time
            without consequence. Completing the survey implies your consent to participate.</p>

            <h3>🎵 Music During the Survey</h3>
            <p>You will have the option to play calming ambient music while answering the questions.
            This feature is entirely optional and can be toggled on or off at any time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ I Agree — Proceed", use_container_width=True):
            st.session_state.page = "user_info"
            st.rerun()
    with col2:
        if st.button("❌ Exit Survey", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()


def page_user_info() -> None:
    st.markdown('<div class="title-hero"><h1>👤 Your Details</h1></div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    name = st.text_input(
        "Full Name (Surname and Given Name)",
        value=st.session_state.get("user_name", ""),
        placeholder="e.g. Smith-Jones Mary Ann",
    )
    dob = st.text_input(
        "Date of Birth (DD/MM/YYYY)",
        value=st.session_state.get("user_dob", ""),
        placeholder="e.g. 15/03/2002",
    )
    sid = st.text_input(
        "Student ID (digits only)",
        value=st.session_state.get("user_sid", ""),
        placeholder="e.g. 20240001",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Continue to Survey →", use_container_width=True):
        error_set: set = set()

        if not validate_name(name):
            error_set.add("Name may only contain letters, spaces, hyphens (-), and apostrophes ('). No digits or other symbols.")
        if not validate_dob(dob):
            error_set.add("Date of birth must be in DD/MM/YYYY format with realistic values.")
        if not validate_student_id(sid):
            error_set.add("Student ID must contain only digits.")

        if error_set:
            for err in error_set:
                st.error(err)
        else:
            st.session_state.user_name = name.strip()
            st.session_state.user_dob = dob.strip()
            st.session_state.user_sid = sid.strip()
            st.session_state.page = "survey"
            st.session_state.current_q = 0
            st.session_state.music_on = False
            st.session_state.track_idx = 0
            if "answers" not in st.session_state:
                st.session_state.answers = {}
            st.rerun()

    if st.button("← Back"):
        st.session_state.page = "consent"
        st.rerun()


def page_survey() -> None:
    q_idx: int = st.session_state.get("current_q", 0)
    answers: dict = st.session_state.get("answers", {})

    # Progress bar
    progress: float = q_idx / TOTAL_QUESTIONS
    st.markdown(
        f'<p class="progress-label">Question {q_idx + 1} of {TOTAL_QUESTIONS}</p>',
        unsafe_allow_html=True,
    )
    st.progress(progress)

    # Ambient music player
    st.markdown("---")
    render_ambient_player()
    st.markdown("---")

    question: dict = QUESTIONS[q_idx]
    options: list = question["options"]
    option_labels: list = [opt[0] for opt in options]
    option_scores: list = [opt[1] for opt in options]

    default_idx: int = 0
    if q_idx in answers:
        saved_score: int = answers[q_idx]
        for i, sc in enumerate(option_scores):
            if sc == saved_score:
                default_idx = i
                break

    st.markdown(f'<div class="card"><h3>{question["text"]}</h3>', unsafe_allow_html=True)

    chosen_label = st.radio(
        "Select your answer:",
        option_labels,
        index=default_idx,
        key=f"q_{q_idx}",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    chosen_score_val: int = option_scores[option_labels.index(chosen_label)]
    answers[q_idx] = chosen_score_val
    st.session_state.answers = answers

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if q_idx > 0:
            if st.button("← Previous"):
                st.session_state.current_q = q_idx - 1
                st.rerun()
    with col3:
        if q_idx < TOTAL_QUESTIONS - 1:
            if st.button("Next →"):
                st.session_state.current_q = q_idx + 1
                st.rerun()
        else:
            if st.button("✅ Submit"):
                st.session_state.music_on = False
                st.session_state.page = "results"
                st.rerun()


def page_results() -> None:
    answers: dict = st.session_state.get("answers", {})
    user_info: dict = {
        "name": st.session_state.get("user_name", ""),
        "dob": st.session_state.get("user_dob", ""),
        "sid": st.session_state.get("user_sid", ""),
    }

    score: int = compute_score(answers)
    state: dict = get_psychological_state(score)

    st.markdown('<div class="title-hero"><h1>📊 Your Results</h1></div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card">
            <p><strong>Name:</strong> {user_info['name']}</p>
            <p><strong>Date of Birth:</strong> {user_info['dob']}</p>
            <p><strong>Student ID:</strong> {user_info['sid']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card result-box">
            <p style="font-size:1rem;color:#2471a3;font-weight:600;">Total Score</p>
            <span class="score-chip">{score} / {MAX_SCORE}</span>
            <h2 style="margin-top:1rem;">{state.get('label','')}</h2>
            <p style="color:#1a5276;">{state.get('description','')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Personalised music recommendations
    render_playlist_recommendations(score)

    with st.expander("📖 Full Scoring Scale"):
        for low, high, label, desc in SCORE_STATES:
            marker: str = "  ◀ You are here" if low <= score <= high else ""
            st.markdown(f"**{low}–{high}  {label}**{marker}")
            st.caption(desc)

    st.markdown("---")
    st.subheader("💾 Save Your Results")

    save_format: str = st.selectbox(
        "Choose file format:",
        ["JSON", "CSV", "TXT"],
        key="save_format",
    )

    results_data: dict = build_results_dict(user_info, answers, score, state)

    if save_format == "JSON":
        file_content: str = results_to_json(results_data)
        mime: str = "application/json"
        filename: str = f"survey_results_{user_info['sid']}.json"
    elif save_format == "CSV":
        file_content = results_to_csv(results_data)
        mime = "text/csv"
        filename = f"survey_results_{user_info['sid']}.csv"
    else:
        file_content = results_to_txt(results_data)
        mime = "text/plain"
        filename = f"survey_results_{user_info['sid']}.txt"

    st.download_button(
        label=f"⬇️ Download as {save_format}",
        data=file_content,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )

    if st.button("🔄 Start New Survey", use_container_width=True):
        for key in ["answers", "user_name", "user_dob", "user_sid", "current_q", "music_on", "track_idx"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.page = "welcome"
        st.rerun()


def page_load() -> None:
    st.markdown('<div class="title-hero"><h1>📂 Load Existing Results</h1></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="card"><p>Upload a previously saved results file (JSON, CSV, or TXT) to view your results and music recommendations.</p></div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload results file",
        type=["json", "csv", "txt"],
        key="upload_file",
    )

    if uploaded is not None:
        ext: str = uploaded.name.rsplit(".", 1)[-1].lower()
        content: str = uploaded.read().decode("utf-8")

        try:
            loaded: dict = load_results_from_file(content, ext)
        except Exception as e:
            st.error(f"Could not parse file: {e}")
            loaded = {}

        if loaded:
            st.success("File loaded successfully!")
            loaded_score: int = loaded.get("total_score", -1)

            st.markdown(
                f"""
                <div class="card">
                    <p><strong>Name:</strong> {loaded.get('surname_name','—')}</p>
                    <p><strong>Date of Birth:</strong> {loaded.get('date_of_birth','—')}</p>
                    <p><strong>Student ID:</strong> {loaded.get('student_id','—')}</p>
                    <p><strong>Total Score:</strong> {loaded.get('total_score','—')} / {MAX_SCORE}</p>
                    <p><strong>Psychological State:</strong> {loaded.get('psychological_state','—')}</p>
                    <p><strong>Assessment:</strong> {loaded.get('description','—')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if loaded_score >= 0:
                render_playlist_recommendations(loaded_score)
        else:
            st.warning("File could not be read or has an unexpected format.")

    if st.button("← Back to Home"):
        st.session_state.page = "welcome"
        st.rerun()


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎵",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    apply_styles()

    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "music_on" not in st.session_state:
        st.session_state.music_on = False
    if "track_idx" not in st.session_state:
        st.session_state.track_idx = 0

    page: str = st.session_state.page

    if page == "welcome":
        page_welcome()
    elif page == "consent":
        page_consent()
    elif page == "user_info":
        page_user_info()
    elif page == "survey":
        page_survey()
    elif page == "results":
        page_results()
    elif page == "load":
        page_load()
    else:
        st.session_state.page = "welcome"
        st.rerun()


if __name__ == "__main__":
    main()
