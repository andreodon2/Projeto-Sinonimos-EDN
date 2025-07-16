import requests
from bs4 import BeautifulSoup

def get_sinonimos(word):
    url = f"https://www.sinonimos.com.br/{word}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        p_syn_list = soup.find("p", class_="syn-list syn-list-1")
        if p_syn_list:
            sinonimos = [a.text.strip() for a in p_syn_list.find_all("a", class_="sinonimo")]
            return sinonimos
        else:
            return []
    else:
        return None

palavra = input("Digite a palavra: ")
sinonimos = get_sinonimos(palavra)
if sinonimos:
    print("Sinônimos encontrados:", sinonimos)
else:
    print("Nenhum sinônimo encontrado.")
