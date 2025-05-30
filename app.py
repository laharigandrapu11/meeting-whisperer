import streamlit as st
import whisper
import tempfile
import requests

# --- Config ---
TOGETHER_API_KEY = st.secrets.get("TOGETHER_API_KEY")  # Set in .streamlit/secrets.toml
MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# --- Functions ---
def transcribe_audio(uploaded_file):
    model = whisper.load_model("base")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    result = model.transcribe(tmp_path)
    return result["text"]

def summarize_transcript(transcript):
    prompt = f"""
You are an AI assistant. Please summarize the following meeting transcript and extract any action items or key decisions discussed.

Transcript:
{transcript[:5000]}
"""
    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={"Authorization": f"Bearer {TOGETHER_API_KEY}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    output = response.json()["choices"][0]["message"]["content"]
    if "Action Items:" in output:
        summary, todos = output.split("Action Items:", 1)
        todos = "Action Items:" + todos
    else:
        summary, todos = output, "❌ No action items identified."
    return summary.strip(), todos.strip()

def ask_question_about_meeting(question, transcript):
    prompt = f"""
You are an assistant helping summarize and analyze meetings. Answer the following question based on this transcript:

Transcript: {transcript[:5000]}

Question: {question}
"""
    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={"Authorization": f"Bearer {TOGETHER_API_KEY}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# --- Streamlit UI ---
st.set_page_config(page_title="Meeting Whisperer", layout="centered")
st.title("🧠 Meeting Whisperer")
st.markdown("Upload your meeting recording. Get a summary, action items, and ask questions!")

uploaded_file = st.file_uploader("Upload Zoom file (.mp3/.mp4/.m4a)", type=["mp3", "mp4", "m4a"])

if uploaded_file:
    with st.spinner("🔊 Transcribing audio..."):
        transcript = transcribe_audio(uploaded_file)
    st.success("✅ Transcription complete!")
    st.text_area("📝 Transcript Preview", transcript[:1500] + "...", height=200)

    with st.spinner("🧠 Generating summary and action items..."):
        summary, action_items = summarize_transcript(transcript)
    st.subheader("📋 Summary")
    st.markdown(summary)
    st.subheader("✅ Action Items")
    st.markdown(action_items)

    st.markdown("---")
    st.subheader("💬 Ask a question about the meeting")
    question = st.text_input("Enter your question")
    if question:
        with st.spinner("🤖 Thinking..."):
            answer = ask_question_about_meeting(question, transcript)
        st.markdown(f"**❓ {question}**")
        st.markdown(f"**➡️ {answer}**")
