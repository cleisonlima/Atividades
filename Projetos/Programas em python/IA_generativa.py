import tkinter as tk
from tkinter import messagebox
import google.generativeai as genai
import os

# Configurar a chave da API
api_key = "SUA_CHAVE_AQUI"
os.environ["GEMINI_API_KEY"] = api_key

# Inicializar o cliente da API
client = genai.Client()

# Função para enviar a pergunta e obter a resposta
def enviar_pergunta():
    pergunta = entry_pergunta.get()
    if not pergunta:
        messagebox.showwarning("Entrada vazia", "Por favor, digite uma pergunta.")
        return

    try:
        resposta = client.chat(messages=[{"role": "user", "content": pergunta}])
        texto_resposta.config(state=tk.NORMAL)
        texto_resposta.delete(1.0, tk.END)
        texto_resposta.insert(tk.END, resposta.message["content"])
        texto_resposta.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Criar a janela principal
root = tk.Tk()
root.title("Assistente AI com Gemini")
root.geometry("500x400")

# Criar widgets
label_pergunta = tk.Label(root, text="Digite sua pergunta:")
label_pergunta.pack(pady=10)

entry_pergunta = tk.Entry(root, width=50)
entry_pergunta.pack(pady=5)

btn_enviar = tk.Button(root, text="Enviar", command=enviar_pergunta)
btn_enviar.pack(pady=10)

label_resposta = tk.Label(root, text="Resposta:")
label_resposta.pack(pady=10)

texto_resposta = tk.Text(root, height=10, width=60, wrap=tk.WORD, state=tk.DISABLED)
texto_resposta.pack(pady=5)

# Iniciar o loop da interface
root.mainloop()
