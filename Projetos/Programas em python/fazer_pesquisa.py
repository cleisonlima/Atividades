# Importa bibliotecas necessárias
import webbrowser      # Para abrir links no navegador
import urllib.parse    # Para codificar textos em formato de URL
from datetime import datetime  # Para pegar a data atual

# Define a cidade que será pesquisada
cidade = "Recife"

# Pega a data de hoje no formato DD/MM/AAAA
data_hoje = datetime.now().strftime("%d/%m/%Y")

# Monta o texto da pesquisa com cidade e data
pesquisa = f"tempo hoje {cidade} {data_hoje}"

# Codifica o texto para o formato de URL (substitui espaços por %20, etc.)
url = f"https://www.google.com/search?q={urllib.parse.quote(pesquisa)}"

# Caminho do executável do Google Chrome no Windows
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"

# Abre o navegador Chrome com a pesquisa feita
webbrowser.get(chrome_path).open(url)
