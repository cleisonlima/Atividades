# 📝 Atividade - Desenvolvimento em Python com Tkinter

Desenvolver, utilizando **Python** e **Tkinter**, um dos seguintes aplicativos funcionais:

1. 🔑 Gerador de Senhas Seguras  
2. 🌍 Tradutor de Idiomas  
3. ✅ Checklist de Tarefas  

---

## ⚙️ Conversão do Script Python para Executável (.exe)

### 📦 Instalar o PyInstaller
```bash
python -m pip install pyinstaller



python -m PyInstaller --onefile --noconsole gerador_senha.py 


python -m PyInstaller --onefile --noconsole --icon=chave.ico gerador_senha.py

```

## 🔑 Gerador de Senhas Seguras (Tkinter + Python)
```python
import tkinter as tk
import random
import string

def gerar_senha():
    tamanho = 12
    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho))
    entry_senha.delete(0, tk.END)
    entry_senha.insert(0, senha)

root = tk.Tk()
root.title("Gerador de Senhas Seguras")

btn = tk.Button(root, text="Gerar Senha", command=gerar_senha)
btn.pack(pady=10)

entry_senha = tk.Entry(root, width=30)
entry_senha.pack(pady=10)

root.mainloop()
```



