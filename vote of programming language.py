votes = {
    "Python": 0,
    "Java":0,
    "C++":0
}

n = int(input("Enter number of votes: "))
for i in range(n):
    vote = input("Vote for Python / Java / C++: ")
    
    if vote in votes:
        votes[vote] += 1
    else:
        print("Invalid Vote")
print("Voting Result: ", votes)

winner = max(votes, key=votes.get)
print("Winner: ", winner)