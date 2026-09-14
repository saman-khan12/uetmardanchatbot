"""Terminal chat over the same rag.py logic the web UI uses."""

from rag import answer_question

if __name__ == "__main__":
    print("UET Mardan Assistant (type 'exit' to quit)\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        answer, sources = answer_question(question)
        print(f"\nBot: {answer}\n")
        if sources:
            print("Sources:")
            for s in sources:
                print(f"  - {s}")
        print()