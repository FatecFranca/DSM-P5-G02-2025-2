import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
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

# -----------------------------------------------------------------------------
# Treino e avaliação comparativa (testando opções diferentes)
# Testamos combinações de vetorizadores e classificadores; escolhemos e exportamos
# o melhor modelo segundo o F1-score no conjunto de teste.
# -----------------------------------------------------------------------------

# Definir vetorizadores e classificadores candidatos
vectorizers = {
    'tfidf_1': TfidfVectorizer(ngram_range=(1, 1)),
    'tfidf_12': TfidfVectorizer(ngram_range=(1, 2)),
    'count_1': CountVectorizer(ngram_range=(1, 1))
}

classifiers = {
    'MultinomialNB': MultinomialNB(),
    'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
    'LinearSVC': LinearSVC(random_state=42),
    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42)
}

best_score = -1
best_model = None
best_vectorizer = None
best_combo = None

# Pequena função auxiliar para avaliar modelos
def evaluate_model(model, Xv_test, y_test):
    y_pred = model.predict(Xv_test)
    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0)
    }

print('Iniciando avaliação de combinações...')
for vname, vect in vectorizers.items():
    # Fit no X_train
    X_train_v = vect.fit_transform(X_train)
    X_test_v = vect.transform(X_test)

    for cname, clf in classifiers.items():
        # Treinar classifier
        clf.fit(X_train_v, y_train)

        # Avaliar no conjunto de teste
        scores = evaluate_model(clf, X_test_v, y_test)
        print(f"{vname} + {cname}  -> F1: {scores['f1']:.3f}, Acc: {scores['accuracy']:.3f}")

        # Atualizar melhor modelo usando F1 como métrica principal
        if scores['f1'] > best_score:
            best_score = scores['f1']
            best_model = clf
            best_vectorizer = vect
            best_combo = (vname, cname, scores)

print('\nMelhor combinação encontrada:')
print(best_combo)

# Salvar o melhor modelo e o vectorizer

# Re-treinar o melhor modelo com o dataset inteiro antes de salvar:
# 1) Re-ajusta (fit) o vectorizer no conjunto completo `X`.
# 2) Transforma X inteiro e re-treina o classificador no dataset completo.
best_vectorizer = best_vectorizer.fit(X)
X_full_vec = best_vectorizer.transform(X)
best_model.fit(X_full_vec, y)

# Salvar o classificador treinado com todos os dados e o vectorizer completo
joblib.dump(best_model, 'spam_model.pkl')
joblib.dump(best_vectorizer, 'vectorizer.pkl')

print('Melhor modelo salvo em spam_model.pkl (e vectorizer.pkl)')

# Opcional: avaliação cruzada do melhor (k-fold)
if best_model is not None:
    # Reconstruir pipeline e avaliar por cross-validation para validar estabilidade
    X_full_vec = best_vectorizer.transform(X)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(best_model, X_full_vec, y, cv=cv, scoring='f1')
    print(f"Validação cruzada F1 (5-fold) do melhor modelo: média={cv_scores.mean():.3f}, std={cv_scores.std():.3f}")