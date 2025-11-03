from dotenv import load_dotenv

load_dotenv()

from src.agent import ChatBot

agent = ChatBot()

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input.lower() in ["clear", "clean"]:
            agent.clear_memory("1")
            print("Memory cleared")
            continue

        answer = agent.invoke("1", user_input)
        
        print("Assistant:", answer['messages'][-1].content)

    except Exception as e:
        print("Something went wrong: %s", repr(e))
        break
