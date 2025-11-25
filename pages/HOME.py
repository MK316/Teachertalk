import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.set_page_config(page_title="Classroom English Expressions", layout="centered")

st.title("Classroom English Expressions for Future English Teachers")

st.write(
    "Choose a classroom situation on the left, read useful expressions, "
    "and listen to the audio to prepare for your 20-minute English teaching demo."
)

# --------------------------------
# 1. Load CSV (from local file or GitHub)
# --------------------------------
@st.cache_data
def load_expressions_from_csv(path: str) -> pd.DataFrame:
    """
    CSV format:
    Opening, Giving feedback, Closing
    (each row contains one expression in each column, empty cells are allowed)
    """
    df = pd.read_csv(path)
    return df


# 여기서는 로컬 CSV 파일 이름을 가정합니다.
# 나중에 GitHub raw 링크를 쓰고 싶으면 아래 한 줄만 바꾸면 됩니다.
# 예: df = load_expressions_from_csv("https://raw.githubusercontent.com/...")
CSV_PATH = "classroom_expressions.csv"

try:
    df = load_expressions_from_csv(CSV_PATH)
except Exception:
    # CSV가 아직 없을 때를 대비해서, 빈 DataFrame으로 초기화
    df = pd.DataFrame(columns=["Opening", "Giving feedback", "Closing"])


# --------------------------------
# 2. Sidebar – 상황 선택 + 샘플 CSV 다운로드
# --------------------------------
st.sidebar.header("Classroom situation")

situations = ["Opening", "Giving feedback", "Closing"]
selected_situation = st.sidebar.radio("Choose a situation", situations)

st.sidebar.markdown("---")
st.sidebar.subheader("Sample data")

st.sidebar.write(
    "You can download a sample CSV file with five example expressions "
    "for each situation."
)


# 샘플 CSV 생성 함수
def get_sample_csv_bytes() -> bytes:
    sample_data = {
        "Opening": [
            "Good morning, everyone. Today we’re going to learn about reported speech.",
            "Let’s get started. Last time we looked at phrasal verbs.",
            "Before we begin, does everyone remember yesterday’s homework?",
            "Today’s goal is to practice speaking in pairs.",
            "By the end of this lesson, you will be able to use conditionals in real situations.",
        ],
        "Giving feedback": [
            "That’s a great idea. Can you say that one more time?",
            "Almost right. Let’s think about the verb tense here.",
            "I like how you used that word in your sentence.",
            "Turn to your partner and compare your answers together.",
            "Let’s check together. Who has a different answer?",
        ],
        "Closing": [
            "Before we finish, let’s quickly review what we learned today.",
            "For homework, please write five sentences using today’s expressions.",
            "Any questions before we wrap up?",
            "You did a nice job today. Thank you for your hard work.",
            "See you next time. Have a good day, everyone.",
        ],
    }

    sample_df = pd.DataFrame(sample_data)
    csv_bytes = sample_df.to_csv(index=False).encode("utf-8-sig")
    return csv_bytes


sample_csv_bytes = get_sample_csv_bytes()

st.sidebar.download_button(
    label="Download sample CSV",
    data=sample_csv_bytes,
    file_name="classroom_expressions_sample.csv",
    mime="text/csv",
)


# --------------------------------
# 3. 선택된 상황에 맞는 표현 목록 만들기
# --------------------------------
# df가 비어 있으면 샘플 데이터로 대체할 수 있도록 옵션
if df.empty:
    st.warning(
        "No CSV file found. Using built-in sample data instead. "
        "You can download the sample CSV from the left sidebar."
    )
    df = pd.read_csv(io.BytesIO(sample_csv_bytes))


# 선택된 상황에 해당하는 컬럼명과 Series 추출
col_name = selected_situation
if col_name not in df.columns:
    st.error(f"Column '{col_name}' not found in CSV file.")
    st.stop()

expressions = df[col_name].dropna().tolist()

if not expressions:
    st.warning(f"No expressions found in column '{col_name}'.")
    st.stop()

st.markdown(f"### Situation: {selected_situation}")

selected_expression = st.selectbox(
    "Choose an expression to practice:",
    expressions,
    index=0,
)

st.markdown("#### Selected expression")
st.markdown(f"> {selected_expression}")


# --------------------------------
# 4. TTS로 오디오 생성 & 재생
# --------------------------------
def text_to_speech_bytes(text: str, lang: str = "en") -> bytes:
    """
    Generate TTS audio from text using gTTS and return as bytes.
    """
    tts = gTTS(text=text, lang=lang)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()


st.markdown("#### Listen and repeat")

# 버튼을 눌렀을 때만 TTS 생성 (불필요한 반복 호출 감소)
if st.button("Generate & play audio"):
    with st.spinner("Generating audio..."):
        try:
            audio_bytes = text_to_speech_bytes(selected_expression, lang="en")
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"Error generating audio: {e}")
else:
    st.info("Click the button above to generate audio for this expression.")
