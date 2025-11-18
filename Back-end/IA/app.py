from flask import Flask, request, jsonify
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

app = Flask(__name__)
# -----------------------------------------------------------------------------
# API de classificação de spam
# Este arquivo expõe um serviço Flask simples com duas rotas:
# - '/' para verificar se a API está disponível
# - '/classify' para classificar uma mensagem como spam (POST JSON com campo 'message')
#
# Observações importantes:
# - Os modelos `spam_model.pkl` e `vectorizer.pkl` são carregados do disco com joblib.
# - Os recursos do NLTK (stopwords, punkt) estão sendo baixados em tempo de execução;
#   em produção é recomendado pré-baixar esses recursos e remover os downloads do app.
# - Os comentários abaixo explicam os passos de pré-processamento e a entrada/saída das rotas.
# -----------------------------------------------------------------------------

# Carrega o modelo e o `vectorizer` previamente treinados com joblib.
# Espera-se que os arquivos `spam_model.pkl` e `vectorizer.pkl` existam na mesma pasta.
model = joblib.load('spam_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Faz o download dos recursos do NLTK necessários para tokenização e stopwords.
# Nota: o `punkt_tab` não é um recurso NLTK padrão (verificar se é necessário).
# Em servidores de produção, prefira baixar recursos em uma etapa de build/instalação
# para evitar downloads repetidos a cada inicialização do serviço.
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

def preprocess_text(text):
    """
    Pré-processamento da mensagem de entrada.

    Etapas realizadas:
    1. Remove pontuação (ex.: ?, !, .) usando translate.
    2. Converte o texto para minúsculas (normalização).
    3. Tokeniza o texto em palavras com `word_tokenize`.
    4. Remove stopwords em Português usando o corpus do NLTK.

    Retorna uma string com tokens separados por espaço, pronta para vetorização.
    """
    # Remove pontuação para evitar tokens com sinais
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('portuguese'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

@app.route('/')
def home():
    # Rota de sanity-check para verificar se a API está ativa.
    # Retorna uma mensagem simples com os endpoints disponíveis.
    return jsonify({"message": "API de Classificação de Spam", "endpoints": ["/classify (POST)"]})

@app.route('/classify', methods=['POST'])
def classify():
    # Recebe JSON com o campo `message` via POST. Exemplo:
    # {"message": "Texto a ser classificado"}
    data = request.get_json()
    if not data or 'message' not in data:
        # Se o JSON estiver ausente ou o campo 'message' não for enviado,
        # retornamos HTTP 400 com uma mensagem de erro.
        return jsonify({"error": "Campo 'message' é obrigatório"}), 400
    
    message = data['message']
    processed = preprocess_text(message)
    vectorized = vectorizer.transform([processed])
    prediction = model.predict(vectorized)[0]
    
    # `prediction` vem do modelo treinado (por exemplo, 1 = spam, 0 = ham/not spam)
    # Convertendo para int para garantir compatibilidade JSON (numpy types causam erro)
    return jsonify({"message": message, "is_spam": int(prediction)})

if __name__ == '__main__':
    # Executa o app Flask. Em produção, prefira usar um servidor WSGI (gunicorn/uwsgi)
    # e desabilitar debug.
    app.run(host='0.0.0.0', port=5000, debug=True)
