# 🚑 E.C.H.O. (Empathy & Crisis Handling Operative)

> **A Voice-Powered, Audio-Immersive "Flight Simulator" for Difficult Conversations.**

E.C.H.O. is an advanced training simulation designed to help users practice de-escalation techniques in high-stakes, emotional scenarios. By placing you in a room with an AI character who is panicked, angry, or scared, E.C.H.O. tests your ability to use empathy, active listening, and calm communication to resolve crises.

---

## 🏆 The Project

This project leverages **Generative AI** and **Multi-Agent Systems** to create a dynamic, responsive roleplay partner. Unlike static chatbots, E.C.H.O. features an "invisible" Director that adjusts difficulty in real-time and a Monitor that judges your performance.

### 🌟 Key Features
- **Real-Time Tension Monitoring**: A visual gauge shows the character's stress levels, reacting instantly to your words.
- **Dynamic Complications**: The simulation throws curveballs (e.g., "A loud alarm goes off") to test your focus.
- **Immersive Audio**: Features Text-to-Speech (TTS) for the AI's responses, creating a realistic dialogue experience.
- **Multi-Scenario Support**: Practice with different archetypes, from ER patients to angry customers.

---

## 🏗️ Architecture

E.C.H.O. is built on a modular **Multi-Agent** architecture using **LangGraph**.

### 🧠 The Agents
1.  **🎭 Actor Agent (`agents/actor.py`)**
    *   **Role**: Plays the crisis character (e.g., Sarah, Alex).
    *   **Logic**: Adopts a specific persona and emotional state. Reacts to the user's input based on the current tension level and scenario context.
    *   **Model**: Google Gemini 1.5 Flash.

2.  **⚖️ Monitor Agent (`agents/monitor.py`)**
    *   **Role**: The invisible judge.
    *   **Logic**: Analyzes the user's input for empathy, aggression, or neutrality. Adjusts the "Tension" score (0-100) accordingly.
    *   **Rules**:
        *   Validation -> Lowers Tension.
        *   Aggression/Orders -> Increases Tension.

3.  **🎬 Director Agent (`agents/director.py`)**
    *   **Role**: The simulation controller.
    *   **Logic**: Monitors the turn count and tension. Injects external complications (e.g., environmental noise, interruptions) at specific turns (Turn 3 & 6) to increase difficulty.

### 🔄 The Workflow (`agents/graph.py`)
The system follows a cyclic graph:
1.  **User Input** → **Monitor** (Updates Tension)
2.  **Monitor** → **Director** (Decides on Complications)
3.  **Director** → **Actor** (Generates Response)
4.  **Actor** → **User** (Output)

---

## 📋 Scenarios

| Scenario | Character | Description | Initial Tension |
| :--- | :--- | :--- | :--- |
| **ER Patient** | Sarah | A terrified patient hyper-ventilating and refusing IV medication. | 90% |
| **School** | Alex | A bullied student hiding in the bathroom, afraid to go to class. | 80% |
| **Customer** | Karen | A furious customer whose flight was cancelled, missing a wedding. | 95% |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Google Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/echo.git
    cd echo
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup**
    *   Create a `.env` file in the root directory (optional, can also enter key in UI):
        ```env
        GOOGLE_API_KEY=your_api_key_here
        ```

### Running the App

**Option 1: Streamlit (Main Application)**
The core Python application with full agent logic.
```bash
streamlit run app.py
```

**Option 2: Web Frontend (Alternative)**
A lightweight HTML/JS version located in the `frontend/` folder.
```bash
cd frontend
# Open index.html directly or serve it
python -m http.server 8000
```

---

## 📂 Project Structure

```text
E.C.H.O/
├── agents/             # Logic for AI Agents
│   ├── actor.py        # Roleplay agent
│   ├── director.py     # Difficulty controller
│   ├── monitor.py      # Sentiment/Tension analyzer
│   ├── graph.py        # LangGraph workflow definition
│   └── state.py        # State schema
├── frontend/           # Alternative Web Interface
│   ├── assets/         # Images and icons
│   ├── index.html      # Web entry point

## 🔮 Future Roadmap

We are actively working on making E.C.H.O. a competition-ready platform. Planned upgrades include:

### 🚀 Features
-   **📈 Emotion Curve Timeline**: Visual graph showing tension changes over time.
-   **🎙️ Voice Input (STT)**: Talk directly to the character using Whisper or Gemini Audio.
-   **🗣️ Emotion-Aware TTS**: AI voice that changes tone (angry, calm, shaky) based on tension.
-   **🧠 AI Personality Memory**: Characters remember past interactions and have deep backstories.
-   **📊 Scoring & Debriefing**: Post-simulation analysis with Empathy and De-escalation scores.

### 🎮 Gamification & Immersion
-   **🔀 Branching Difficulty**: Dynamic difficulty scaling based on user performance.
-   **🔊 Real-Time Audio Effects**: Background sounds (hospital alarms, school bells) triggered by the Director.
-   **💓 Motion Visualizer**: Pulsing visual elements reacting to stress levels.
-   **🏆 Leaderboard & XP**: Gamified progression system.

### 🛠️ Technical
-   **🛡️ Safety Boundary Detection**: Automated flagging of aggressive or harmful language.
-   **💾 Replay Mode**: Export full conversation logs and analysis as PDF.
-   **🥽 VR Mode**: Experimental WebXR support for full immersion.

