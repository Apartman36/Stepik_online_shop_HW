from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

# Mock data
products = [
    {'id': 1, 'name': 'Product 1', 'description': 'Description 1', 'price': 9.99},
    {'id': 2, 'name': 'Product 2', 'description': 'Description 2', 'price': 19.99},
    {'id': 3, 'name': 'Product 3', 'description': 'Description 3', 'price': 29.99}
]

cart = []

# Endpoints for clients
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart.append(product)
        return jsonify({'message': 'Product added to cart'}), 200
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/cart', methods=['DELETE'])
def remove_from_cart():
    product_id = request.json.get('product_id')
    product = next((p for p in cart if p['id'] == product_id), None)
    if product:
        cart.remove(product)
        return jsonify({'message': 'Product removed from cart'}), 200
    else:
        return jsonify({'message': 'Product not found in cart'}), 404

@app.route('/order', methods=['POST'])
def place_order():
    email = request.json.get('email')
    if email:
        # Process order
        return jsonify({'message': 'Order placed successfully'}), 200
    else:
        return jsonify({'message': 'Email is required'}), 400

# Endpoints for managers and admins
@app.route('/login', methods=['POST'])
def login():
    if request.json.get('username') == 'admin' and request.json.get('password') == 'password':
        access_token = create_access_token(identity='admin')
        return jsonify({'access_token': access_token}), 200
    elif request.json.get('username') == 'manager' and request.json.get('password') == 'password':
        access_token = create_access_token(identity='manager')
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    current_user = get_jwt_identity()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        if current_user == 'admin':
            product['name'] = request.json.get('name', product['name'])
            product['description'] = request.json.get('description', product['description'])
            product['price'] = request.json.get('price', product['price'])
            return jsonify({'message': 'Product updated'}), 200
        elif current_user == 'manager':
            product['description'] = request.json.get('description', product['description'])
            product['price'] = request.json.get('price', product['price'])
            return jsonify({'message': 'Product updated'}), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    current_user = get_jwt_identity()
    if current_user == 'admin':
        product = {
            'id': len(products) + 1,
            'name': request.json.get('name'),
            'description': request.json.get('description'),
            'price': request.json.get('price')
        }
        products.append(product)
        return jsonify({'message': 'Product added'}), 201
    else:
        return jsonify({'message': 'Unauthorized'}), 403

if __name__ == '__main__':
    app.run(debug=True)