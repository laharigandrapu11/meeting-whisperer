# 📝 Meeting Whisperer

An AI-powered Streamlit app that turns your meeting audio into actionable insights.

## 🔧 Features

- 🎧 **Transcribes audio** using OpenAI Whisper  
- 🧠 **Summarizes** with Claude (Anthropic)  
- 📋 **Extracts task matrix** (who-should-do-what)  
- ✅ **Auto-creates Jira tickets**  
- 🧑‍⚖️ **Flags sensitive content** & commitments  
- 💬 **Lets you ask questions** after the meeting

## 🚀 Tech Stack

- Python  
- Streamlit  
- Whisper  
- Claude API  
- Jira API  

## ⚙️ Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt```
   
2. Add your Claude API key in app.py

3. Run the app
```streamlit run app.py```

4. Jira Integration

Securely create Jira tickets from extracted tasks.

You'll need:

- Jira domain (e.g. yourteam.atlassian.net)

- Project key (e.g. ENG)

- Email & API token
