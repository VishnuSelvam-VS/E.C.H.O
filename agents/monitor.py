from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from .state import AgentState

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

monitor_prompt = ChatPromptTemplate.from_template(
    """You are the 'Monitor Agent', an invisible judge of a crisis negotiation simulation.
    
    Your Job: Analyze the User's input and determine if it De-escalates or Escalates the situation.
    
    Current Tension: {current_tension}
    
    User Input: "{user_input}"
    
    Rules:
    - If User validates feelings ("I see you're scared"), Tension -10.
    - If User gives orders ("Calm down"), Tension +15.
    - If User is neutral, Tension +0.
    - If User is aggressive, Tension +20.
    
    Output JSON ONLY:
    {{
        "tension_change": int,
        "reasoning": "string",
        "new_tension": int (0-100)
    }}
    """
)

def monitor_node(state: AgentState):
    current_tension = state.get('tension', 50)
    user_input = state.get('user_input', "")
    
    try:
        chain = monitor_prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "current_tension": current_tension,
            "user_input": user_input
        })
        
        new_tension = max(0, min(100, result['new_tension']))
        
        return {
            "tension": new_tension, 
            "heart_rate": 60 + new_tension  # Simple mapping
        }
    except Exception as e:
        print(f"Monitor Error: {e}")
        return {"tension": current_tension}
