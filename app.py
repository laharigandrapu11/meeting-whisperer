import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import requests

# --- Config ---
TOGETHER_API_KEY = st.secrets.get("TOGETHER_API_KEY")
MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# --- Functions ---
def transcribe_audio(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    model = WhisperModel("base", compute_type="float32")
    segments, _ = model.transcribe(tmp_path)

    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
    return transcript.strip()


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

    try:
        result = response.json()
        if "choices" not in result:
            st.error("❌ API call failed. Check your Together.ai key or rate limits.")
            st.text(result)  # Optional: debug the raw response
            return "Summary unavailable.", "No action items extracted."
        
        output = result["choices"][0]["message"]["content"]
        if "Action Items:" in output:
            summary, todos = output.split("Action Items:", 1)
            todos = "Action Items:" + todos
        else:
            summary, todos = output, "❌ No action items identified."

        return summary.strip(), todos.strip()
    
    except Exception as e:
        st.error("❌ An unexpected error occurred while summarizing.")
        st.exception(e)
        return "Summary failed.", "Action item extraction failed."


def ask_question_about_meeting(question, transcript):
    prompt = f"""
You are an assistant helping summarize and analyze meetings. Answer the following question based on this transcript:

Transcript: {transcript[:5000]}

Question: {question}
"""
    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={"Authorization": f"Bearer {TOGETHER_API_KEY}"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        result = response.json()
        if "choices" not in result:
            st.error("❌ Q&A failed. API returned an error.")
            st.text(result)
            return "Unable to answer the question."

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        st.error("❌ An error occurred during Q&A.")
        st.exception(e)
        return "Error answering question."


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
