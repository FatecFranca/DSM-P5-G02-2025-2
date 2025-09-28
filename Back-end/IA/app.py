import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np
import kagglehub
import os

path = kagglehub.dataset_download("sumn2u/garbage-classification-v2")
DATASET_PATH = os.path.join(path, 'garbage-dataset')

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
NUM_CLASSES = 10
INITIAL_EPOCHS = 20
FINE_TUNE_EPOCHS = 15
TOTAL_EPOCHS = INITIAL_EPOCHS + FINE_TUNE_EPOCHS

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=5,
    width_shift_range=0.05,
    height_shift_range=0.05,
    zoom_range=0.05,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  
)

validation_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

validation_generator = validation_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

print("Classes encontradas:", train_generator.class_indices)
print("Total de imagens de treino:", train_generator.samples)
print("Total de imagens de validação:", validation_generator.samples)


class_indices = train_generator.class_indices
class_counts = {}
for class_name, class_index in class_indices.items():
    class_counts[class_index] = 0

for i in range(len(train_generator.classes)):
    class_counts[train_generator.classes[i]] += 1

print("Distribuição das classes:")
for class_name, class_index in class_indices.items():
    print(f"{class_name}: {class_counts[class_index]} imagens")

total_samples = sum(class_counts.values())
class_weights = {}
for class_index, count in class_counts.items():
    class_weights[class_index] = total_samples / (len(class_counts) * count)

print("Pesos calculados para balanceamento:", class_weights)


base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.4)(x)
predictions = Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("--- FASE 1: TREINANDO APENAS AS CAMADAS SUPERIORES ---")
history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=INITIAL_EPOCHS,
    class_weight=class_weights,
    verbose=1
)


base_model.trainable = True

fine_tune_at = 140  
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

model.compile(
    optimizer=Adam(learning_rate=5e-6), 
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"Descongelando apenas {len(base_model.layers) - fine_tune_at} camadas para fine-tuning")
print("\n--- FASE 2: REALIZANDO O AJUSTE FINO (FINE-TUNING) ---")
history_fine = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=TOTAL_EPOCHS,
    initial_epoch=history.epoch[-1],
    class_weight=class_weights,
    verbose=1
)

model.save('modelo_lixo_ajustado.h5')
print("Modelo aprimorado e salvo como 'modelo_lixo_ajustado.h5'")

acc = history.history['accuracy'] + history_fine.history['accuracy']
val_acc = history.history['val_accuracy'] + history_fine.history['val_accuracy']
loss = history.history['loss'] + history_fine.history['loss']
val_loss = history.history['val_loss'] + history_fine.history['val_loss']

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(acc, label='Acurácia de Treino')
plt.plot(val_acc, label='Acurácia de Validação')
plt.axvline(x=INITIAL_EPOCHS-1, color='gray', linestyle='--', label='Início do Fine-Tuning')
plt.legend(loc='lower right')
plt.title('Acurácia de Treino e Validação')
plt.xlabel('Épocas')

plt.subplot(1, 2, 2)
plt.plot(loss, label='Perda de Treino')
plt.plot(val_loss, label='Perda de Validação')
plt.axvline(x=INITIAL_EPOCHS-1, color='gray', linestyle='--', label='Início do Fine-Tuning')
plt.legend(loc='upper right')
plt.title('Perda de Treino e Validação')
plt.xlabel('Épocas')
plt.show()