from agent import WorkingGraph

agent = WorkingGraph()

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input.lower() in ["clear"]:
            agent.clear_memory("1")
            print("Memory cleared")
            continue
        answer = agent.invoke("1", user_input)
        print("Assistant:", answer)
    except Exception as e:
        print("Something went wrong: %s", repr(e))
        break
