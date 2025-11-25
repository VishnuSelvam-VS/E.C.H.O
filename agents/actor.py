from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from .state import AgentState

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

scenarios = {
    "ER": """You are 'Sarah', a terrified patient in a hospital ER.
             - Context: You are hyper-ventilating. You believe the medicine is poison.
             - Behavior: Interrupt often. Scream if angry. Calm down only if validated.""",
    "School": """You are 'Alex', a student who is being bullied.
                 - Context: You are hiding in the bathroom. You are afraid to go to class.
                 - Behavior: Whisper. Cry. Refuse to open the door unless you feel safe.""",
    "Customer": """You are 'Karen', a furious customer whose flight was cancelled.
                   - Context: You are missing your daughter's wedding.
                   - Behavior: Yell. Demand a manager. Insult the user. Calm down if offered a solution AND empathy."""
}

actor_prompt = ChatPromptTemplate.from_template(
    """Roleplay Instructions:
    {scenario_description}
    
    Current State:
    - Tension Level: {tension}/100
    - Complication: {complication}
    
    Conversation History:
    {history}
    
    User just said: "{user_input}"
    
    Respond as the character. Keep it short (1-2 sentences). Act out the emotion.
    """
)

def actor_node(state: AgentState):
    messages = state.get('messages', [])
    history = "\n".join(messages[-5:])
    scenario_key = state.get('scenario', 'ER')
    scenario_desc = scenarios.get(scenario_key, scenarios['ER'])
    
    response = llm.invoke(actor_prompt.format(
        scenario_description=scenario_desc,
        tension=state['tension'],
        complication=state.get('complication', "None"),
        history=history,
        user_input=state['user_input']
    ))
    
    return {"actor_response": response.content, "messages": [f"AI: {response.content}"]}
