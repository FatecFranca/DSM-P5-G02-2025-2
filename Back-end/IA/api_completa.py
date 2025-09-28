from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import base64
from ultralytics import YOLO
import cv2
import os

app = Flask(__name__)

# Tentar carregar o modelo customizado
modelo_carregado = False
try:
    if os.path.exists('modelo_lixo_ajustado.h5'):
        modelo_material = tf.keras.models.load_model('modelo_lixo_ajustado.h5')
        modelo_carregado = True
        print("Modelo customizado carregado com sucesso!")
    else:
        print("Arquivo modelo_lixo_ajustado.h5 não encontrado")
        modelo_material = None
except Exception as e:
    print(f"Erro ao carregar modelo customizado: {e}")
    modelo_material = None

# Carregar modelo YOLOv8 para detecção
modelo_deteccao = YOLO('yolov8n.pt')

# Classes que NÃO são lixo (humanos, animais, veículos, etc.)
CLASSES_NAO_LIXO = {
    'person': 'pessoa',
    'bicycle': 'bicicleta', 
    'car': 'carro',
    'motorcycle': 'moto',
    'airplane': 'avião',
    'bus': 'ônibus',
    'train': 'trem',
    'truck': 'caminhão',
    'boat': 'barco',
    'traffic light': 'semáforo',
    'fire hydrant': 'hidrante',
    'stop sign': 'placa pare',
    'parking meter': 'parquímetro',
    'bench': 'banco',
    'bird': 'pássaro',
    'cat': 'gato',
    'dog': 'cachorro',
    'horse': 'cavalo',
    'sheep': 'ovelha',
    'cow': 'vaca',
    'elephant': 'elefante',
    'bear': 'urso',
    'zebra': 'zebra',
    'giraffe': 'girafa',
    'backpack': 'mochila',
    'umbrella': 'guarda-chuva',
    'handbag': 'bolsa',
    'tie': 'gravata',
    'suitcase': 'mala',
    'frisbee': 'frisbee',
    'skis': 'esquis',
    'snowboard': 'snowboard',
    'sports ball': 'bola',
    'kite': 'pipa',
    'baseball bat': 'taco beisebol',
    'baseball glove': 'luva beisebol',
    'skateboard': 'skate',
    'surfboard': 'prancha surf',
    'tennis racket': 'raquete tênis',
    'chair': 'cadeira',
    'couch': 'sofá',
    'potted plant': 'planta',
    'bed': 'cama',
    'dining table': 'mesa',
    'toilet': 'banheiro',
    'tv': 'tv',
    'laptop': 'laptop',
    'microwave': 'microondas',
    'oven': 'forno',
    'toaster': 'torradeira',
    'sink': 'pia',
    'refrigerator': 'geladeira'
}

# Mapeamento expandido para classes de lixo
MAPEAMENTO_LIXO = {
    'bottle': 'plastic',
    'can': 'metal',
    'cup': 'plastic',
    'paper': 'paper',
    'cardboard': 'cardboard',
    'glass': 'glass',
    'wine glass': 'glass',
    'fork': 'metal',
    'knife': 'metal',
    'spoon': 'metal',
    'bowl': 'plastic',
    'banana': 'biological',
    'apple': 'biological',
    'orange': 'biological',
    'carrot': 'biological',
    'broccoli': 'biological',
    'pizza': 'biological',
    'donut': 'biological',
    'cake': 'biological',
    'sandwich': 'biological',
    'hot dog': 'biological',
    'cell phone': 'trash',
    'keyboard': 'trash',
    'mouse': 'trash',
    'remote': 'trash',
    'book': 'paper',
    'clock': 'trash',
    'vase': 'glass',
    'scissors': 'metal',
    'teddy bear': 'clothes',
    'hair drier': 'trash',
    'toothbrush': 'plastic'
}

RECICLABILIDADE_BASE = {
    'glass': True,
    'metal': True,
    'paper': True,
    'cardboard': True,
    'plastic': True,
    'battery': False,
    'biological': False,
    'clothes': False,
    'shoes': False,
    'trash': False
}

traducoes = {
    'battery': 'bateria',
    'biological': 'orgânico',
    'cardboard': 'papelão',
    'clothes': 'roupas',
    'glass': 'vidro',
    'metal': 'metal',
    'paper': 'papel',
    'plastic': 'plástico',
    'shoes': 'sapatos',
    'trash': 'lixo comum'
}

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert('RGB')
    image = image.resize((224, 224))
    image_array = np.array(image)
    image_array = image_array / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

def determinar_reciclabilidade(material, confidence):
    """
    Sistema de regras inteligente para determinar reciclabilidade
    """
    regras_reciclabilidade = {
        'glass': {'reciclavel': True, 'motivo': 'Vidro é infinitamente reciclável'},
        'metal': {'reciclavel': True, 'motivo': 'Metal pode ser derretido e reutilizado'},
        'paper': {'reciclavel': True, 'motivo': 'Papel limpo é reciclável'},
        'cardboard': {'reciclavel': True, 'motivo': 'Papelão é altamente reciclável'},
        'plastic': {'reciclavel': True, 'motivo': 'Depende do tipo - PET, HDPE são recicláveis'},
        'battery': {'reciclavel': False, 'motivo': 'Requer descarte especial em pontos específicos'},
        'biological': {'reciclavel': False, 'motivo': 'Orgânico - use compostagem'},
        'clothes': {'reciclavel': False, 'motivo': 'Doe ou use em brechós - reutilização é melhor'},
        'shoes': {'reciclavel': False, 'motivo': 'Doe se em bom estado, alguns pontos aceitam'},
        'trash': {'reciclavel': False, 'motivo': 'Lixo comum - descarte normal'}
    }
    
    return regras_reciclabilidade.get(material, {
        'reciclavel': False, 
        'motivo': 'Material não identificado'
    })

@app.route('/classify-full', methods=['POST'])
def classify_full():
    """
    Classificação completa usando modelo customizado se disponível
    """
    if not modelo_carregado or not modelo_material:
        return jsonify({'error': 'Modelo customizado não disponível'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome do arquivo vazio'}), 400

    image_bytes = file.read()
    resultado = classify_single_image(image_bytes, 'single_image')

    if 'id' in resultado:
        del resultado['id']

    if resultado['status'] == 'erro':
        return jsonify(resultado), 500

    if 'status' in resultado:
        del resultado['status']

    return jsonify(resultado)

def classify_single_image(image_bytes, image_id=None):
    """
    Função auxiliar para classificar uma única imagem
    """
    try:
        preprocessed_image = preprocess_image(image_bytes)
        prediction = modelo_material.predict(preprocessed_image, verbose=0)
        predicted_class_index = np.argmax(prediction, axis=1)[0]
        confidence = float(np.max(prediction))

        if confidence < 0.5:
            return {
                'id': image_id,
                'material': 'Não identificado',
                'confidence': confidence,
                'reciclavel': None,
                'message': 'Imagem muito unclear - tente uma foto mais nítida',
                'status': 'baixa_confianca'
            }

        class_names = ['battery', 'biological', 'cardboard', 'clothes', 'glass', 'metal', 'paper', 'plastic', 'shoes', 'trash']
        
        metal_idx = 5
        glass_idx = 4
        
        metal_conf = float(prediction[0][metal_idx])
        glass_conf = float(prediction[0][glass_idx])
        
        if predicted_class_index == metal_idx and glass_conf > 0.25:
            return {
                'id': image_id,
                'material': 'Incerto entre Metal e Vidro',
                'confidence': confidence,
                'metal_confidence': metal_conf,
                'glass_confidence': glass_conf,
                'reciclavel': True,
                'message': 'Classificação incerta - tente foto mais clara',
                'motivo': 'Tanto metal quanto vidro são recicláveis',
                'status': 'incerto'
            }
        
        if predicted_class_index == glass_idx and metal_conf > 0.25:
            return {
                'id': image_id,
                'material': 'Incerto entre Vidro e Metal',
                'confidence': confidence,
                'glass_confidence': glass_conf,
                'metal_confidence': metal_conf,
                'reciclavel': True,
                'message': 'Classificação incerta - tente foto mais clara',
                'motivo': 'Tanto vidro quanto metal são recicláveis',
                'status': 'incerto'
            }

        material_en = class_names[predicted_class_index]
        
        traducoes = {
            'battery': 'bateria',
            'biological': 'orgânico', 
            'cardboard': 'papelão',
            'clothes': 'roupas',
            'glass': 'vidro',
            'metal': 'metal',
            'paper': 'papel', 
            'plastic': 'plástico',
            'shoes': 'sapatos',
            'trash': 'lixo comum'
        }
        
        material_pt = traducoes.get(material_en, material_en)
        info_reciclabilidade = determinar_reciclabilidade(material_en, confidence)
        
        return {
            'id': image_id,
            'material': material_pt,
            'material_confidence': confidence,
            'reciclavel': info_reciclabilidade['reciclavel'],
            'motivo': info_reciclabilidade['motivo'],
            'instrucao': get_instrucao_descarte(material_en, info_reciclabilidade['reciclavel']),
            'status': 'sucesso'
        }
        
    except Exception as e:
        return {
            'id': image_id,
            'error': str(e),
            'status': 'erro'
        }

@app.route('/classify-multiple', methods=['POST'])
def classify_multiple():
    """
    Classifica múltiplas imagens de uma vez
    Aceita múltiplos arquivos com nomes como 'image_1', 'image_2', etc.
    Ou múltiplos arquivos com o mesmo nome 'files'
    """
    try:
        resultados = {}
        total_imagens = 0
        sucessos = 0
        
        if not request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        for file_key in request.files:
            files = request.files.getlist(file_key)
            
            for i, file in enumerate(files):
                if file and file.filename != '':
                    total_imagens += 1
                    
                    if len(files) > 1:
                        image_id = f"{file_key}_{i+1}"
                    else:
                        image_id = file_key
                    
                    image_bytes = file.read()
                    resultado = classify_single_image(image_bytes, image_id)
                    
                    resultados[image_id] = resultado
                    
                    if resultado['status'] == 'sucesso':
                        sucessos += 1

        if total_imagens == 0:
            return jsonify({'error': 'Nenhuma imagem válida encontrada'}), 400

        resumo = {
            'total_imagens': total_imagens,
            'classificacoes_bem_sucedidas': sucessos,
            'taxa_sucesso': f"{(sucessos/total_imagens)*100:.1f}%"
        }
        
        categorias = {}
        for resultado in resultados.values():
            if resultado['status'] == 'sucesso':
                material = resultado['material']
                if material not in categorias:
                    categorias[material] = 0
                categorias[material] += 1

        return jsonify({
            'resumo': resumo,
            'categorias_encontradas': categorias,
            'resultados_detalhados': resultados,
            'status': 'concluido'
        })

    except Exception as e:
        return jsonify({
            'error': f'Erro interno: {str(e)}',
            'status': 'erro'
        }), 500

def get_instrucao_descarte(material, reciclavel):
    """
    Instruções específicas de descarte
    """
    if reciclavel:
        instrucoes = {
            'glass': 'Lave e coloque na lixeira azul (vidro)',
            'metal': 'Lave e coloque na lixeira amarela (metal)', 
            'paper': 'Mantenha seco e coloque na lixeira azul (papel)',
            'cardboard': 'Desmonte e coloque na lixeira azul (papel)',
            'plastic': 'Lave e verifique o símbolo - coloque na lixeira vermelha (plástico)'
        }
        return instrucoes.get(material, 'Coloque na coleta seletiva apropriada')
    else:
        instrucoes_especiais = {
            'battery': 'Leve a pontos de coleta especiais (supermercados, lojas de eletrônicos)',
            'biological': 'Faça compostagem ou descarte no lixo orgânico',
            'clothes': 'Doe para instituições ou coloque em contêineres de roupas',
            'shoes': 'Doe se em bom estado ou descarte no lixo comum',
            'trash': 'Descarte no lixo comum'
        }
        return instrucoes_especiais.get(material, 'Descarte no lixo comum')

@app.route('/classify-simple', methods=['POST'])
def classify_simple():
    """
    Classificação simples de múltiplas imagens - retorna apenas ID e categoria
    Exemplo de resposta: {"imagem_1": "orgânico", "imagem_2": "reciclável"}
    """
    try:
        resultados = {}
        
        if not request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        for file_key in request.files:
            files = request.files.getlist(file_key)
            
            for i, file in enumerate(files):
                if file and file.filename != '':
                    if len(files) > 1:
                        image_id = f"{file_key}_{i+1}"
                    else:
                        image_id = file_key
                    
                    image_bytes = file.read()
                    resultado = classify_single_image(image_bytes, image_id)
                    
                    if resultado['status'] == 'sucesso':
                        if resultado['reciclavel']:
                            categoria = "reciclável"
                        else:
                            categoria = resultado['material'] 
                    else:
                        categoria = "não identificado"
                    
                    resultados[image_id] = categoria
        return jsonify(resultados)

    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/debug', methods=['GET'])
def debug_model():
    """Endpoint para verificar se o modelo está funcionando"""
    try:
        # Teste com YOLO
        fake_image = np.random.rand(640, 480, 3) * 255
        fake_image = fake_image.astype(np.uint8)
        resultados = modelo_deteccao(fake_image)
        
        return jsonify({
            'status': 'OK',
            'yolo_loaded': True,
            'classes_mapeadas': list(MAPEAMENTO_LIXO.keys()),
            'sample_detection': len(resultados[0].boxes) if resultados else 0
        })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'yolo_loaded': False,
            'error': str(e)
        }), 500

def detectar_e_classificar(image_bytes):
    """
    Detecta objetos com YOLO e aplica sistema de cores:
    Verde: Não é lixo (humanos, animais, móveis)
    Azul: Lixo reciclável (plástico, metal, vidro, papel)
    Laranja: Lixo orgânico (frutas, comida)
    Vermelho: Lixo não reciclável
    """
    try:
        # Converter bytes para imagem OpenCV
        image = Image.open(io.BytesIO(image_bytes))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Detectar objetos com YOLO
        resultados = modelo_deteccao(image_cv)

        objetos_detectados = []
        for resultado in resultados:
            for box in resultado.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                classe_id = int(box.cls[0].cpu().numpy())
                classe_nome = modelo_deteccao.names[classe_id]

                # Threshold de confiança baixo para detectar mais objetos
                if conf > 0.25:
                    # Determinar tipo e cor
                    if classe_nome in CLASSES_NAO_LIXO:
                        # NÃO É LIXO - VERDE
                        objeto_pt = CLASSES_NAO_LIXO[classe_nome]
                        cor = (0, 255, 0)  # Verde
                        tipo = "não_lixo"
                        label = f"{objeto_pt}"
                        material_pt = objeto_pt
                        reciclavel = None
                        
                    elif classe_nome in MAPEAMENTO_LIXO:
                        # É LIXO - determinar subtipo
                        material_en = MAPEAMENTO_LIXO[classe_nome]
                        material_pt = traducoes.get(material_en, material_en)
                        reciclavel = RECICLABILIDADE_BASE.get(material_en, False)
                        tipo = "lixo"
                        
                        if material_en == 'biological':
                            # ORGÂNICO - LARANJA
                            cor = (0, 165, 255)  # Laranja (BGR)
                            label = f"{material_pt} - Orgânico"
                        elif reciclavel:
                            # RECICLÁVEL - AZUL
                            cor = (255, 0, 0)  # Azul (BGR)
                            label = f"{material_pt} - Reciclável"
                        else:
                            # NÃO RECICLÁVEL - VERMELHO
                            cor = (0, 0, 255)  # Vermelho (BGR)
                            label = f"{material_pt} - Não Reciclável"
                    else:
                        # Objeto não mapeado - cinza
                        cor = (128, 128, 128)  # Cinza
                        tipo = "desconhecido"
                        label = f"{classe_nome}"
                        material_pt = classe_nome
                        reciclavel = None

                    # Desenhar bounding box mais espessa
                    cv2.rectangle(image_cv, (int(x1), int(y1)), (int(x2), int(y2)), cor, 3)

                    # Label com fundo para melhor visibilidade
                    (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                    cv2.rectangle(image_cv, (int(x1), int(y1) - label_height - 10), 
                                (int(x1) + label_width, int(y1)), cor, -1)
                    cv2.putText(image_cv, label, (int(x1), int(y1) - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    objetos_detectados.append({
                        'material': material_pt,
                        'reciclavel': reciclavel,
                        'confidence': float(conf),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'tipo': tipo
                    })

        # Converter imagem processada
        _, buffer = cv2.imencode('.jpg', image_cv)
        image_processada_bytes = buffer.tobytes()

        return {
            'status': 'sucesso',
            'objetos': objetos_detectados,
            'imagem_processada_base64': base64.b64encode(image_processada_bytes).decode('utf-8'),
            'modelo_usado': 'custom' if modelo_carregado else 'yolo'
        }

    except Exception as e:
        return {'status': 'erro', 'error': str(e)}

@app.route('/detect', methods=['POST'])
def detect_objects():
    """
    Endpoint para detecção de objetos com bounding boxes.
    Retorna imagem com overlays e dados JSON.
    Aceita 'file' ou 'image' como campo do arquivo.
    """
    # Verificar se há arquivo em 'file' ou 'image'
    file = None
    if 'file' in request.files:
        file = request.files['file']
    elif 'image' in request.files:
        file = request.files['image']
    else:
        return jsonify({'error': 'Nenhum arquivo enviado (use "file" ou "image")'}), 400

    if file.filename == '':
        return jsonify({'error': 'Nome do arquivo vazio'}), 400

    image_bytes = file.read()
    resultado = detectar_e_classificar(image_bytes)
    
    if resultado['status'] == 'erro':
        return jsonify(resultado), 500
    
    return jsonify(resultado)

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    print("Rotas disponíveis:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
