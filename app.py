from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_sinonimos(word):
    """
    Função para buscar sinônimos de uma palavra no site sinonimos.com.br.
    """
    url = f"https://www.sinonimos.com.br/{word}/"
    try:
        response = requests.get(url, timeout=5) # Adicionado timeout para evitar que a requisição demore demais
        response.raise_for_status() # Lança um erro para status de erro HTTP
        soup = BeautifulSoup(response.text, "html.parser")
        p_syn_list = soup.find("p", class_="syn-list syn-list-1")
        if p_syn_list:
            sinonimos = [a.text.strip() for a in p_syn_list.find_all("a", class_="sinonimo")]
            return sinonimos
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    sinonimos = []
    palavra_buscada = ""
    if request.method == 'POST':
        palavra = request.form.get('palavra')
        if palavra:
            palavra_buscada = palavra
            sinonimos_encontrados = get_sinonimos(palavra)
            if sinonimos_encontrados is not None:
                sinonimos = sinonimos_encontrados
            else:
                sinonimos = ["Não foi possível buscar os sinônimos. Tente novamente mais tarde."]
        else:
            sinonimos = ["Por favor, digite uma palavra para buscar."]
    return render_template('index.html', sinonimos=sinonimos, palavra_buscada=palavra_buscada)

if __name__ == '__main__':
    app.run(debug=True) # debug=True recarrega o servidor automaticamente a cada alteração