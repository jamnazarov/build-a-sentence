import json
import logging
from flask import Flask, render_template, request
from googletrans import Translator
import google.generativeai as genai

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
translator = Translator()

data = []  # Локальный список для хранения данных

GEMINI_API_KEY = "AIzaSyDOprSzbCATJhoBqIga96Ku9l83mNa4Rtc"  # Вставь свой ключ сюда
genai.configure(api_key=GEMINI_API_KEY)

JSON_FILE = "sentences.json"

# Загружаем данные из JSON при старте сервера
def load_data():
    global data
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        logging.info("Данные загружены из JSON")
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning("Файл JSON не найден или пуст. Создаём новый.")
        data = []
        save_data()  # Создаём пустой файл

# Сохраняем данные в JSON
def save_data():
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logging.info("Данные сохранены в JSON")
    except Exception as e:
        logging.error(f"Ошибка сохранения в JSON: {e}")

# Функция генерации предложения
def generate_sentence(words):
    try:
        prompt = f"Составь осмысленное английское предложение, используя эти слова: {', '.join(words)}"
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        sentence = response.text.strip() if response and response.text else "Ошибка генерации."
        logging.info(f"Generated sentence: {sentence}")  # Логирование результата
        return sentence
    except Exception as e:
        logging.error(f"Ошибка генерации предложения: {e}")
        return "Ошибка генерации."

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/generate', methods=['POST'])
def generate():
    words = request.form.get('words', '').split(',')
    words = [word.strip() for word in words if word.strip()]
    if not words:
        return "<tr><td colspan='3'>Введите слова!</td></tr>"

    sentence = generate_sentence(words)

    # Переводим предложение на русский
    try:
        translation = translator.translate(sentence, src='en', dest='ru').text
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        translation = "Ошибка перевода."

    # Создаём объект данных
    entry = {"words": ', '.join(words), "sentence": sentence, "translation": translation}
    data.append(entry)

    # Сохраняем в JSON
    save_data()

    return f"""
    <tr>
        <td>{entry['words']}</td>
        <td>{entry['sentence']}</td>
        <td>{entry['translation']}</td>
    </tr>
    """

if __name__ == '__main__':
    load_data()  # Загружаем старые данные перед стартом сервера
    app.run(debug=True)
