from agent import agent_invoke

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        answer = agent_invoke(user_input)
        print("Assistant:", answer)
    except Exception as e:
        print("Something went wrong: %s", repr(e))
        break
