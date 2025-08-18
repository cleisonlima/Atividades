import tkinter as tk
from tkinter import messagebox
import requests
import pyperclip

# Função para encurtar link
def encurtar_link():
    url_original = entrada.get()
    
    if not url_original.strip():
        messagebox.showwarning("Aviso", "Digite um link para encurtar.")
        return

    try:
        api_url = f"https://tinyurl.com/api-create.php?url={url_original}"
        resposta = requests.get(api_url)
        
        if resposta.status_code == 200:
            link_encurtado = resposta.text
            resultado.config(state="normal")
            resultado.delete(0, tk.END)
            resultado.insert(0, link_encurtado)
            resultado.config(state="readonly")
        else:
            messagebox.showerror("Erro", "Não foi possível encurtar o link.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao encurtar link: {e}")

# Função para copiar link
def copiar_link():
    link = resultado.get()
    if link:
        pyperclip.copy(link)
        messagebox.showinfo("Copiado", "Link copiado para a área de transferência!")

# Janela principal
janela = tk.Tk()
janela.title("Encurtador de Links")
janela.geometry("450x250")
janela.config(bg="#1e1e2f")

# Estilo
fonte_titulo = ("Arial", 18, "bold")
fonte_normal = ("Arial", 12)
cor_botao = "#4CAF50"
cor_botao_hover = "#45a049"
cor_texto = "white"

# Função para hover
def on_enter(e, cor):
    e.widget.config(bg=cor_botao_hover)

def on_leave(e, cor):
    e.widget.config(bg=cor)

# Título
tk.Label(janela, text="🔗 Encurtador de Links", font=fonte_titulo, bg="#1e1e2f", fg=cor_texto).pack(pady=10)

# Campo para digitar link
tk.Label(janela, text="Digite o link:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
entrada = tk.Entry(janela, width=50, font=fonte_normal, relief="flat", bg="#2e2e3e", fg=cor_texto, insertbackground="white")
entrada.pack(pady=5)

# Botão encurtar
btn_encurtar = tk.Button(janela, text="Encurtar", font=fonte_normal, bg=cor_botao, fg="white", relief="flat", command=encurtar_link)
btn_encurtar.pack(pady=5)
btn_encurtar.bind("<Enter>", lambda e: on_enter(e, cor_botao))
btn_encurtar.bind("<Leave>", lambda e: on_leave(e, cor_botao))

# Resultado
tk.Label(janela, text="Link encurtado:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
resultado = tk.Entry(
    janela,
    width=50,
    font=fonte_normal,
    relief="flat",
    bg="#2e2e3e",
    fg=cor_texto,
    readonlybackground="#2e2e3e",  # 🔹 Fundo para modo readonly
    insertbackground="white",
    state="readonly"
)
resultado.pack(pady=5)

# Botão copiar
btn_copiar = tk.Button(janela, text="Copiar", font=fonte_normal, bg="#2196F3", fg="white", relief="flat", command=copiar_link)
btn_copiar.pack(pady=5)
btn_copiar.bind("<Enter>", lambda e: on_enter(e, "#2196F3"))
btn_copiar.bind("<Leave>", lambda e: on_leave(e, "#2196F3"))

janela.mainloop()
