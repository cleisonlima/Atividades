import webbrowser
import urllib.parse
from datetime import datetime

cidade = "Paulista"
data_hoje = datetime.now().strftime("%d/%m/%Y")
pesquisa = f"tempo hoje {cidade} {data_hoje}"
url = f"https://www.google.com/search?q={urllib.parse.quote(pesquisa)}"
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
webbrowser.get(chrome_path).open(url)
