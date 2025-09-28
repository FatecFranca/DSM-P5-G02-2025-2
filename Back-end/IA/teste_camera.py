import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import requests
import io
import base64
import threading
import time
import queue

class CameraTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teste de Detecção de Lixo - Câmera ao Vivo")
        self.root.geometry("800x600")

        # Variáveis
        self.cap = None
        self.is_capturing = False
        self.is_live_detection = False
        self.current_image = None
        self.detection_thread = None
        self.camera_thread = None
        self.processing_queue = queue.Queue(maxsize=1)  # Fila para processamento
        self.last_processed_time = 0
        self.processing_active = False  # Flag para controlar processamento
        self.cached_result = None  # Cache do último resultado
        self.last_frame = None  # Último frame capturado
        
        # Thread de trabalho pesado
        self.worker_thread = None
        self.worker_active = False
        
        # NOVO: Sistema de detecção AO VIVO com câmera simultânea
        self.frame_buffer = queue.Queue(maxsize=1)
        self.last_processed_frame = None
        self.processing_fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.last_gui_update = 0
        self.gui_update_interval = 0.15  # 6-7 FPS de atualização visual
        
        # NOVO: Controle de overlay
        self.overlay_image = None  # Imagem com overlays
        self.show_overlay = False  # Flag para mostrar overlay
        self.last_overlay_update = 0  # Controle de frequência de atualização do overlay

        # Widgets
        self.start_btn = tk.Button(root, text="Iniciar Câmera", command=self.start_camera)
        self.start_btn.pack(pady=10)

        self.live_btn = tk.Button(root, text="Iniciar Detecção ao Vivo", command=self.toggle_live_detection, state=tk.DISABLED)
        self.live_btn.pack(pady=10)

        self.capture_btn = tk.Button(root, text="Capturar Frame Único", command=self.capture_and_detect, state=tk.DISABLED)
        self.capture_btn.pack(pady=10)

        self.stop_btn = tk.Button(root, text="Parar Câmera", command=self.stop_camera, state=tk.DISABLED)
        self.stop_btn.pack(pady=10)

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Pronto")
        self.status_label.pack(pady=10)

    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Erro", "Não foi possível abrir a câmera")
                return

            self.is_capturing = True
            self.start_btn.config(state=tk.DISABLED)
            self.live_btn.config(state=tk.NORMAL)
            self.capture_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Câmera iniciada")

            # Iniciar atualização da câmera usando after() do Tkinter
            self.update_camera_preview()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar câmera: {str(e)}")

    def update_camera_preview(self):
        if not self.is_capturing:
            return

        try:
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame
                
                if not self.is_live_detection:
                    # Modo preview normal - mostrar câmera ao vivo
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_pil = frame_pil.resize((480, 360), Image.Resampling.LANCZOS)
                    self.current_image = ImageTk.PhotoImage(frame_pil)
                    self.image_label.config(image=self.current_image)
                    
                else:
                    # NOVO: Modo detecção AO VIVO com câmera simultânea - MAIS ESTÁVEL
                    try:
                        # Sempre tenta colocar frame no buffer para processamento
                        if self.frame_buffer.empty():
                            self.frame_buffer.put_nowait(frame.copy())
                    except queue.Full:
                        pass
                    
                    # Mostrar câmera ao vivo + overlay APENAS quando necessário
                    current_time = time.time()
                    if current_time - self.last_overlay_update >= 0.1:  # Máximo 10 FPS para overlay
                        self._show_live_camera_with_overlay(frame)
                        self.last_overlay_update = current_time
                    else:
                        # Mostrar apenas câmera sem overlay para manter fluidez
                        self._show_camera_only(frame)

            # Captura suave da câmera
            self.root.after(50, self.update_camera_preview)  # 20 FPS

        except Exception as e:
            print(f"Erro na atualização da câmera: {e}")
            self.root.after(50, self.update_camera_preview)

    def toggle_live_detection(self):
        if self.is_live_detection:
            self.stop_live_detection()
        else:
            self.start_live_detection()

    def start_live_detection(self):
        if not self.cap or not self.cap.isOpened():
            messagebox.showerror("Erro", "Câmera não está ativa")
            return

        self.is_live_detection = True
        self.live_btn.config(text="Parar Detecção ao Vivo")
        self.capture_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Detecção ao vivo iniciada")

        # NOVO: Limpar buffer e iniciar processamento AO VIVO
        while not self.frame_buffer.empty():
            try:
                self.frame_buffer.get_nowait()
            except queue.Empty:
                break
        
        # Iniciar worker thread para processamento CONTÍNUO
        self.worker_active = True
        self.worker_thread = threading.Thread(
            target=self._live_processing_worker,
            daemon=True
        )
        self.worker_thread.start()

    def stop_live_detection(self):
        self.is_live_detection = False
        self.live_btn.config(text="Iniciar Detecção ao Vivo")
        self.capture_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Detecção ao vivo parada")

    def process_live_detection(self):
        """DEPRECATED - Substituída por processamento ao vivo contínuo"""
        pass

    def _live_processing_worker(self):
        """
        Worker thread que processa frames AO VIVO continuamente - VERSÃO MAIS ESTÁVEL
        """
        while self.worker_active and self.is_live_detection:
            try:
                # Pegar frame do buffer com timeout MAIOR
                frame = self.frame_buffer.get(timeout=0.5)  # Espera até 0.5s por frame
                
                # Verificar se ainda estamos ativos antes de processar
                if not self.worker_active or not self.is_live_detection:
                    break
                
                # Processar frame
                self._process_single_frame_live(frame)
                
                # Calcular FPS MENOS frequentemente
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_fps_time >= 2.0:  # A cada 2 segundos
                    self.processing_fps = self.frame_count // 2  # FPS médio
                    self.frame_count = 0
                    self.last_fps_time = current_time
                
                # Pausa adicional entre processamentos para estabilidade
                time.sleep(0.1)
                
            except queue.Empty:
                # Nenhum frame disponível, pausa maior
                time.sleep(0.2)
                continue
            except Exception as e:
                print(f"Erro no processamento ao vivo: {e}")
                time.sleep(0.5)  # Pausa maior em caso de erro

    def _process_single_frame_live(self, frame):
        """
        Processa um único frame para detecção ao vivo - VERSÃO MAIS LENTA E ESTÁVEL
        """
        try:
            # 1. Codificação MAIS RÁPIDA ainda
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Qualidade ainda menor
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            image_bytes = buffer.tobytes()

            # 2. Requisição HTTP com timeout MAIS LONGO para estabilidade
            files = {'file': ('frame.jpg', io.BytesIO(image_bytes), 'image/jpeg')}
            response = requests.post('http://localhost:5000/detect', files=files, timeout=2.0)

            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'sucesso':
                    # 3. Processamento MAIS RÁPIDO
                    img_data = base64.b64decode(result['imagem_processada_base64'])
                    img_pil = Image.open(io.BytesIO(img_data))
                    img_pil = img_pil.resize((320, 240), Image.Resampling.LANCZOS)  # TAMANHO AINDA MENOR!
                    
                    # 4. Criar ImageTk
                    processed_image = ImageTk.PhotoImage(img_pil)
                    
                    # 5. Preparar status
                    status_text = self._prepare_status_text(result['objetos'])
                    
                    # 6. Cachear resultado
                    self.cached_result = {
                        'image': processed_image,
                        'status': status_text,
                        'raw_result': result
                    }
                    
                    # 7. Agendar atualização com THROTTLING
                    current_time = time.time()
                    if current_time - self.last_gui_update >= self.gui_update_interval:
                        self.root.after(0, lambda: self._update_gui_safe(processed_image, status_text))
                        self.last_gui_update = current_time
                    
            # Pausa MAIOR para reduzir carga
            time.sleep(0.15)  # 6-7 FPS de processamento (era 20)

        except requests.exceptions.Timeout:
            # Timeout mais longo, continuar
            pass
        except Exception as e:
            print(f"Erro no processamento de frame: {e}")
            time.sleep(0.1)  # Pausa extra em caso de erro

    def _heavy_processing_worker(self, frame):
        """
        Worker thread que executa todo o trabalho pesado:
        - Codificação da imagem
        - Requisição HTTP 
        - Decodificação da resposta
        - Redimensionamento
        - Preparação do resultado final
        """
        try:
            # 1. Codificação da imagem MAIS RÁPIDA (qualidade menor para velocidade)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Qualidade 70% - MAIS RÁPIDO!
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            image_bytes = buffer.tobytes()

            # 2. Requisição HTTP com timeout MAIS CURTO para reduzir demora
            files = {'file': ('frame.jpg', io.BytesIO(image_bytes), 'image/jpeg')}
            response = requests.post('http://localhost:5000/detect', files=files, timeout=1.5)  # REDUZIDO!

            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'sucesso':
                    # 3. Decodificação e redimensionamento MAIS RÁPIDO
                    img_data = base64.b64decode(result['imagem_processada_base64'])
                    img_pil = Image.open(io.BytesIO(img_data))
                    
                    # REDUZIR TAMANHO PARA PROCESSAMENTO MAIS RÁPIDO
                    img_pil = img_pil.resize((480, 360), Image.Resampling.LANCZOS)  # TAMANHO MENOR!
                    
                    # 4. Preparar ImageTk (operação pesada)
                    processed_image = ImageTk.PhotoImage(img_pil)
                    
                    # 5. Preparar texto de status
                    status_text = self._prepare_status_text(result['objetos'])
                    
                    # 6. Cachear resultado para reutilização
                    self.cached_result = {
                        'image': processed_image,
                        'status': status_text,
                        'raw_result': result
                    }
                    
                    # 7. Agendar atualização mínima na thread principal
                    self.root.after(0, lambda: self._update_gui_safe(processed_image, status_text))
                else:
                    self.root.after(0, lambda: self._update_status_safe("Status: Processamento falhou"))
            else:
                self.root.after(0, lambda: self._update_status_safe("Status: Erro servidor"))

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self._update_status_safe("Status: Timeout - reduzindo velocidade..."))
        except Exception as e:
            print(f"Erro na worker thread: {e}")
            self.root.after(0, lambda: self._update_status_safe("Status: Erro de processamento"))
        finally:
            # Sempre liberar flag de processamento
            self.processing_active = False

    def _prepare_status_text(self, objetos):
        """Prepara texto de status (operação leve mas separada)"""
        if not objetos:
            return "Status: Nenhum objeto detectado"
        
        lixo_reciclavel = sum(1 for obj in objetos if obj.get('tipo') == 'lixo' and obj.get('reciclavel') == True)
        lixo_organico = sum(1 for obj in objetos if obj.get('material') in ['orgânico'])
        lixo_nao_reciclavel = sum(1 for obj in objetos if obj.get('tipo') == 'lixo' and obj.get('reciclavel') == False and obj.get('material') != 'orgânico')
        nao_lixo = sum(1 for obj in objetos if obj.get('tipo') == 'não_lixo')

        status_parts = []
        if nao_lixo > 0:
            status_parts.append(f"🟢{nao_lixo} não-lixo")
        if lixo_reciclavel > 0:
            status_parts.append(f"🔵{lixo_reciclavel} reciclável")
        if lixo_organico > 0:
            status_parts.append(f"🟠{lixo_organico} orgânico")
        if lixo_nao_reciclavel > 0:
            status_parts.append(f"🔴{lixo_nao_reciclavel} não-reciclável")

        return f"Status: {' | '.join(status_parts)}"

    def _update_gui_safe(self, processed_image, status_text):
        """Atualização mínima e rápida da GUI com proteção contra travamentos"""
        try:
            # Verificar se ainda estamos em modo de detecção ao vivo
            if not self.is_live_detection or not self.is_capturing:
                return
                
            self.current_image = processed_image
            self.image_label.config(image=self.current_image)
            
            # NOVO: Adicionar info de FPS ao status APENAS se disponível
            if hasattr(self, 'processing_fps') and self.processing_fps > 0:
                status_text += f" | {self.processing_fps} FPS"
            
            self.status_label.config(text=status_text)
            
        except Exception as e:
            # Log silencioso para não sobrecarregar console
            pass

    def _update_status_safe(self, status_text):
        """Atualização segura apenas do status"""
        try:
            self.status_label.config(text=status_text)
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")

    def update_processed_image(self, result):
        """DEPRECATED - Mantido para compatibilidade com capture_and_detect"""
        try:
            # Decodificar imagem processada com overlays coloridos
            img_data = base64.b64decode(result['imagem_processada_base64'])
            img_pil = Image.open(io.BytesIO(img_data))
            img_pil = img_pil.resize((480, 360), Image.Resampling.LANCZOS)  # TAMANHO MENOR!

            # Atualizar imagem na interface
            self.current_image = ImageTk.PhotoImage(img_pil)
            self.image_label.config(image=self.current_image)

            # Preparar e mostrar status
            status_text = self._prepare_status_text(result['objetos'])
            self.status_label.config(text=status_text)

        except Exception as e:
            print(f"Erro ao atualizar imagem: {e}")
            self.status_label.config(text="Status: Erro ao processar imagem")

    def display_cached_result(self):
        """Mostra o último resultado processado de forma otimizada e segura"""
        if self.cached_result and 'image' in self.cached_result and self.is_live_detection:
            try:
                # Usar resultado já processado - operação instantânea
                self.current_image = self.cached_result['image']
                self.image_label.config(image=self.current_image)
                self.status_label.config(text=self.cached_result['status'])
            except Exception as e:
                # Log silencioso para não sobrecarregar
                pass

    def capture_and_detect(self):
        if not self.cap or not self.cap.isOpened():
            messagebox.showerror("Erro", "Câmera não está ativa")
            return

        try:
            self.status_label.config(text="Status: Capturando...")

            # Capturar frame
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Erro", "Falha ao capturar frame")
                return

            self.status_label.config(text="Status: Processando...")

            # Executar processamento em worker thread para não travar a GUI
            def process_single_frame():
                try:
                    # Operações pesadas na worker thread MAIS RÁPIDAS
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # Qualidade 70% - MAIS RÁPIDO!
                    _, buffer = cv2.imencode('.jpg', frame, encode_param)
                    image_bytes = buffer.tobytes()

                    # Enviar para API
                    files = {'file': ('frame.jpg', io.BytesIO(image_bytes), 'image/jpeg')}
                    response = requests.post('http://localhost:5000/detect', files=files, timeout=10)

                    if response.status_code == 200:
                        result = response.json()
                        if result['status'] == 'sucesso':
                            # Processamento pesado da imagem MAIS RÁPIDO
                            img_data = base64.b64decode(result['imagem_processada_base64'])
                            img_pil = Image.open(io.BytesIO(img_data))
                            img_pil = img_pil.resize((480, 360), Image.Resampling.LANCZOS)  # TAMANHO MENOR!
                            processed_image = ImageTk.PhotoImage(img_pil)

                            # Preparar info para popup
                            objetos = result['objetos']
                            if objetos:
                                info = f"Objetos detectados: {len(objetos)}\n"
                                for obj in objetos:
                                    reciclavel_text = 'Reciclável' if obj.get('reciclavel') else 'Não Reciclável'
                                    if obj.get('reciclavel') is None:
                                        reciclavel_text = 'N/A'
                                    info += f"- {obj['material']} ({reciclavel_text}) - Conf: {obj['confidence']:.2f}\n"
                            else:
                                info = "Nenhum objeto detectado"

                            # Agendar atualização na thread principal
                            self.root.after(0, lambda: self._finish_single_capture(processed_image, info, "Status: Detecção concluída"))
                        else:
                            error_msg = result.get('error', 'Erro desconhecido')
                            self.root.after(0, lambda: self._show_error(f"Erro na API: {error_msg}"))
                    else:
                        self.root.after(0, lambda: self._show_error(f"Erro HTTP: {response.status_code}"))

                except requests.exceptions.RequestException as e:
                    self.root.after(0, lambda: self._show_error(f"Erro de conexão: {str(e)}"))
                except Exception as e:
                    self.root.after(0, lambda: self._show_error(f"Erro inesperado: {str(e)}"))

            # Executar em thread separada
            worker_thread = threading.Thread(target=process_single_frame, daemon=True)
            worker_thread.start()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar processamento: {str(e)}")

    def _finish_single_capture(self, processed_image, info_text, status_text):
        """Finaliza captura única na thread principal"""
        try:
            # Atualizar interface
            self.current_image = processed_image
            self.image_label.config(image=self.current_image)
            self.status_label.config(text=status_text)
            
            # Mostrar popup com resultados
            messagebox.showinfo("Detecção", info_text)
        except Exception as e:
            print(f"Erro ao finalizar captura: {e}")

    def _show_error(self, error_msg):
        """Mostra erro na thread principal"""
        try:
            self.status_label.config(text="Status: Erro")
            messagebox.showerror("Erro", error_msg)
        except Exception as e:
            print(f"Erro ao mostrar erro: {e}")

    def _show_live_camera_with_overlay(self, frame):
        """
        Mostra câmera ao vivo COM overlay de detecção simultaneamente
        """
        try:
            # 1. Converter frame para RGB e criar cópia para overlay
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            display_frame = frame_rgb.copy()

            # 2. Verificar se temos resultado processado recente
            if self.cached_result and 'raw_result' in self.cached_result:
                result = self.cached_result['raw_result']

                # 3. Aplicar overlays coloridos nos objetos detectados
                if 'objetos' in result and result['objetos']:
                    for obj in result['objetos']:
                        # Coordenadas do bounding box
                        x1, y1, x2, y2 = obj['bbox']

                        # Determinar cor baseada no tipo de objeto
                        if obj.get('tipo') == 'não_lixo':
                            color = (0, 255, 0)  # Verde para não-lixo
                        elif obj.get('tipo') == 'lixo':
                            if obj.get('reciclavel') == True:
                                color = (0, 255, 255)  # Azul ciano para reciclável
                            elif obj.get('material') == 'orgânico':
                                color = (0, 165, 255)  # Laranja para orgânico
                            else:
                                color = (0, 0, 255)  # Vermelho para não-reciclável
                        else:
                            color = (255, 255, 255)  # Branco como fallback

                        # Desenhar retângulo
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)

                        # Adicionar label com material e confiança
                        label = f"{obj.get('material', 'desconhecido')} {obj.get('confidence', 0):.2f}"
                        cv2.putText(display_frame, label, (x1, y1-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 4. Converter para PIL e redimensionar
            frame_pil = Image.fromarray(display_frame)
            frame_pil = frame_pil.resize((480, 360), Image.Resampling.LANCZOS)

            # 5. Criar PhotoImage e atualizar display
            self.current_image = ImageTk.PhotoImage(frame_pil)
            self.overlay_image = self.current_image  # Salvar para reutilização
            self.show_overlay = True  # Permitir mostrar overlay
            self.image_label.config(image=self.current_image)

            # 6. Atualizar status se disponível
            if self.cached_result and 'status' in self.cached_result:
                status_text = self.cached_result['status']
                # Adicionar FPS se disponível
                if hasattr(self, 'processing_fps') and self.processing_fps > 0:
                    status_text += f" | {self.processing_fps} FPS"
                self.status_label.config(text=status_text)

        except Exception as e:
            print(f"Erro ao mostrar câmera com overlay: {e}")
            # Fallback: mostrar apenas câmera sem overlay
            try:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_pil = frame_pil.resize((480, 360), Image.Resampling.LANCZOS)
                self.current_image = ImageTk.PhotoImage(frame_pil)
                self.image_label.config(image=self.current_image)
            except Exception as e2:
                print(f"Erro no fallback da câmera: {e2}")

    def _show_camera_only(self, frame):
        """
        Mostra apenas a câmera ao vivo sem overlay - para manter fluidez
        """
        try:
            # Verificar se já temos uma imagem de overlay para mostrar
            if self.overlay_image and self.show_overlay:
                # Usar imagem com overlay se disponível e permitida
                self.image_label.config(image=self.overlay_image)
            else:
                # Mostrar apenas câmera limpa
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_pil = frame_pil.resize((480, 360), Image.Resampling.LANCZOS)
                self.current_image = ImageTk.PhotoImage(frame_pil)
                self.image_label.config(image=self.current_image)

        except Exception as e:
            print(f"Erro ao mostrar câmera: {e}")

    def stop_camera(self):
        self.is_live_detection = False
        self.is_capturing = False
        self.processing_active = False  # Resetar flag de processamento
        self.worker_active = False  # Parar worker threads
        self.cached_result = None  # Limpar cache
        
        # NOVO: Limpar buffer de frames
        while not self.frame_buffer.empty():
            try:
                self.frame_buffer.get_nowait()
            except queue.Empty:
                break
        
        if self.cap:
            self.cap.release()
            
        # Aguardar threads terminarem (timeout de 1 segundo)
        if self.worker_thread and self.worker_thread.is_alive():
            try:
                self.worker_thread.join(timeout=1.0)
            except:
                pass  # Ignore se não conseguir fazer join
                
        self.start_btn.config(state=tk.NORMAL)
        self.live_btn.config(state=tk.DISABLED, text="Iniciar Detecção ao Vivo")
        self.capture_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Câmera parada")

    def on_closing(self):
        self.stop_camera()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraTestApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()