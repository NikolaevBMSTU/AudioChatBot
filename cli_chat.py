from dotenv import load_dotenv

load_dotenv()

from src.agent import ChatBot

agent = ChatBot()

while True:
    try:
        user_input = input("User: ")
        match user_input.lower():
            case "quit" | "exit" | "q":
                print("Goodbye!")
                break
            case "clear" | "clean":
                agent.clear_memory("1")
                print("Memory cleared")
                continue
            case _:
                answer = agent.invoke("1", user_input)
                print("Assistant:", answer['messages'][-1].content)

    except Exception as e:
        print("Something went wrong: %s", repr(e))
        break
