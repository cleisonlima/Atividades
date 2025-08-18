import tkinter as tk
from tkinter import messagebox

# Lista para armazenar as despesas
despesas = []

# Função para adicionar despesa
def adicionar_despesa():
    descricao = entrada_desc.get()
    valor = entrada_valor.get()

    if not descricao.strip() or not valor.strip():
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return
    
    try:
        valor = float(valor)
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")
        return

    despesas.append((descricao, valor))
    atualizar_lista()
    entrada_desc.delete(0, tk.END)
    entrada_valor.delete(0, tk.END)

# Atualizar lista e total
def atualizar_lista():
    lista_despesas.delete(0, tk.END)
    total = 0
    for desc, val in despesas:
        lista_despesas.insert(tk.END, f"{desc} - R$ {val:.2f}")
        total += val
    label_total.config(text=f"💰 Total gasto: R$ {total:.2f}")

# Remover despesa selecionada
def remover_despesa():
    try:
        indice = lista_despesas.curselection()[0]
        despesas.pop(indice)
        atualizar_lista()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma despesa para remover.")

# ===== INTERFACE =====
janela = tk.Tk()
janela.title("Controle de Gastos Pessoais")
janela.geometry("450x400")
janela.config(bg="#1e1e2f")

# Estilo
fonte_titulo = ("Arial", 18, "bold")
fonte_normal = ("Arial", 12)
cor_texto = "white"
cor_campo = "#2e2e3e"
cor_botao = "#4CAF50"
cor_botao_remover = "#E74C3C"

# Função para hover
def on_enter(e, cor):
    e.widget.config(bg=cor)

def on_leave(e, cor):
    e.widget.config(bg=cor)

# Título
tk.Label(janela, text="📊 Controle de Gastos", font=fonte_titulo, bg="#1e1e2f", fg=cor_texto).pack(pady=10)

# Campos
tk.Label(janela, text="Descrição:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
entrada_desc = tk.Entry(janela, font=fonte_normal, bg=cor_campo, fg=cor_texto, relief="flat", insertbackground="white")
entrada_desc.pack(pady=5)

tk.Label(janela, text="Valor (R$):", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
entrada_valor = tk.Entry(janela, font=fonte_normal, bg=cor_campo, fg=cor_texto, relief="flat", insertbackground="white")
entrada_valor.pack(pady=5)

# Botão adicionar
btn_add = tk.Button(janela, text="Adicionar", font=fonte_normal, bg=cor_botao, fg="white", relief="flat", command=adicionar_despesa)
btn_add.pack(pady=5)
btn_add.bind("<Enter>", lambda e: on_enter(e, "#45a049"))
btn_add.bind("<Leave>", lambda e: on_leave(e, cor_botao))

# Lista
lista_despesas = tk.Listbox(janela, font=fonte_normal, bg=cor_campo, fg=cor_texto, relief="flat", width=40, height=8)
lista_despesas.pack(pady=10)

# Botão remover
btn_remover = tk.Button(janela, text="Remover", font=fonte_normal, bg=cor_botao_remover, fg="white", relief="flat", command=remover_despesa)
btn_remover.pack(pady=5)
btn_remover.bind("<Enter>", lambda e: on_enter(e, "#c0392b"))
btn_remover.bind("<Leave>", lambda e: on_leave(e, cor_botao_remover))

# Total
label_total = tk.Label(janela, text="💰 Total gasto: R$ 0.00", font=fonte_normal, bg="#1e1e2f", fg=cor_texto)
label_total.pack(pady=10)

janela.mainloop()
