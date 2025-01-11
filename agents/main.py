from LLMCompiler import chain
from langchain_core.messages import HumanMessage

for step in chain.stream(
    {
        "messages": [
            HumanMessage(
                content=""
            )
        ]
    }
):
    print(step)

print(step["join"]["messages"][-1].content)