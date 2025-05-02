#!/usr/bin/env python3
# Mouse Info - Um script para mostrar informações do mouse em tempo real e gerar log de cliques
# Necessita a biblioteca pynput: pip install pynput

import time
import datetime
from pynput import mouse
import tkinter as tk
from tkinter import font, scrolledtext, messagebox
import os

class MouseInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Info")
        self.root.geometry("500x500")
        self.root.resizable(True, True)
        
        # Configuração da fonte
        self.info_font = font.Font(family="Arial", size=12)
        self.title_font = font.Font(family="Arial", size=14, weight="bold")
        self.log_font = font.Font(family="Courier", size=10)
        
        # Criar arquivo de log
        self.log_filename = f"mouse_clicks_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.log_file = open(self.log_filename, "w")
        self.log_file.write("# Log de Cliques do Mouse\n")
        self.log_file.write("# Formato: Data/Hora, Botão, Posição X, Posição Y\n")
        self.log_file.write("---------------------------------------------\n")
        self.log_file.flush()
        
        # Contador de cliques
        self.click_count = 0
        
        # Título
        self.title_label = tk.Label(root, text="Informações do Mouse", font=self.title_font)
        self.title_label.pack(pady=10)
        
        # Frame para informações
        info_frame = tk.Frame(root)
        info_frame.pack(fill=tk.X, padx=20)
        
        # Labels para mostrar posição
        self.pos_label = tk.Label(info_frame, text="Posição: (0, 0)", font=self.info_font, anchor="w")
        self.pos_label.pack(fill=tk.X, pady=5)
        
        # Label para mostrar cliques
        self.click_label = tk.Label(info_frame, text="Último clique: Nenhum", font=self.info_font, anchor="w")
        self.click_label.pack(fill=tk.X, pady=5)
        
        # Label para contador de cliques
        self.count_label = tk.Label(info_frame, text="Total de cliques: 0", font=self.info_font, anchor="w")
        self.count_label.pack(fill=tk.X, pady=5)
        
        # Label para nome do arquivo de log
        self.log_label = tk.Label(info_frame, text=f"Arquivo de log: {self.log_filename}", font=self.info_font, anchor="w")
        self.log_label.pack(fill=tk.X, pady=5)
        
        # Área de texto para exibir o log
        log_frame = tk.LabelFrame(root, text="Log de Cliques", font=self.info_font)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, font=self.log_font, wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para botões
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botão para limpar log
        self.clear_button = tk.Button(button_frame, text="Limpar Log", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=20)
        
        # Botão para abrir o arquivo de log
        self.open_button = tk.Button(button_frame, text="Abrir Arquivo Log", command=self.open_log_file)
        self.open_button.pack(side=tk.LEFT, padx=20)
        
        # Botão para sair
        self.exit_button = tk.Button(button_frame, text="Sair", command=self.on_exit)
        self.exit_button.pack(side=tk.RIGHT, padx=20)
        
        # Iniciar monitoramento do mouse
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )
        self.listener.start()
        
        # Atualizar a interface a cada 100ms
        self.root.after(100, self.update_ui)
        
        # Configurar ação de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
    def on_move(self, x, y):
        """Callback quando o mouse é movido"""
        self.current_pos = (x, y)
        
    def on_click(self, x, y, button, pressed):
        """Callback quando um botão do mouse é clicado"""
        if pressed:
            self.last_click = (x, y, button)
            button_name = str(button).split(".")[-1]
            
            # Incrementar contador
            self.click_count += 1
            
            # Formatar timestamp
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # Registrar no log
            log_entry = f"{timestamp}, {button_name}, X={x}, Y={y}\n"
            
            # Escrever no arquivo
            self.log_file.write(log_entry)
            self.log_file.flush()
            
            # Adicionar à área de texto
            self.log_area.insert(tk.END, log_entry)
            self.log_area.see(tk.END)  # Rolar para mostrar a entrada mais recente
    
    def update_ui(self):
        """Atualiza a interface com as informações mais recentes"""
        # Atualizar posição
        if hasattr(self, 'current_pos'):
            self.pos_label.config(text=f"Posição: {self.current_pos}")
        
        # Atualizar informação de clique
        if hasattr(self, 'last_click'):
            x, y, button = self.last_click
            button_name = str(button).split(".")[-1]
            self.click_label.config(text=f"Último clique: {button_name} em ({x}, {y})")
            
        # Atualizar contador
        self.count_label.config(text=f"Total de cliques: {self.click_count}")
        
        # Continuar atualizando
        self.root.after(100, self.update_ui)
        
    def clear_log(self):
        """Limpa a área de log na interface (não afeta o arquivo)"""
        self.log_area.delete(1.0, tk.END)
        
    def open_log_file(self):
        """Tenta abrir o arquivo de log no editor padrão"""
        try:
            # Detecta o sistema operacional e usa o comando apropriado
            import platform
            import subprocess
            
            system = platform.system()
            if system == 'Windows':
                os.startfile(self.log_filename)
            elif system == 'Darwin':  # macOS
                subprocess.call(('open', self.log_filename))
            else:  # Linux e outros
                subprocess.call(('xdg-open', self.log_filename))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {str(e)}")
    
    def on_exit(self):
        """Manipula o evento de fechamento da janela"""
        # Fechar o arquivo de log
        if hasattr(self, 'log_file') and not self.log_file.closed:
            self.log_file.close()
            
        # Finalizar o monitoramento do mouse
        if hasattr(self, 'listener'):
            self.listener.stop()
            
        # Mostrar mensagem sobre o arquivo de log
        messagebox.showinfo("Informação", f"O log foi salvo em:\n{os.path.abspath(self.log_filename)}")
        
        # Fechar a aplicação
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MouseInfoApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
