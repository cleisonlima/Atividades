import webbrowser
import urllib.parse
import tkinter as tk

# Função que pega o texto digitado e abre no YouTube
def pesquisar():
    termo = entrada.get()  # Pega o que o usuário digitou
    if termo.strip():  # Só executa se não estiver vazio
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(termo)}"
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        webbrowser.get(chrome_path).open(url)

# Criando a janela
janela = tk.Tk()
janela.title("Pesquisa no YouTube")
janela.geometry("300x150")

# Texto de instrução
label = tk.Label(janela, text="Digite o que deseja pesquisar:")
label.pack(pady=5)

# Campo de entrada
entrada = tk.Entry(janela, width=40)
entrada.pack(pady=5)

# Botão de pesquisa
botao = tk.Button(janela, text="Pesquisar", command=pesquisar)
botao.pack(pady=10)

# Inicia a interface
janela.mainloop()
