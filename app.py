from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_sinonimos(word):
    """
    Função para buscar sinônimos de uma palavra no site sinonimos.com.br.
    Tenta ser mais robusta para diferentes estruturas da página.
    """
    url = f"https://www.sinonimos.com.br/{word}/"

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP 4xx/5xx

        soup = BeautifulSoup(response.text, "html.parser")
        sinonimos = []

        # Tenta encontrar a lista de sinônimos principal (syn-list-1)
        p_syn_list_1 = soup.find("p", class_="syn-list syn-list-1")
        if p_syn_list_1:
            sinonimos.extend([a.text.strip() for a in p_syn_list_1.find_all("a", class_="sinonimo")])

        # Se não encontrar na primeira lista ou para adicionar mais, verifica outras possíveis listas
        # O site pode ter outras divs com sinônimos, por exemplo, para diferentes nuances.
        # Vamos ser um pouco mais genéricos e buscar por qualquer elemento com a classe 'syn-list'
        all_syn_lists = soup.find_all("p", class_="syn-list")
        for syn_list_p in all_syn_lists:
            # Garante que não estamos duplicando sinônimos já encontrados na syn-list-1
            new_sinonimos = [a.text.strip() for a in syn_list_p.find_all("a", class_="sinonimo") if a.text.strip() not in sinonimos]
            sinonimos.extend(new_sinonimos)

        # Se ainda não houver sinônimos, podemos tentar buscar em outro padrão
        # (ex: o site pode ter uma estrutura diferente para palavras sem muitas opções)
        if not sinonimos:
            # Por exemplo, às vezes os sinônimos podem estar em uma div mais genérica
            # ou até mesmo em parágrafos que não são 'syn-list' mas contêm links de sinônimos.
            # Esta parte é mais experimental e depende de como o site renderiza.
            # Você pode inspecionar o HTML do site para um verbo no infinitivo que não funciona.
            # Exemplo: alguns sinônimos podem estar em tags <li> dentro de um <ul>
            # Vamos buscar por links com a classe 'sinonimo' de forma mais ampla
            all_sinonimo_links = soup.find_all("a", class_="sinonimo")
            for link in all_sinonimo_links:
                sinonimo_text = link.text.strip()
                if sinonimo_text and sinonimo_text not in sinonimos:
                    sinonimos.append(sinonimo_text)


        if sinonimos:
            return list(set(sinonimos)) # Retorna a lista de sinônimos únicos
        else:
            return [] # Retorna lista vazia se nada for encontrado

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para {url}: {e}")
        return None # Retorna None em caso de erro na requisição
    except Exception as e:
        print(f"Ocorreu um erro ao processar a resposta para {url}: {e}")
        return None # Retorna None em caso de outros erros

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