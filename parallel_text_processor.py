import os
import re
import csv
import sqlite3
from datetime import datetime
from multiprocessing import Pool, cpu_count
import smtplib
from email.message import EmailMessage

# ===============================
# CONFIGURATION
# ===============================

DATABASE_NAME = "text_processor.db"

positive_words = ["good", "excellent", "happy", "success", "great", "positive"]
negative_words = ["bad", "terrible", "sad", "failure", "poor", "negative"]

pattern_keywords = ["error", "warning", "critical"]

# ===============================
# DATABASE SETUP
# ===============================

def init_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_chunk TEXT,
            sentiment_score INTEGER,
            tags TEXT,
            timestamp TEXT
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_score ON texts(sentiment_score)")
    conn.commit()
    conn.close()


# ===============================
# TEXT CHUNKING
# ===============================

def chunk_text(text):
    # Split by sentence
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]


# ===============================
# SENTIMENT + PATTERN PROCESSOR
# ===============================

def process_chunk(text_chunk):
    words = text_chunk.lower().split()

    positive_count = sum(word in positive_words for word in words)
    negative_count = sum(word in negative_words for word in words)

    score = positive_count - negative_count

    tags_found = []
    for pattern in pattern_keywords:
        if re.search(rf"\b{pattern}\b", text_chunk.lower()):
            tags_found.append(pattern)

    return (text_chunk, score, ",".join(tags_found))


# ===============================
# SAVE TO DATABASE
# ===============================

def save_results(results):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    for text_chunk, score, tags in results:
        cursor.execute("""
            INSERT INTO texts (text_chunk, sentiment_score, tags, timestamp)
            VALUES (?, ?, ?, ?)
        """, (text_chunk, score, tags, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


# ===============================
# PARALLEL PROCESSING
# ===============================

def parallel_process(text_chunks):
    with Pool(cpu_count()) as pool:
        results = pool.map(process_chunk, text_chunks)
    return results


# ===============================
# SEARCH FUNCTION
# ===============================

def search_text(keyword=None, min_score=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    query = "SELECT * FROM texts WHERE 1=1"
    params = []

    if keyword:
        query += " AND text_chunk LIKE ?"
        params.append(f"%{keyword}%")

    if min_score is not None:
        query += " AND sentiment_score >= ?"
        params.append(min_score)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results


# ===============================
# EXPORT TO CSV
# ===============================

def export_to_csv(filename="output.csv"):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM texts")
    rows = cursor.fetchall()

    conn.close()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Text Chunk", "Sentiment Score", "Tags", "Timestamp"])
        writer.writerows(rows)

    print(f"CSV exported successfully to {filename}")


# ===============================
# EMAIL REPORT
# ===============================

def send_email_report(sender_email, sender_password, receiver_email, attachment_file):
    msg = EmailMessage()
    msg["Subject"] = "Text Processing Report"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Attached is your text processing report.")

    with open(attachment_file, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_file)

    msg.add_attachment(file_data, maintype="application",
                       subtype="octet-stream", filename=file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

    print("Email sent successfully!")


# ===============================
# MAIN EXECUTION
# ===============================

def main():
    init_database()

    file_path = input("Enter text file path: ")

    if not os.path.exists(file_path):
        print("File not found!")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    print("Chunking text...")
    chunks = chunk_text(text)

    print("Processing in parallel...")
    results = parallel_process(chunks)

    print("Saving to database...")
    save_results(results)

    print("Processing completed successfully!")


if __name__ == "__main__":
    main()
