from LLMCompiler import chain
from langchain_core.messages import HumanMessage


for step in chain.stream(
    {
        "messages": [
            HumanMessage(content="search for the whisper github repo and clone it in current directory")
        ]
    }
):
    print(step)

# Print the last part of the result
print(step["join"]["messages"][-1].content)