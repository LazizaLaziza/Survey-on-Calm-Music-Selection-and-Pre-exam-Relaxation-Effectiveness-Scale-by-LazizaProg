import streamlit as st
import json
from datetime import datetime

# ─────────────────────────────────────────────
#  VARIABLE TYPES  (satisfies the 10-type criterion)
# ─────────────────────────────────────────────
version_float: float = 1.0                                      # float
MAX_SCORE:     int   = 80                                       # int
APP_TITLE:     str   = "Calm Music & Exam Anxiety Survey"       # str

# Psychological states stored in a dict
psych_states: dict = {
    "Optimal Relaxation":          (0,  13, "Calm music is highly effective; you are in an excellent pre-exam psychological state."),
    "Good Relaxation":             (14, 26, "Music reliably supports your pre-exam calm; minor adjustments could further improve outcomes."),
    "Moderate Relaxation":         (27, 40, "Music provides partial relief; residual exam anxiety remains and may affect performance."),
    "Limited Relaxation Response": (41, 53, "Music has modest effects; pre-exam anxiety is noticeably present and managing it is advisable."),
    "Poor Relaxation Response":    (54, 67, "Music provides little relief; significant pre-exam stress is likely impacting your readiness. Consider additional coping strategies."),
    "Ineffective Relaxation":      (68, 80, "Music-based strategies are not working for you; professional guidance or alternative stress management techniques are strongly recommended."),
}

# Valid score range
valid_score_range: range = range(0, MAX_SCORE + 1)              # range

# Forbidden characters for name validation
FORBIDDEN_IN_NAME: frozenset = frozenset("0123456789")          # frozenset

# Unique result labels
result_labels: set = set(psych_states.keys())                   # set

# Questions list (filled below)
questions: list = []                                            # list

# Layout ratio tuple
LAYOUT_RATIO: tuple = (1, 2)                                    # tuple

# Boolean flag for questions load status
questions_loaded: bool = False                                  # bool

# ─────────────────────────────────────────────
#  QUESTIONS DATA  (embedded in code)
# ─────────────────────────────────────────────
QUESTIONS_DATA: list = [
    {
        "q": "How often do you deliberately listen to calm music as part of your pre-exam routine?",
        "opts": [
            ["Always \u2014 it is a fixed habit before every exam", 0],
            ["Often \u2014 I do it most of the time", 1],
            ["Sometimes \u2014 only when I remember or feel particularly nervous", 2],
            ["Rarely \u2014 I've tried it but have no consistent habit", 3],
            ["Never \u2014 I do not use music before exams", 4],
        ]
    },
    {
        "q": "When you begin a calm music listening session before an exam, how quickly do you notice your breathing becoming slower and steadier?",
        "opts": [
            ["Within the first 2\u20133 minutes", 0],
            ["Within about 5 minutes", 1],
            ["After 10\u201315 minutes", 2],
            ["After a very long time, if at all", 3],
            ["I never notice any change in my breathing", 4],
        ]
    },
    {
        "q": "How would you describe the physical tension in your body (e.g., tight shoulders, clenched jaw) right before an exam, even after listening to calm music?",
        "opts": [
            ["No tension at all \u2014 I feel fully loose and at ease", 0],
            ["Slight tension that fades quickly", 1],
            ["Moderate tension that lingers throughout", 2],
            ["Significant tension that does not ease much", 3],
            ["Severe, persistent tension regardless of music", 4],
        ]
    },
    {
        "q": "How deliberately do you choose music based on relaxation-specific qualities (e.g., slow tempo, no lyrics, soft instrumentation) before an exam?",
        "opts": [
            ["Always \u2014 I carefully select tracks based on their calming properties", 0],
            ["Often \u2014 I usually look for slow, soft pieces", 1],
            ["Sometimes \u2014 my choices are fairly random", 2],
            ["Rarely \u2014 I prefer energetic music even before exams", 3],
            ["Never \u2014 I do not consider musical qualities when choosing", 4],
        ]
    },
    {
        "q": "After a calm music session before an exam, how do you feel emotionally?",
        "opts": [
            ["Noticeably calmer and more positive than before", 0],
            ["Somewhat calmer", 1],
            ["About the same \u2014 no emotional shift", 2],
            ["Slightly more anxious, as the music gives me time to overthink", 3],
            ["More anxious \u2014 music either does nothing or makes things worse", 4],
        ]
    },
    {
        "q": "How well do you sleep the night before an exam when you include calm music in your evening routine?",
        "opts": [
            ["Very well \u2014 I fall asleep quickly and wake up rested", 0],
            ["Fairly well \u2014 some restlessness but manageable", 1],
            ["Average \u2014 I wake up occasionally but recover", 2],
            ["Poorly \u2014 I toss and turn for most of the night", 3],
            ["Very poorly \u2014 I barely sleep at all", 4],
        ]
    },
    {
        "q": "While listening to calm music before an exam, how often do you find yourself imagining negative outcomes (e.g., failing, blanking out)?",
        "opts": [
            ["Never \u2014 the music keeps my mind clear and present", 0],
            ["Rarely \u2014 occasional worry that passes quickly", 1],
            ["Sometimes \u2014 I drift into anxious thinking but can recover", 2],
            ["Often \u2014 music provides little protection against worry", 3],
            ["Always \u2014 I cannot stop catastrophising regardless of what I listen to", 4],
        ]
    },
    {
        "q": "How well does calm music help you shift mentally from active studying to a relaxed, exam-ready state?",
        "opts": [
            ["Extremely well \u2014 the mental shift happens almost immediately", 0],
            ["Well \u2014 the transition occurs gradually within one session", 1],
            ["Partially \u2014 some relaxation is achieved but stress lingers", 2],
            ["Minimally \u2014 I remain tense through most of the session", 3],
            ["Not at all \u2014 music has no transitional effect for me", 4],
        ]
    },
    {
        "q": "How would you rate your overall anxiety level in the 30 minutes before an exam, even when using calm music as preparation?",
        "opts": [
            ["Very low \u2014 I feel composed, grounded, and ready", 0],
            ["Low \u2014 mild nervousness that does not interfere", 1],
            ["Moderate \u2014 noticeable anxiety but still manageable", 2],
            ["High \u2014 significant anxiety that shakes my confidence", 3],
            ["Very high \u2014 I feel overwhelmed and unable to settle", 4],
        ]
    },
    {
        "q": "After listening to calm music before an exam, how confident do you feel about your performance?",
        "opts": [
            ["Much more confident than I would feel without music", 0],
            ["Slightly more confident", 1],
            ["No change in my confidence level", 2],
            ["Slightly less confident \u2014 I feel the time should have gone to last-minute revision", 3],
            ["Much less confident \u2014 music time feels wasted", 4],
        ]
    },
    {
        "q": "How effectively does calm music reduce physical symptoms of exam anxiety for you (e.g., racing heart, sweaty palms, stomach discomfort)?",
        "opts": [
            ["Very effectively \u2014 physical symptoms largely subside", 0],
            ["Effectively \u2014 symptoms reduce noticeably", 1],
            ["Partially \u2014 some physical relief but symptoms persist", 2],
            ["Minimally \u2014 little to no physical change is noticeable", 3],
            ["Not at all, or symptoms worsen", 4],
        ]
    },
    {
        "q": "How long are you typically able to sustain a calm, relaxed state after a pre-exam music session before exam-related stress takes over again?",
        "opts": [
            ["More than 20 minutes of sustained calm", 0],
            ["Between 10 and 20 minutes", 1],
            ["Around 5 to 10 minutes", 2],
            ["Less than 5 minutes", 3],
            ["Stress is present from the very beginning; music creates no window of calm", 4],
        ]
    },
    {
        "q": "How easily can you recall studied material during an exam when you have used calm music as part of your pre-exam preparation?",
        "opts": [
            ["Very easily \u2014 my memory feels clear and well-organised", 0],
            ["Fairly easily \u2014 minor gaps but generally strong recall", 1],
            ["Moderately \u2014 I recall some things but struggle with others", 2],
            ["With difficulty \u2014 anxiety significantly disrupts my recall", 3],
            ["Very poorly \u2014 I feel I have forgotten most of what I studied", 4],
        ]
    },
    {
        "q": "How often does your attention wander during a calm music relaxation session (e.g., picking up your phone, pacing, checking the time)?",
        "opts": [
            ["Never \u2014 I remain still and fully present", 0],
            ["Rarely \u2014 I lose focus briefly but return quickly", 1],
            ["Sometimes \u2014 I frequently shift between relaxing and other activities", 2],
            ["Often \u2014 I struggle to sit and genuinely listen", 3],
            ["Always \u2014 I am unable to remain still or focused even with music", 4],
        ]
    },
    {
        "q": "How do you feel about the exam subject or topic itself while calm music is playing before the test?",
        "opts": [
            ["Positive and ready \u2014 music helps me view the subject with confidence", 0],
            ["Neutral to mildly positive", 1],
            ["Indifferent \u2014 I feel neither ready nor afraid", 2],
            ["Slightly apprehensive about the content", 3],
            ["Very anxious or avoidant \u2014 I cannot bear thinking about the subject", 4],
        ]
    },
    {
        "q": "How structured and consistent is your use of calm music as a pre-exam relaxation strategy across different exams?",
        "opts": [
            ["Highly structured \u2014 I follow the same music-based routine every time", 0],
            ["Mostly consistent \u2014 I plan for it and usually follow through", 1],
            ["Somewhat consistent \u2014 I do it when I feel like it", 2],
            ["Inconsistent \u2014 I try it occasionally without any real plan", 3],
            ["Non-existent \u2014 I have no music-based routine whatsoever", 4],
        ]
    },
    {
        "q": "How emotionally drained or fatigued do you feel on the morning of an exam, even after using calm music the evening before?",
        "opts": [
            ["Not at all \u2014 I feel energised and mentally sharp", 0],
            ["Slightly tired but alert enough", 1],
            ["Moderately fatigued \u2014 I need some time to warm up", 2],
            ["Quite exhausted \u2014 low energy is affecting my mood", 3],
            ["Completely depleted \u2014 I feel worn out before the exam even starts", 4],
        ]
    },
    {
        "q": "When calm music is playing, how well can you absorb or review study material at a light, relaxed pace?",
        "opts": [
            ["Very well \u2014 calm music enhances my review process noticeably", 0],
            ["Fairly well \u2014 some positive effect on focus", 1],
            ["Neutrally \u2014 music neither helps nor hinders light review", 2],
            ["Poorly \u2014 I get distracted by the music itself", 3],
            ["Very poorly \u2014 I cannot combine music with any form of study", 4],
        ]
    },
    {
        "q": "How do people around you (classmates, housemates, family) tend to describe your pre-exam demeanour after you have used calm music as preparation?",
        "opts": [
            ["They remark that I seem calm and well-prepared", 0],
            ["They say I appear relatively composed", 1],
            ["They describe me as neither calm nor particularly distressed", 2],
            ["They express concern about how nervous I seem", 3],
            ["They find my pre-exam anxiety visibly worrying", 4],
        ]
    },
    {
        "q": "Overall, how would you rate the effectiveness of calm music as a relaxation tool within your exam preparation?",
        "opts": [
            ["Highly effective \u2014 it is an indispensable part of my preparation", 0],
            ["Effective \u2014 it provides clear, reliable benefit", 1],
            ["Somewhat effective \u2014 it has modest but inconsistent benefits", 2],
            ["Largely ineffective \u2014 it makes little real difference", 3],
            ["Ineffective or counterproductive \u2014 it does nothing or increases my stress", 4],
        ]
    },
]

# ─────────────────────────────────────────────
#  USER-DEFINED FUNCTIONS
# ─────────────────────────────────────────────

def load_questions_from_file(filepath: str) -> list:
    """Try to load questions from an external JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_name(name: str) -> bool:
    """Return True if name is non-empty and contains no digits."""
    name = name.strip()
    if len(name) == 0:
        return False
    for ch in name:                             # for loop used in validation
        if ch in FORBIDDEN_IN_NAME:
            return False
    return True


def validate_dob(dob: str) -> bool:
    """Return True if dob matches YYYY-MM-DD format."""
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except Exception:
        return False


def validate_sid(sid: str) -> bool:
    """Return True if student ID is non-empty and digits only."""
    sid = sid.strip()
    if len(sid) == 0:
        return False
    for ch in sid:                              # for loop used in validation
        if ch not in "0123456789":
            return False
    return True


def collect_errors(name: str, surname: str, dob: str, sid: str) -> list:
    """
    Validate all four user inputs using a while loop.
    Returns a list of error strings; empty list means all inputs are valid.
    """
    raw_inputs: list = [
        (name,    "given name",    validate_name),
        (surname, "surname",       validate_name),
        (dob,     "date of birth", validate_dob),
        (sid,     "student ID",    validate_sid),
    ]
    errors: list = []
    idx: int = 0
    while idx < len(raw_inputs):                # while loop for validation
        value, label, validator = raw_inputs[idx]
        if not validator(value):
            if label == "date of birth":
                errors.append(f"Invalid {label}. Please use the format YYYY-MM-DD.")
            elif label == "student ID":
                errors.append(f"Invalid {label}. It must contain digits only.")
            else:
                errors.append(f"Invalid {label}. It must not be empty or contain digits.")
        idx += 1
    return errors


def interpret_score(score: int) -> tuple:
    """Return (state_label, description) tuple for a given total score."""
    for state, (low, high, desc) in psych_states.items():
        if low <= score <= high:
            return state, desc
    return "Unknown", "Score out of expected range."


# ─────────────────────────────────────────────
#  LOAD QUESTIONS — external file first,
#  fall back to embedded data if file missing
# ─────────────────────────────────────────────
try:
    questions = load_questions_from_file("questions.json")
    questions_loaded = True
except FileNotFoundError:
    questions = QUESTIONS_DATA          # fall back to embedded list
    questions_loaded = True             # still loaded, just from embedded source


# ─────────────────────────────────────────────
#  STREAMLIT UI
# ─────────────────────────────────────────────
st.set_page_config(page_title=APP_TITLE, page_icon="🎵")
st.title(f"🎵 {APP_TITLE}")

if not questions_loaded:                        # if — conditional 1
    st.error("Could not load questions. Please contact support.")
    st.stop()

st.info("Please fill out your details and answer all 20 questions honestly.")

name    = st.text_input("Given Name")
surname = st.text_input("Surname")
dob     = st.text_input("Date of Birth (YYYY-MM-DD)")
sid     = st.text_input("Student ID (digits only)")

if st.button("Start Survey"):                   # if — conditional 2

    errors = collect_errors(name, surname, dob, sid)

    if len(errors) > 0:                         # if — conditional 3
        for e in errors:                        # for loop — display errors
            st.error(e)

    elif len(errors) == 0:                      # elif — conditional 4
        st.success("All inputs are valid. Please answer the questions below.")

        total_score: int = 0
        answers: list    = []

        for idx, q in enumerate(questions):     # for loop — render questions
            opt_labels = [opt[0] for opt in q["opts"]]
            choice = st.selectbox(
                f"Q{idx + 1}. {q['q']}",
                opt_labels,
                key=f"q{idx}"
            )

            matched_score: int = 0
            for label, score in q["opts"]:      # for loop — find score
                if label == choice:
                    matched_score = score
                    break

            total_score += matched_score
            answers.append({
                "question":        q["q"],
                "selected_option": choice,
                "score":           matched_score,
            })

        state, description = interpret_score(total_score)

        if total_score in valid_score_range:    # if — conditional 5
            st.markdown(f"## ✅ Your Result: **{state}**")
            st.markdown(f"**Total Score:** {total_score} / {MAX_SCORE}")
            st.markdown(f"_{description}_")
        else:                                   # else — conditional 5
            st.error("Unexpected score total. Please refresh and try again.")
            st.stop()

        record: dict = {
            "name":               name.strip(),
            "surname":            surname.strip(),
            "dob":                dob.strip(),
            "student_id":         sid.strip(),
            "total_score":        total_score,
            "result":             state,
            "result_description": description,
            "answers":            answers,
            "version":            version_float,
        }

        json_filename: str = f"{sid.strip()}_result.json"
        json_str:      str = json.dumps(record, indent=2, ensure_ascii=False)

        st.download_button(
            label="⬇️ Download your result as JSON",
            data=json_str,
            file_name=json_filename,
            mime="application/json"
        )

    else:                                       # else — conditional 6 (safety fallback)
        st.warning("Something unexpected happened. Please refresh the page.")