import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
from io import BytesIO
import time
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from agents.graph import app as agent_graph

# Load environment variables
load_dotenv()

# PAGE CONFIG
st.set_page_config(
    page_title="E.C.H.O. - Crisis Simulator", 
    page_icon="🚑",
    layout="wide"
)

# CUSTOM CSS FOR IMMERSIVE FEEL
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    .tension-box {
        border: 4px solid;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(255,255,255,0.1);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff6b6b 100%);
        color: white;
        font-weight: bold;
        font-size: 18px;
        padding: 15px;
        border-radius: 10px;
        border: none;
    }
    .stTextInput>div>div>input {
        background-color: #2a2a3e;
        color: white;
        border: 2px solid #ff4b4b;
        border-radius: 10px;
        padding: 15px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# SESSION STATE INITIALIZATION
if "tension" not in st.session_state:
    st.session_state.tension = 100
if "history" not in st.session_state:
    st.session_state.history = []
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "tension_history" not in st.session_state:
    st.session_state.tension_history = [100] * 20
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "scenario" not in st.session_state:
    st.session_state.scenario = "ER"

# SCENARIO CONFIGURATION
SCENARIOS = {
    "ER": {
        "name": "ER Patient (Sarah)",
        "image": "frontend/assets/er_patient.png",
        "description": "Sarah, 24, is terrified of needles and refusing IV medication.",
        "initial_tension": 90
    },
    "School": {
        "name": "Bullying Victim (Alex)",
        "image": "frontend/assets/bullying_victim.png",
        "description": "Alex is hiding in the bathroom, afraid to go to class.",
        "initial_tension": 80
    },
    "Customer": {
        "name": "Angry Customer (Karen)",
        "image": "frontend/assets/customer_service.jpg",
        "description": "Karen is furious about a cancelled flight and missing a wedding.",
        "initial_tension": 95
    }
}

# SIDEBAR - CONFIGURATION
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Scenario Selector
    selected_scenario = st.selectbox(
        "Select Scenario",
        options=list(SCENARIOS.keys()),
        format_func=lambda x: SCENARIOS[x]["name"]
    )
    
    # Reset if scenario changes
    if selected_scenario != st.session_state.scenario:
        st.session_state.scenario = selected_scenario
        st.session_state.tension = SCENARIOS[selected_scenario]["initial_tension"]
        st.session_state.history = []
        st.session_state.tension_history = [st.session_state.tension] * 20
        st.session_state.agent_logs = []
        st.session_state.turn_count = 0
        st.session_state.audio_buffer = None
        st.rerun()

    default_key = os.getenv("GOOGLE_API_KEY", "")
    api_key = st.text_input(
        "Google Gemini API Key", 
        value=default_key,
        type="password", 
        help="Get it from https://aistudio.google.com/app/apikey"
    )
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
    
    st.divider()
    st.header("🏁 Session Control")
    if st.button("End Simulation & Get Report", type="primary"):
        if st.session_state.history:
            avg_tension = sum(st.session_state.tension_history) / len(st.session_state.tension_history)
            final_tension = st.session_state.tension
            score = max(0, 100 - final_tension)
            
            st.markdown("### 📊 Performance Report")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("De-escalation Score", f"{score}/100")
            with col_b:
                st.metric("Average Tension", f"{int(avg_tension)}%")
                
            if score > 80:
                st.success("🌟 Excellent work! You kept the situation calm.")
            elif score > 50:
                st.warning("⚠️ Good effort, but try to validate feelings more.")
            else:
                st.error("🚨 The situation escalated. Try to listen more actively.")
                
            # AI Feedback (Optional - could call LLM here)
        else:
            st.warning("No interaction history yet.")

    st.divider()
    st.header("🧠 Agent Logs")
    if st.session_state.agent_logs:
        for log in st.session_state.agent_logs[-5:]:
            with st.expander(f"Turn {log['turn']}", expanded=False):
                st.json(log['data'])

# SIMULATION LOGIC USING LANGGRAPH
def run_simulation(user_input):
    if not api_key:
        st.error("⚠️ Please enter your Google Gemini API Key in the sidebar!")
        return None

    # Prepare initial state for the graph
    initial_state = {
        "messages": [m["text"] for m in st.session_state.history if m["role"] == "ai"], # Pass recent context if needed, but graph handles history mostly via prompt
        # Actually, let's pass the full history formatted for the prompt in the node
        "user_input": user_input,
        "tension": st.session_state.tension,
        "turn_count": st.session_state.turn_count,
        "scenario": st.session_state.scenario,
        "complication": "None"
    }
    
    # Pass the conversation history explicitly if the graph expects it
    # The actor node reads 'messages' from state.
    # We should populate 'messages' with the history so far.
    history_messages = []
    for msg in st.session_state.history:
        role = "User" if msg["role"] == "user" else "AI"
        history_messages.append(f"{role}: {msg['text']}")
    
    initial_state["messages"] = history_messages

    try:
        # Run the graph
        result = agent_graph.invoke(initial_state)
        
        # Update Session State from Graph Result
        st.session_state.tension = result.get("tension", st.session_state.tension)
        st.session_state.turn_count = result.get("turn_count", st.session_state.turn_count)
        ai_response = result.get("actor_response", "...")
        
        # Log analysis
        st.session_state.agent_logs.append({
            "turn": st.session_state.turn_count,
            "data": {
                "monitor_tension": result.get("tension"),
                "director_complication": result.get("complication"),
                "actor_response": ai_response
            }
        })
        
        # TTS
        try:
            tts = gTTS(text=ai_response, lang='en', slow=False)
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            st.session_state.audio_buffer = audio_fp
        except Exception as e:
            st.error(f"TTS Error: {e}")

        # Update History
        st.session_state.history.append({"role": "user", "text": user_input})
        st.session_state.history.append({
            "role": "ai", 
            "text": ai_response, 
            "tension": st.session_state.tension
        })
        
        # Update Chart History
        st.session_state.tension_history.append(st.session_state.tension)
        if len(st.session_state.tension_history) > 20:
            st.session_state.tension_history.pop(0)
            
        return result.get("complication", "None")

    except Exception as e:
        st.error(f"Simulation Error: {e}")
        return None

# MAIN LAYOUT
st.title("🚑 E.C.H.O. - Empathy & Crisis Handling Operative")
st.caption(f"Scenario: {SCENARIOS[st.session_state.scenario]['name']}")

# TENSION MONITOR
col1, col2 = st.columns([2, 1])

with col1:
    tension_color = "#ff2b2b" if st.session_state.tension > 70 else "#f7b731" if st.session_state.tension > 30 else "#00cc96"
    
    st.markdown(f"""
        <div class="tension-box" style="border-color: {tension_color};">
            <h1 style="color: {tension_color}; font-size: 80px; margin: 0;">{st.session_state.tension}%</h1>
            <p style="font-size: 24px; margin: 10px 0 0 0;">TENSION LEVEL</p>
            <p style="font-size: 14px; opacity: 0.7;">💓 Heart Rate: {60 + st.session_state.tension} BPM</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tension Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state.tension_history,
        mode='lines',
        line=dict(color=tension_color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba({int(tension_color[1:3], 16)}, {int(tension_color[3:5], 16)}, {int(tension_color[5:7], 16)}, 0.2)'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
        yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    image_path = SCENARIOS[st.session_state.scenario]["image"]
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"Image not found: {image_path}")

# SCENARIO CONTEXT
with st.expander("📋 Scenario Brief", expanded=True):
    st.write(SCENARIOS[st.session_state.scenario]["description"])

# CONVERSATION HISTORY
if st.session_state.history:
    st.subheader("💬 Conversation")
    for msg in st.session_state.history[-6:]:
        if msg['role'] == 'user':
            st.markdown(f"**🧑 You:** {msg['text']}")
        else:
            st.markdown(f"**🗣️ AI:** {msg['text']}")
            if st.session_state.audio_buffer and msg == st.session_state.history[-1]:
                st.audio(st.session_state.audio_buffer, format='audio/mp3')

# INPUT AREA
st.divider()
st.subheader("🎙️ Your Response")

# Audio Input
audio_value = st.audio_input("Record your voice")

if audio_value:
    st.info("🎧 Processing audio...")
    try:
        # Use Gemini for STT
        model = genai.GenerativeModel("gemini-1.5-flash")
        audio_bytes = audio_value.read()
        
        # Create a simple prompt for transcription
        response = model.generate_content([
            "Transcribe the following audio exactly as spoken. Do not add any commentary.",
            {"mime_type": "audio/wav", "data": audio_bytes}
        ])
        
        transcribed_text = response.text.strip()
        st.success(f"🗣️ You said: {transcribed_text}")
        
        # Auto-populate the text input or run directly
        user_text_input = transcribed_text
        
        # Optional: Auto-send if audio is detected
        if st.button("📤 Send Audio Response", key="send_audio"):
             with st.spinner("Agents are thinking..."):
                complication = run_simulation(user_text_input)
                if complication and complication != "None":
                    st.warning(f"⚠️ DIRECTOR INJECTION: {complication}")
                st.rerun()
                
    except Exception as e:
        st.error(f"STT Error: {e}")

# Text Input
user_text_input = st.text_input("Type what you would say:", placeholder="I'm here to help you...")

if st.button("📤 Send Response", use_container_width=True):
    if user_text_input:
        with st.spinner("Agents are thinking..."):
            complication = run_simulation(user_text_input)
            if complication and complication != "None":
                st.warning(f"⚠️ DIRECTOR INJECTION: {complication}")
            st.rerun()
    else:
        st.warning("Please enter a response first!")

# RESET BUTTON
if st.button("🔄 Reset Simulation", use_container_width=True):
    st.session_state.tension = SCENARIOS[st.session_state.scenario]["initial_tension"]
    st.session_state.history = []
    st.session_state.tension_history = [st.session_state.tension] * 20
    st.session_state.agent_logs = []
    st.session_state.turn_count = 0
    st.rerun()
