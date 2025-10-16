from flask import Flask, request, jsonify
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

app = Flask(__name__)

model = joblib.load('spam_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

def preprocess_text(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('portuguese'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

@app.route('/')
def home():
    return jsonify({"message": "API de Classificação de Spam", "endpoints": ["/classify (POST)"]})

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Campo 'message' é obrigatório"}), 400
    
    message = data['message']
    processed = preprocess_text(message)
    vectorized = vectorizer.transform([processed])
    prediction = model.predict(vectorized)[0]
    
    return jsonify({"message": message, "is_spam": int(prediction)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
