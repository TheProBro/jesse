# from LLMCompiler import chain
# from langchain_core.messages import HumanMessage
import time
import sys
import queue
sys.path.append('../')

import shared_queue1

# for step in chain.stream(
#     {
#         "messages": [
#             HumanMessage(
#                 content="create a file called test.txt with the content 'Hello, World!'"
#             )
#         ]
#     }
# ):
#     print(step)

# print(step["join"]["messages"][-1].content)

def send_text_to_chain():
    while True:
        try:
            print(f"Queue size: {shared_queue1.shared_queue.qsize()}")

            recognized_text = shared_queue1.shared_queue.get(timeout=2)  # Get the recognized speech text

            # # Process the text with your main chain code
            # for step in chain.stream(
            #     {
            #         "messages": [
            #             HumanMessage(content=recognized_text)
            #         ]
            #     }
            # ):
            #     print(step)

            # # Print the last part of the result
            # print(step["join"]["messages"][-1].content)
            print(recognized_text)
        except queue.Empty:
            # Queue is empty, print a message and wait a bit before checking again
            print("Queue is empty. Waiting for new items...")
            time.sleep(1)  # Adjust this to control the delay between retries

        except Exception as e:
            # Catch any other exceptions and log them
            print(f"Error occurred: {e}")
            time.sleep(1)

# Start processing text
send_text_to_chain()
