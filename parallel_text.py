import re
import sqlite3
from multiprocessing import Pool, cpu_count

positive = ["good", "excellent", "great"]
negative = ["bad", "failure", "poor"]

def process_sentence(sentence):
    words = sentence.lower().split()
    score = sum(word in positive for word in words) - \
            sum(word in negative for word in words)
    return sentence, score

def main():
    with open("sample.txt", "r") as file:
        text = file.read()

    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    with Pool(cpu_count()) as pool:
        results = pool.map(process_sentence, sentences)

    # Save to database
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY,
            sentence TEXT,
            score INTEGER
        )
    """)

    for sentence, score in results:
        cursor.execute(
            "INSERT INTO texts (sentence, score) VALUES (?, ?)",
            (sentence, score)
        )

    conn.commit()
    conn.close()

    for r in results:
        print(r)

# VERY IMPORTANT
if __name__ == "__main__":
    main()
