positive = ["good", "excellent", "great"]
negative = ["bad", "failure", "poor"]

def process_sentence(sentence):
    words = sentence.lower().split()
    score = sum(word in positive for word in words) - \
            sum(word in negative for word in words)

    return f"{sentence} | Score: {score}"