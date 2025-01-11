from LLMCompiler import chain
from langchain_core.messages import HumanMessage

for step in chain.stream(
    {
        "messages": [
            HumanMessage(
                content="create a file called test.txt with the content 'Hello, World!'"
            )
        ]
    }
):
    print(step)

print(step["join"]["messages"][-1].content)