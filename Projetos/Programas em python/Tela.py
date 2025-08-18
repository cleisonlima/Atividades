import tkinter as tk
import webbrowser
import os

# Caminho absoluto para o arquivo index.html
caminho_html = os.path.abspath("index.html")

def abrir_jogo():
    webbrowser.open(f"index.html")

# Criar a janela principal
janela = tk.Tk()
janela.title("Abrir Livro - Crônicas do Vácuo")
janela.geometry("400x200")
janela.configure(bg="#1c1c1c")

# Título
label = tk.Label(
    janela,
    text="🌌 Crônicas do Vácuo 🌌",
    font=("Arial", 16, "bold"),
    fg="yellow",
    bg="#1c1c1c"
)
label.pack(pady=20)

# Botão para abrir o Livro
botao = tk.Button(
    janela,
    text="Abrir Livro",
    font=("Arial", 14),
    bg="yellow",
    fg="black",
    command=abrir_jogo
)
botao.pack(pady=20)

janela.mainloop()
