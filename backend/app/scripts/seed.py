from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.crud import content
from app.models.exercise import Exercise
from app.models.passage import Passage
from app.models.sentence import Sentence
from app.models.word import Word


def seed_words(db: Session) -> None:
    items = [
        {
            "text": "gratitude",
            "meaning": "the quality of being thankful; readiness to show appreciation",
            "example": "She expressed gratitude for the support.",
            "audio_url": "https://example.com/audio/gratitude.mp3",
            "image_url": "https://example.com/images/gratitude.jpg",
            "level": "A2",
            "tags": ["emotion", "attitude"],
        },
        {
            "text": "efficient",
            "meaning": "achieving maximum productivity with minimum effort or waste",
            "example": "We need a more efficient workflow.",
            "audio_url": "https://example.com/audio/efficient.mp3",
            "image_url": "https://example.com/images/efficient.jpg",
            "level": "B1",
            "tags": ["work", "technology"],
        },
        {
            "text": "persist",
            "meaning": "to continue firmly or obstinately in an opinion or a course of action",
            "example": "He persisted despite setbacks.",
            "audio_url": "https://example.com/audio/persist.mp3",
            "image_url": "https://example.com/images/persist.jpg",
            "level": "B2",
            "tags": ["behavior", "learning"],
        },
        {
            "text": "innovate",
            "meaning": "to make changes in something established, introducing new methods",
            "example": "Small teams can innovate quickly.",
            "audio_url": "https://example.com/audio/innovate.mp3",
            "image_url": "https://example.com/images/innovate.jpg",
            "level": "B2",
            "tags": ["technology", "work"],
        },
        {
            "text": "clarity",
            "meaning": "the quality of being coherent and intelligible",
            "example": "Clear goals bring clarity to the team.",
            "audio_url": "https://example.com/audio/clarity.mp3",
            "image_url": "https://example.com/images/clarity.jpg",
            "level": "A2",
            "tags": ["communication", "learning"],
        },
    ]

    for item in items:
        exists = db.query(Word).filter(Word.text == item["text"]).first()
        if exists is None:
            content.create_word(db, item)


def seed_sentences(db: Session) -> None:
    items = [
        {
            "text": "The train arrives at 8:30 every morning.",
            "meaning": "The train comes at the same time each morning.",
            "audio_url": "https://example.com/audio/train_arrives.mp3",
            "image_url": "https://example.com/images/train.jpg",
            "level": "A1",
            "tags": ["travel", "routine"],
        },
        {
            "text": "Please upload your assignment before midnight.",
            "meaning": "You should submit your assignment before 12:00 AM.",
            "audio_url": "https://example.com/audio/assignment.mp3",
            "image_url": "https://example.com/images/assignment.jpg",
            "level": "A2",
            "tags": ["school", "deadline"],
        },
        {
            "text": "We discussed several options and chose the safest one.",
            "meaning": "After considering different choices, we selected the safest.",
            "audio_url": "https://example.com/audio/options.mp3",
            "image_url": "https://example.com/images/options.jpg",
            "level": "B1",
            "tags": ["decision", "work"],
        },
    ]

    for item in items:
        exists = db.query(Sentence).filter(Sentence.text == item["text"]).first()
        if exists is None:
            content.create_sentence(db, item)


def seed_passages(db: Session) -> None:
    items = [
        {
            "title": "A Morning Routine",
            "content": (
                "Lena wakes up at 6:30 and makes a cup of tea. "
                "She reads the news for ten minutes and then prepares breakfast. "
                "By 7:30, she is ready to leave for work."
            ),
            "summary": "A short description of a daily morning routine.",
            "audio_url": "https://example.com/audio/morning_routine.mp3",
            "image_url": "https://example.com/images/morning.jpg",
            "level": "A2",
            "tags": ["routine", "lifestyle"],
        },
        {
            "title": "Learning in Small Steps",
            "content": (
                "Learning a language takes time, but small steps add up. "
                "If you practice a little each day, your confidence grows. "
                "Consistency matters more than intensity."
            ),
            "summary": "Small daily practice builds confidence over time.",
            "audio_url": "https://example.com/audio/small_steps.mp3",
            "image_url": "https://example.com/images/learning.jpg",
            "level": "B1",
            "tags": ["learning", "motivation"],
        },
    ]

    for item in items:
        exists = db.query(Passage).filter(Passage.title == item["title"]).first()
        if exists is None:
            content.create_passage(db, item)


def seed_exercises(db: Session) -> None:
    items = [
        {
            "exercise_type": "image_choice",
            "prompt": "Choose the image that matches the word: gratitude",
            "options": [
                "https://example.com/images/gratitude.jpg",
                "https://example.com/images/traffic.jpg",
                "https://example.com/images/desk.jpg",
            ],
            "answer": "https://example.com/images/gratitude.jpg",
            "explanation": "Gratitude relates to appreciation and thankfulness.",
            "level": "A2",
            "tags": ["vocabulary", "image"],
        },
        {
            "exercise_type": "listening_choice",
            "prompt": "Listen to the audio and choose the correct sentence.",
            "options": [
                "The train arrives at 8:30 every morning.",
                "The train leaves at 9:30 every evening.",
                "The bus arrives at 8:30 every morning.",
            ],
            "answer": "The train arrives at 8:30 every morning.",
            "explanation": "The audio matches the sentence about the train arrival time.",
            "level": "A1",
            "tags": ["listening", "choice"],
        },
        {
            "exercise_type": "sentence_order",
            "prompt": "Reorder the words to form a correct sentence.",
            "options": ["morning", "every", "arrives", "train", "the", "at", "8:30"],
            "answer": "the train arrives at 8:30 every morning",
            "explanation": "Standard word order: subject + verb + time expression.",
            "level": "A1",
            "tags": ["grammar", "order"],
        },
        {
            "exercise_type": "cloze",
            "prompt": "Complete the sentence: We need a more ____ workflow.",
            "options": ["efficient", "fragile", "silent", "distant"],
            "answer": "efficient",
            "explanation": "Efficient means productive with minimal waste.",
            "level": "B1",
            "tags": ["vocabulary", "cloze"],
        },
    ]

    for item in items:
        exists = (
            db.query(Exercise)
            .filter(Exercise.exercise_type == item["exercise_type"])
            .filter(Exercise.prompt == item["prompt"])
            .first()
        )
        if exists is None:
            content.create_exercise(db, item)


def run_seed() -> None:
    db = SessionLocal()
    try:
        seed_words(db)
        seed_sentences(db)
        seed_passages(db)
        seed_exercises(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
