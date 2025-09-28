import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, Input, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import numpy as np
#
def criar_modelo_reciclabilidade():
    """
    Modelo que recebe:
    1. Imagem (224x224x3)
    2. Tipo de material (one-hot encoded - 10 classes)
    
    Saída: Reciclável (1) ou Não Reciclável (0)
    """
    
    input_image = Input(shape=(224, 224, 3), name='image_input')
    
    input_material = Input(shape=(10,), name='material_input')
    
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_tensor=input_image)
    base_model.trainable = False
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)
    
    material_features = Dense(32, activation='relu')(input_material)
    material_features = Dense(16, activation='relu')(material_features)
    
    combined = Concatenate()([x, material_features])
    combined = Dense(64, activation='relu')(combined)
    combined = Dropout(0.3)(combined)
    combined = Dense(32, activation='relu')(combined)
    
    output = Dense(1, activation='sigmoid', name='recyclable_output')(combined)
    
    model = Model(inputs=[input_image, input_material], outputs=output)
    
    return model

RECICLABILIDADE_BASE = {
    'glass': True,      # Vidro: geralmente reciclável
    'metal': True,      # Metal: geralmente reciclável  
    'paper': True,      # Papel: geralmente reciclável
    'cardboard': True,  # Papelão: geralmente reciclável
    'plastic': True,    # Plástico: depende do tipo (modelo vai aprender)
    'battery': False,   # Bateria: requer descarte especial
    'biological': False,# Orgânico: compostável, não reciclável tradicional
    'clothes': False,   # Roupas: doação/reutilização, não reciclagem comum
    'shoes': False,     # Sapatos: similar às roupas
    'trash': False      # Lixo comum: não reciclável
}

def preparar_dataset_reciclabilidade():
    """
    Prepara dataset combinando:
    1. Imagens do dataset atual
    2. Labels de reciclabilidade baseados nas regras + exceções
    """
    pass

if __name__ == "__main__":
    modelo = criar_modelo_reciclabilidade()
    print("Modelo de reciclabilidade criado!")
    print(modelo.summary())
