questions = [
    {
        "question": "Which symbol is used for List?",
        "answer": "[]"
    },
    {
        "question": "Which Keyword is used for loop?",
        "answer": "for"
    },
    {
        "question": "Which function displays outputs?",
        "answer": "print"
    }
]

score = 0
for q in questions:
    print(q["question"])
    ans = input("Enter answer: ")
    if ans == q["answer"]:
        print("Correct")
        score += 1
    else:
        print("Wrong")

print("FinalScore: ", score, "/", len(questions))