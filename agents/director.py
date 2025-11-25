from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from .state import AgentState
import random

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

director_prompt = ChatPromptTemplate.from_template(
    """You are the 'Director', controlling the difficulty of a simulation.
    
    Current State:
    - Turn Count: {turn_count}
    - Tension: {tension}
    
    Logic:
    - If Turn Count is 3, inject a minor complication.
    - If Turn Count is 6, inject a major complication.
    - Otherwise, return "None".
    
    Complication Examples:
    - "A loud alarm goes off."
    - "Another nurse walks in and yells."
    - "The lights flicker."
    
    Output just the complication text or "None".
    """
)

def director_node(state: AgentState):
    turn_count = state.get('turn_count', 0) + 1
    tension = state.get('tension', 50)
    
    # Simple logic to save tokens, only call LLM on specific turns
    if turn_count not in [3, 6]:
        return {"complication": "None", "turn_count": turn_count}
        
    response = llm.invoke(director_prompt.format(
        turn_count=turn_count,
        tension=tension
    ))
    
    return {"complication": response.content, "turn_count": turn_count}
