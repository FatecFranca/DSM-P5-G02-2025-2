import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Baixar stopwords se necessário
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

# Função para pré-processar texto
def preprocess_text(text):
    # Remover pontuação
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Lowercase
    text = text.lower()
    # Tokenizar
    tokens = word_tokenize(text)
    # Remover stopwords
    stop_words = set(stopwords.words('portuguese'))
    tokens = [word for word in tokens if word not in stop_words]
    # Juntar novamente
    return ' '.join(tokens)

# Ler dataset
df = pd.read_csv('spam_dataset.csv')

# Aplicar pré-processamento
df['mensagem_processada'] = df['mensagem'].apply(preprocess_text)

# Separar features e labels
X = df['mensagem_processada']
y = df['spam']

# Dividir em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorizar
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Treinar modelo
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Avaliar
y_pred = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred)
print(f'Acurácia: {accuracy:.2f}')

# Salvar modelo e vectorizer
joblib.dump(model, 'spam_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print('Modelo treinado e salvo!')