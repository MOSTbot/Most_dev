import json

with open('tgbot/json/questions.json', 'r') as file:
    questions_answers_json = json.load(file)

with open('tgbot/json/advice.json', 'r') as file:
    advice_json = json.load(file)

question_keys = questions_answers_json.keys()  # Extract question_keys from dict
advice_keys = advice_json.keys()  # Extract advise_keys from dict