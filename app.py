from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flasgger import Swagger
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

app.config['SWAGGER'] = {
    'title': 'My flask API',
    'uiversion': 3
}

swagger = Swagger(app)

users = {
    "user1": "senha1",
    "user2": "senha2"
}

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username


@app.route('/')
def home():
    return "Hello, flask"


@app.route('/hello', methods=['GET'])
@auth.login_required
def hello():
    return jsonify({"message": "Hello, World!"})


items = []


@app.route('/items', methods=['GET'])
def get_imtes():
    return jsonify(items)  # Retorna a lista como um Json


@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    items.append(data)
    return jsonify(data), 201


@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):  # identifica o item pelo indice<int:item_id>
    data = request.get_json()
    if 0 <= item_id < len(items):  # Valida de o id está em um intervalo valido
        items[item_id].update(data)
        return jsonify(items[item_id])
    return jsonify({'error': 'Item not found'}), 404


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if 0 <= item_id < len(items):
        removed = items.pop(item_id)
        return jsonify(removed)
    return jsonify({"error": "Item not found"}), 404


def get_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headers = []
        for header_tag in ['h1', 'h2', 'h3']:
            for header in soup.find_all(header_tag):
                headers.append(header.get_text(strip=True))
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        return jsonify({'heades': headers, 'paragraphs': paragraphs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/scrape/content', methods=['GET'])
@auth.login_required
def scrape_content():
    """
    Extrai cabeçalhos e parágrafos de um site fornecido pela URL
    ---
    security:
      - BasicAuth: []
    parameters:
      - name: url
        in: query
        type: string
        required: true
        description: URL de um site
    responses:
      200:
        description: Conteúdo da página web
    """
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    return get_content(url)


if __name__ == '__main__':
    app.run(debug=True)
