# Importa as bibliotecas necessárias
import webbrowser      # Para abrir links no navegador
import urllib.parse    # Para codificar textos em formato de URL

# Texto que será pesquisado no YouTube
pesquisa = "música relaxante"

# Monta o link de pesquisa do YouTube já codificando o texto para URL
# Exemplo: "música relaxante" vira "m%C3%BAsica+relaxante"
url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(pesquisa)}"

# Caminho do executável do Google Chrome no Windows
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"

# Abre o Chrome com a pesquisa feita no YouTube
webbrowser.get(chrome_path).open(url)
