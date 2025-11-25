from langgraph.graph import StateGraph, END
from .state import AgentState
from .actor import actor_node
from .monitor import monitor_node
from .director import director_node

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("monitor", monitor_node)
workflow.add_node("director", director_node)
workflow.add_node("actor", actor_node)

# Define edges
# 1. User Input -> Monitor (Analyze sentiment)
workflow.set_entry_point("monitor")

# 2. Monitor -> Director (Check for complications)
workflow.add_edge("monitor", "director")

# 3. Director -> Actor (Generate response based on state)
workflow.add_edge("director", "actor")

# 4. Actor -> End
workflow.add_edge("actor", END)

# Compile
app = workflow.compile()
