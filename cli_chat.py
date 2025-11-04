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

                if '__interrupt__' in answer:
                    print("Interrapt:", answer['__interrupt__'])
                    
                    user_decision = input("Decision (yes/no): ")
                    match user_decision.lower():
                        case "a" | "approve" | "y" | "yes":
                            answer = agent.approve_action("1", "approve")
                        case "r" | "reject" | "no" | "n":
                            answer = agent.approve_action("1", "reject")
                    pass

                print("Assistant:", answer['messages'][-1].content)

    except Exception as e:
        print("Something went wrong: %s", repr(e))
        break
