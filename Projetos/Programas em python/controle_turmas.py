import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3

# ===== Banco de dados =====
conn = sqlite3.connect("turmas.db")
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute("""
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    alunos INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS atividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turma_id INTEGER,
    nome TEXT,
    data TEXT,
    concluida INTEGER DEFAULT 0,
    FOREIGN KEY(turma_id) REFERENCES turmas(id)
)
""")
conn.commit()

# ===== Funções =====
def atualizar_lista_turmas():
    lista_turmas.delete(0, tk.END)
    cursor.execute("SELECT nome FROM turmas ORDER BY nome")
    for t in cursor.fetchall():
        lista_turmas.insert(tk.END, t[0])

def adicionar_turma():
    nome = entrada_turma.get().strip()
    alunos = entrada_alunos.get().strip()

    if not nome or not alunos:
        messagebox.showwarning("Aviso", "Preencha todos os campos da turma.")
        return
    
    try:
        alunos = int(alunos)
    except ValueError:
        messagebox.showerror("Erro", "Quantidade de alunos deve ser numérica.")
        return

    try:
        cursor.execute("INSERT INTO turmas (nome, alunos) VALUES (?, ?)", (nome, alunos))
        conn.commit()
        atualizar_lista_turmas()
        entrada_turma.delete(0, tk.END)
        entrada_alunos.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showwarning("Aviso", "Turma já cadastrada.")

def remover_turma():
    try:
        nome = lista_turmas.get(lista_turmas.curselection()[0])
        cursor.execute("SELECT id FROM turmas WHERE nome=?", (nome,))
        turma_id = cursor.fetchone()[0]

        cursor.execute("DELETE FROM atividades WHERE turma_id=?", (turma_id,))
        cursor.execute("DELETE FROM turmas WHERE id=?", (turma_id,))
        conn.commit()
        atualizar_lista_turmas()
        lista_atividades.delete(0, tk.END)
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma turma para remover.")

def selecionar_turma(event):
    lista_atividades.delete(0, tk.END)
    try:
        nome = lista_turmas.get(lista_turmas.curselection()[0])
        cursor.execute("SELECT id FROM turmas WHERE nome=?", (nome,))
        turma_id = cursor.fetchone()[0]

        cursor.execute("SELECT nome, data, concluida FROM atividades WHERE turma_id=? ORDER BY data", (turma_id,))
        for i, a in enumerate(cursor.fetchall()):
            status = "✅" if a[2] else "❌"
            lista_atividades.insert(tk.END, f"{i+1}. {a[0]} ({a[1]}) [{status}]")
    except IndexError:
        pass

def adicionar_atividade():
    try:
        nome_turma = lista_turmas.get(lista_turmas.curselection()[0])
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma turma primeiro.")
        return

    nome = entrada_atividade.get().strip()
    data = entrada_data.get().strip()

    if not nome or not data:
        messagebox.showwarning("Aviso", "Preencha todos os campos da atividade.")
        return

    try:
        datetime.strptime(data, "%d/%m/%Y")
    except ValueError:
        messagebox.showerror("Erro", "Data inválida. Use DD/MM/AAAA.")
        return

    cursor.execute("SELECT id FROM turmas WHERE nome=?", (nome_turma,))
    turma_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO atividades (turma_id, nome, data) VALUES (?, ?, ?)", (turma_id, nome, data))
    conn.commit()
    selecionar_turma(None)
    entrada_atividade.delete(0, tk.END)
    entrada_data.delete(0, tk.END)

def remover_atividade():
    try:
        nome_turma = lista_turmas.get(lista_turmas.curselection()[0])
        indice = lista_atividades.curselection()[0]
        cursor.execute("SELECT id FROM turmas WHERE nome=?", (nome_turma,))
        turma_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM atividades WHERE turma_id=? ORDER BY data", (turma_id,))
        atividade_id = cursor.fetchall()[indice][0]

        cursor.execute("DELETE FROM atividades WHERE id=?", (atividade_id,))
        conn.commit()
        selecionar_turma(None)
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma atividade para remover.")

def concluir_atividade():
    try:
        nome_turma = lista_turmas.get(lista_turmas.curselection()[0])
        indice = lista_atividades.curselection()[0]
        cursor.execute("SELECT id FROM turmas WHERE nome=?", (nome_turma,))
        turma_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM atividades WHERE turma_id=? ORDER BY data", (turma_id,))
        atividade_id = cursor.fetchall()[indice][0]

        cursor.execute("UPDATE atividades SET concluida=1 WHERE id=?", (atividade_id,))
        conn.commit()
        selecionar_turma(None)
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma atividade para concluir.")

# ===== Interface =====
janela = tk.Tk()
janela.title("Controle de Turmas e Atividades")
janela.geometry("700x500")
janela.config(bg="#1e1e2f")

fonte_titulo = ("Arial", 18, "bold")
fonte_normal = ("Arial", 12)
cor_texto = "white"
cor_campo = "#2e2e3e"
cor_botao = "#4CAF50"
cor_botao_sec = "#2196F3"
cor_botao_destr = "#E74C3C"

# Título
tk.Label(janela, text="🎓 Controle de Turmas e Atividades", font=fonte_titulo, bg="#1e1e2f", fg=cor_texto).pack(pady=10)

# Frames
frame_turmas = tk.Frame(janela, bg="#1e1e2f")
frame_turmas.pack(side="left", padx=10, pady=5, fill="y")

frame_atividades = tk.Frame(janela, bg="#1e1e2f")
frame_atividades.pack(side="right", padx=10, pady=5, fill="both", expand=True)

# ==== Turmas ====
tk.Label(frame_turmas, text="Turmas", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
lista_turmas = tk.Listbox(frame_turmas, font=fonte_normal, bg=cor_campo, fg=cor_texto, width=25, height=15, relief="flat")
lista_turmas.pack(pady=5)
lista_turmas.bind("<<ListboxSelect>>", selecionar_turma)

tk.Label(frame_turmas, text="Nome da turma:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
entrada_turma = tk.Entry(frame_turmas, font=fonte_normal, bg=cor_campo, fg=cor_texto, relief="flat", insertbackground="white")
entrada_turma.pack(pady=2)

tk.Label(frame_turmas, text="Qtd. de alunos:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
entrada_alunos = tk.Entry(frame_turmas, font=fonte_normal, bg=cor_campo, fg=cor_texto, relief="flat", insertbackground="white")
entrada_alunos.pack(pady=2)

btn_add_turma = tk.Button(frame_turmas, text="Adicionar", font=fonte_normal, bg=cor_botao, fg="white", relief="flat", command=adicionar_turma)
btn_add_turma.pack(pady=2)
btn_rem_turma = tk.Button(frame_turmas, text="Remover", font=fonte_normal, bg=cor_botao_destr, fg="white", relief="flat", command=remover_turma)
btn_rem_turma.pack(pady=2)

# ==== Atividades ====
tk.Label(frame_atividades, text="Atividades", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
lista_atividades = tk.Listbox(frame_atividades, font=fonte_normal, bg=cor_campo, fg=cor_texto, width=50, height=15, relief="flat")
lista_atividades.pack(pady=5)

tk.Label(frame_atividades, text="Nome da atividade:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
entrada_atividade = tk.Entry(frame_atividades, font=fonte_normal, bg=cor_campo, fg=cor_texto, relief="flat", insertbackground="white")
entrada_atividade.pack(pady=2)

tk.Label(frame_atividades, text="Data (DD/MM/AAAA):", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack()
entrada_data = tk.Entry(frame_atividades, font=fonte_normal, bg=cor_campo, fg=cor_texto, relief="flat", insertbackground="white")
entrada_data.pack(pady=2)

frame_btns = tk.Frame(frame_atividades, bg="#1e1e2f")
frame_btns.pack(pady=5)

btn_add_atividade = tk.Button(frame_btns, text="Adicionar", font=fonte_normal, bg=cor_botao, fg="white", relief="flat", command=adicionar_atividade)
btn_add_atividade.grid(row=0, column=0, padx=5)
btn_rem_atividade = tk.Button(frame_btns, text="Remover", font=fonte_normal, bg=cor_botao_destr, fg="white", relief="flat", command=remover_atividade)
btn_rem_atividade.grid(row=0, column=1, padx=5)
btn_concluir = tk.Button(frame_btns, text="Concluir", font=fonte_normal, bg=cor_botao_sec, fg="white", relief="flat", command=concluir_atividade)
btn_concluir.grid(row=0, column=2, padx=5)

# Atualizar lista ao iniciar
atualizar_lista_turmas()

janela.mainloop()
conn.close()
