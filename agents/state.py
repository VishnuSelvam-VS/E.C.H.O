from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    user_input: str
    actor_response: str
    tension: int
    heart_rate: int
    complication: str
    turn_count: int
    scenario: str
