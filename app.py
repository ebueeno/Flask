from flask import Flask,jsonify,request
from flask_httpauth import HTTPBasicAuth
from flasgger import Swagger

app = Flask(__name__)

app.config['SWAGGER'] = {
    'title':'My flask API',
    'uiversion':3
}

swagger = Swagger(app)

users ={
    "user1":"senha1",
    "user2":"senha2"
}

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username,password):
    if username in users and users[username] == password:
        return username

@app.route('/')
def home():
    return "Hello, flask"

@app.route('/hello',methods=['GET'])
@auth.login_required
def hello():
    return jsonify({"message":"Hello, World!"})

items = []
@app.route('/items', methods=['GET'])
def get_imtes():
    return jsonify(items) #Retorna a lista como um Json

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    items.append(data)
    return jsonify(data), 201

@app.route('/items/<int:item_id>',methods=['PUT'])
def update_item(item_id): #identifica o item pelo indice<int:item_id>
    data = request.get_json()
    if 0 <= item_id <len(items): # Valida de o id está em um intervalo valido 
        items[item_id].update(data)
        return jsonify(items[item_id])
    return jsonify({'error':'Item not found'}), 404

@app.route('/items/<int:item_id>',methods=['DELETE'])
def delete_item(item_id):
    if 0 <= item_id < len (items):
        removed = items.pop(item_id)
        return jsonify(removed)
    return jsonify({"error":"Item not found"}),404


if __name__ == '__main__':
    app.run(debug=True)