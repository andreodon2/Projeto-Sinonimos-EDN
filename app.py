import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)


def get_sinonimos(palavra):
    url = f"https://www.sinonimos.com.br/{palavra}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        p_syn_list = soup.find("p", class_="syn-list syn-list-1")
        if not p_syn_list:
            return []
        sinonimos = [
            a.text.strip()
            for a in p_syn_list.find_all("a", class_="sinonimo")]
        return sinonimos
    except Exception as e:
        print(f"Erro ao buscar sinônimos: {e}")
        return []


@app.route('/', methods=['GET', 'POST'])
def index():
    sinonimos = []
    palavra = ''
    if request.method == 'POST':
        palavra = request.form.get('palavra', '').strip().lower()
        if palavra:
            sinonimos = get_sinonimos(palavra)
    return render_template('index.html', sinonimos=sinonimos, palavra=palavra)


@app.route("/about-project/")
def about_project():
    return render_template("projeto.html")


@app.route("/about-we/")
def about_we():
    return render_template("quem-somos-nos.html")


if __name__ == '__main__':
    app.run(debug=True)
