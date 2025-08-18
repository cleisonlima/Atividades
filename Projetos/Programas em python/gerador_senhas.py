import tkinter as tk
from tkinter import messagebox
import secrets
import string

# tentar usar pyperclip para copiar; se não tiver, cai fora graciosamente
try:
    import pyperclip
    HAS_PYPERCLIP = True
except Exception:
    HAS_PYPERCLIP = False

# === lógica ===
def calcular_forca(senha: str) -> tuple[str, str]:
    """Retorna (texto, cor) para o indicador de força."""
    if not senha:
        return ("", "white")
    pontuacao = 0
    # comprimento
    n = len(senha)
    if n >= 16: pontuacao += 3
    elif n >= 12: pontuacao += 2
    elif n >= 8: pontuacao += 1

    # diversidade de caracteres
    classes = [
        any(c.islower() for c in senha),
        any(c.isupper() for c in senha),
        any(c.isdigit() for c in senha),
        any(c in string.punctuation for c in senha),
    ]
    pontuacao += sum(classes)

    if pontuacao >= 6:
        return ("Muito forte ✅", "#2ecc71")
    elif pontuacao >= 4:
        return ("Forte 👍", "#27ae60")
    elif pontuacao >= 3:
        return ("Média 😬", "#f39c12")
    else:
        return ("Fraca ❌", "#e74c3c")

def gerar_senha():
    tamanho = var_tamanho.get()
    usar_minus = var_minus.get()
    usar_maius = var_maius.get()
    usar_num = var_num.get()
    usar_simbolos = var_simbolos.get()

    pool = ""
    if usar_minus: pool += string.ascii_lowercase
    if usar_maius: pool += string.ascii_uppercase
    if usar_num: pool += string.digits
    if usar_simbolos: pool += string.punctuation

    if not pool:
        messagebox.showwarning("Aviso", "Selecione pelo menos um tipo de caractere.")
        return
    if tamanho < 4:
        messagebox.showwarning("Aviso", "Escolha um tamanho mínimo de 4.")
        return

    # garantir ao menos 1 de cada classe escolhida
    senha_chars = []
    if usar_minus: senha_chars.append(secrets.choice(string.ascii_lowercase))
    if usar_maius: senha_chars.append(secrets.choice(string.ascii_uppercase))
    if usar_num: senha_chars.append(secrets.choice(string.digits))
    if usar_simbolos: senha_chars.append(secrets.choice(string.punctuation))

    # completar o restante
    while len(senha_chars) < tamanho:
        senha_chars.append(secrets.choice(pool))

    # embaralhar de forma segura
    for i in range(len(senha_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        senha_chars[i], senha_chars[j] = senha_chars[j], senha_chars[i]

    senha = "".join(senha_chars)

    # mostrar
    saida.config(state="normal")
    saida.delete(0, tk.END)
    saida.insert(0, senha)
    saida.config(state="readonly")

    # força
    txt, cor = calcular_forca(senha)
    lbl_forca.config(text=f"Força: {txt}", fg=cor)

def copiar():
    senha = saida.get()
    if not senha:
        messagebox.showinfo("Copiar", "Nada para copiar.")
        return
    if HAS_PYPERCLIP:
        pyperclip.copy(senha)
        messagebox.showinfo("Copiado", "Senha copiada para a área de transferência! 🧷")
    else:
        # fallback: selecionar texto para Ctrl+C manual
        saida.config(state="normal")
        saida.selection_range(0, tk.END)
        saida.config(state="readonly")
        messagebox.showinfo("Atenção", "Instale 'pyperclip' para copiar automaticamente.\nUse Ctrl+C após o campo ficar selecionado.")

def limpar():
    saida.config(state="normal")
    saida.delete(0, tk.END)
    saida.config(state="readonly")
    lbl_forca.config(text="Força: ", fg="white")

def toggle_visibilidade():
    if var_ver.get():
        saida.config(show="")
    else:
        # show não afeta readonlybackground; só a exibição
        saida.config(show="•")

# === UI ===
janela = tk.Tk()
janela.title("Gerador de Senhas")
janela.geometry("520x430")
janela.config(bg="#1e1e2f")

fonte_titulo = ("Arial", 18, "bold")
fonte_normal = ("Arial", 12)
cor_texto = "white"
cor_campo = "#2e2e3e"
cor_botao = "#4CAF50"
cor_botao_sec = "#2196F3"
cor_botao_destr = "#E74C3C"

def hover_bind(widget, cor_base, cor_hover):
    widget.bind("<Enter>", lambda e: widget.config(bg=cor_hover))
    widget.bind("<Leave>", lambda e: widget.config(bg=cor_base))

# Título
tk.Label(janela, text="🔐 Gerador de Senhas", font=fonte_titulo, bg="#1e1e2f", fg=cor_texto).pack(pady=12)

# Frame de opções
frame = tk.Frame(janela, bg="#1e1e2f")
frame.pack(pady=5)

# Tamanho
tk.Label(frame, text="Tamanho:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).grid(row=0, column=0, sticky="w", padx=6, pady=6)
var_tamanho = tk.IntVar(value=12)
scale = tk.Scale(frame, from_=4, to=32, orient="horizontal", variable=var_tamanho,
                 bg="#1e1e2f", fg=cor_texto, troughcolor="#2e2e3e",
                 highlightthickness=0, length=260, relief="flat")
scale.grid(row=0, column=1, columnspan=3, padx=6, pady=6, sticky="we")

# Checkboxes
var_minus = tk.BooleanVar(value=True)
var_maius = tk.BooleanVar(value=True)
var_num = tk.BooleanVar(value=True)
var_simbolos = tk.BooleanVar(value=False)

chk_kwargs = dict(bg="#1e1e2f", fg=cor_texto, activebackground="#1e1e2f", selectcolor="#2e2e3e", font=fonte_normal)
tk.Checkbutton(frame, text="a-z", variable=var_minus, **chk_kwargs).grid(row=1, column=0, sticky="w", padx=6, pady=4)
tk.Checkbutton(frame, text="A-Z", variable=var_maius, **chk_kwargs).grid(row=1, column=1, sticky="w", padx=6, pady=4)
tk.Checkbutton(frame, text="0-9", variable=var_num, **chk_kwargs).grid(row=1, column=2, sticky="w", padx=6, pady=4)
tk.Checkbutton(frame, text="Símbolos", variable=var_simbolos, **chk_kwargs).grid(row=1, column=3, sticky="w", padx=6, pady=4)

# Saída (senha)
tk.Label(janela, text="Senha:", font=fonte_normal, bg="#1e1e2f", fg=cor_texto).pack(pady=(10, 2))
saida = tk.Entry(
    janela, font=("Consolas", 14), width=34, relief="flat",
    bg=cor_campo, fg=cor_texto, insertbackground="white",
    readonlybackground=cor_campo, state="readonly", show="•"
)
saida.pack(pady=4)

# Mostrar/ocultar
var_ver = tk.BooleanVar(value=False)
chk_ver = tk.Checkbutton(janela, text="Mostrar senha", variable=var_ver,
                         command=toggle_visibilidade, bg="#1e1e2f", fg=cor_texto,
                         activebackground="#1e1e2f", selectcolor="#2e2e3e", font=("Arial", 10))
chk_ver.pack()

# Indicador de força
lbl_forca = tk.Label(janela, text="Força: ", font=fonte_normal, bg="#1e1e2f", fg="white")
lbl_forca.pack(pady=6)

# Botões
btns = tk.Frame(janela, bg="#1e1e2f")
btns.pack(pady=8)

btn_gerar = tk.Button(btns, text="Gerar", font=fonte_normal, bg=cor_botao, fg="white", relief="flat", command=gerar_senha, padx=14, pady=6)
btn_gerar.grid(row=0, column=0, padx=6)
hover_bind(btn_gerar, cor_botao, "#45a049")

btn_copiar = tk.Button(btns, text="Copiar", font=fonte_normal, bg=cor_botao_sec, fg="white", relief="flat", command=copiar, padx=14, pady=6)
btn_copiar.grid(row=0, column=1, padx=6)
hover_bind(btn_copiar, cor_botao_sec, "#1e88e5")

btn_limpar = tk.Button(btns, text="Limpar", font=fonte_normal, bg=cor_botao_destr, fg="white", relief="flat", command=limpar, padx=14, pady=6)
btn_limpar.grid(row=0, column=2, padx=6)
hover_bind(btn_limpar, cor_botao_destr, "#c0392b")

# rodapé
tk.Label(janela, text="Dica: combine tamanho + diversidade para senhas melhores ✨",
         font=("Arial", 10), bg="#1e1e2f", fg="#bdc3c7").pack(pady=10)

janela.mainloop()
