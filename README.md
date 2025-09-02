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

# 🛠 Guia de Comandos para Desenvolvimento Front-end e Back-end

Este guia reúne os **principais comandos** para React.js, React Native, Angular, Node.js, SQL e Git, servindo como referência rápida para desenvolvimento web e mobile.

---

## 1️⃣ React.js (Front-end Web)

| Comando | O que faz |
|---------|-----------|
| `npx create-react-app meu-app` | Cria um projeto React tradicional |
| `npm start` | Roda o projeto localmente (porta 3000) |
| `npm run build` | Gera a versão final pronta para produção |
| `npm install <pacote>` | Instala bibliotecas adicionais |
| `npx serve -s build` | Serve a versão de produção localmente |
| `npm test` | Roda os testes automatizados |

**Observação:** React usa **JSX** e componentes, com arquivos principais `App.js` e `index.js`.

---

## 2️⃣ React Native (Mobile)

| Comando | O que faz |
|---------|-----------|
| `npx react-native init MeuApp` | Cria um projeto React Native (Android/iOS) |
| `npx react-native run-android` | Roda o app no emulador ou dispositivo Android |
| `npx react-native run-ios` | Roda o app no emulador iOS (macOS) |
| `npx react-native start` | Inicia o Metro Bundler (servidor do React Native) |
| `npm install <pacote>` | Instala bibliotecas adicionais |
| `npx react-native link <pacote>` | Linka pacotes nativos |

**Observação:** Para mobile, é necessário Android Studio, Xcode ou dispositivo físico.

---

## 3️⃣ Angular (Front-end Web)

| Comando | O que faz |
|---------|-----------|
| `npm install -g @angular/cli` | Instala Angular CLI globalmente |
| `ng new meu-projeto` | Cria um projeto Angular novo |
| `ng serve` | Roda o projeto localmente (porta 4200) |
| `ng build` | Gera a versão de produção |
| `ng generate component <nome>` | Cria um componente Angular |
| `ng generate service <nome>` | Cria um serviço Angular |
| `ng version` | Mostra versão do Angular |

---

## 4️⃣ Node.js / Back-end

| Comando | O que faz |
|---------|-----------|
| `node app.js` | Roda um arquivo JS no Node |
| `npm init` | Cria um `package.json` |
| `npm install express` | Instala Express.js (framework web) |
| `npm install <pacote>` | Instala qualquer pacote do npm |
| `npm start` | Roda o script principal do projeto |
| `npm run <script>` | Roda scripts definidos no `package.json` |

**Exemplo de servidor Express:**
```js
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => res.send('Olá Mundo!'));

app.listen(port, () => console.log(`Servidor rodando na porta ${port}`));



