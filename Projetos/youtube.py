# Importa as bibliotecas necessárias
import webbrowser      # Para abrir links no navegador
import urllib.parse    # Para codificar textos em formato de URL

# Texto que será pesquisado no YouTube
pesquisa = "música relaxante"

url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(pesquisa)}"
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
webbrowser.get(chrome_path).open(url)
