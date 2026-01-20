from flask import Flask, jsonify, request, render_template
from collections import deque
import os

app = Flask(__name__)

# Product Class
class Product:
    def __init__(self, product_id, name, category, price, stock=1):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = float(price)
        self.stock = int(stock)
        self.next = None  # Linked list pointer

# ProductList Class (managing product) // Linked List No. 1
class ProductList:
    def __init__(self):
        self.head = None

    def add_product(self, product_id, name, category, price, stock=1):
        try:
            stock = int(stock) 
        except ValueError:
            raise ValueError("Stock must be a valid integer")

        new_product = Product(product_id, name, category, price, stock)

        if not self.head:
            self.head = new_product
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_product

        # After adding the product, sort the list alphabetically
        self.head = self.merge_sort(self.head)

    def merge_sort(self, head):
        if not head or not head.next:
            return head

        middle = self.get_middle(head)
        next_to_middle = middle.next
        middle.next = None

        left = self.merge_sort(head)
        right = self.merge_sort(next_to_middle)

        sorted_list = self.merge(left, right)
        return sorted_list

    def get_middle(self, head):
        if not head:
            return head

        slow = head
        fast = head

        while fast.next and fast.next.next:
            slow = slow.next
            fast = fast.next.next

        return slow

    def merge(self, left, right):
        if not left:
            return right
        if not right:
            return left

        if left.name <= right.name:
            result = left
            result.next = self.merge(left.next, right)
        else:
            result = right
            result.next = self.merge(left, right.next)

        return result

    def find_product(self, product_id):
        current = self.head
        while current:
            if current.product_id == product_id:
                return current
            current = current.next
        return None

    def delete_product(self, product_id):
        current = self.head
        prev = None
        while current:
            if current.product_id == product_id:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                return True
            prev = current
            current = current.next
        return False

    def update_product(self, product_id, name=None, category=None, price=None, stock=None):
        product = self.find_product(product_id)
        if product:
            if name:
                product.name = name
            if category:
                product.category = category
            if price is not None:
                product.price = float(price)
            if stock is not None:
                product.stock = int(stock)
            return True
        return False

    def get_products(self):
        products = []
        current = self.head
        while current:
            products.append({
                'product_id': current.product_id,
                'name': current.name,
                'category': current.category,
                'price': current.price,
                'stock': current.stock,
            })
            current = current.next
        return products

# Customer Class
class Customer:
    def __init__(self, customer_id, name):
        self.customer_id = customer_id
        self.name = name
        self.purchased_items = []  # List of purchased Product nodes
        self.next = None  # Pointer to the next Customer node

# CustomerList Class (managing customers) // Linked List No. 2
class CustomerList:
    def __init__(self):
        self.head = None

    def add_customer(self, customer_id, name):
        new_customer = Customer(customer_id, name)
        if not self.head:
            self.head = new_customer
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_customer

    def find_customer(self, customer_id):
        current = self.head
        while current:
            if current.customer_id == customer_id:
                return current
            current = current.next
        return None

# Stack Class for Undo/Redo // Stack 
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def clear(self):
        self.items = []

# Queue Class // Queue
class Queue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.popleft()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def clear(self):
        self.items.clear()


# Initialize Product and Customer Lists
product_list = ProductList()
customer_list = CustomerList()

# Initialize Stacks for Undo/Redo
undo_stack = Stack()
redo_stack = Stack()

# Initialize the Restock Queue
restock_queue = Queue()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def list_products():
    products = product_list.get_products()
    return jsonify(products)

@app.route('/products/add', methods=['POST'])
def add_product():
    data = request.json
    product_id = data.get('product_id')
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    stock = data.get('stock', 1)

    try:
        product_list.add_product(product_id, name, category, price, stock)
        
        # Add the product to the undo stack
        undo_stack.push({
            'action': 'add_product',
            'product': {'product_id': product_id, 'name': name, 'category': category, 'price': price, 'stock': stock}
        })
        redo_stack.clear()

        return jsonify({'message': 'Product added successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/products/edit', methods=['POST'])
def edit_product():
    data = request.json
    product_id = data.get('product_id')
    product = product_list.find_product(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Save current state before editing
    previous_state = {
        'product_id': product.product_id,
        'name': product.name,
        'category': product.category,
        'price': product.price,
        'stock': product.stock
    }

    product_list.update_product(
        product_id,
        name=data.get('name'),
        category=data.get('category'),
        price=data.get('price'),
        stock=data.get('stock')
    )

    # Add the edit operation to the undo stack
    undo_stack.push({'action': 'edit_product', 'previous': previous_state})
    redo_stack.clear()

    return jsonify({'message': 'Product updated successfully'}), 200

@app.route('/customers/register', methods=['POST'])
def register_customer():
    data = request.json
    customer_id = data.get('customer_id')
    name = data.get('name')

    if customer_list.find_customer(customer_id):
        return jsonify({'error': 'Customer already registered'}), 400

    customer_list.add_customer(customer_id, name)
    
    # Add the customer registration to the undo stack
    undo_stack.push({
        'action': 'register_customer',
        'customer': {'customer_id': customer_id, 'name': name}
    })
    redo_stack.clear()
    return jsonify({'message': 'Customer registered successfully'}), 201

@app.route('/products/sell', methods=['POST'])
def sell_product():
    data = request.json
    product_id = data.get('product_id')
    customer_id = data.get('customer_id')
    quantity = int(data.get('quantity', 1))

    product = product_list.find_product(product_id)
    customer = customer_list.find_customer(customer_id)

    if not product:
        return jsonify({'error': 'Product not found.'}), 400

    if not customer:
        return jsonify({'error': 'Customer not registered.'}), 400

    if product.stock >= quantity:
        product.stock -= quantity
        for _ in range(quantity):
            customer.purchased_items.append(product)

        # Track the sell action for undo
        undo_stack.push({'action': 'sell', 'product': product, 'customer': customer, 'quantity': quantity})
        
        # Clear redo stack after the new action
        redo_stack.clear()

        return jsonify({'message': f"Sold {quantity} of '{product.name}' to '{customer.name}'."}), 200
    else:
        return jsonify({'error': 'Not enough stock available.'}), 400

@app.route('/products/restock', methods=['POST'])
def add_restock_request():
    data = request.json
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    product = product_list.find_product(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    restock_queue.enqueue({'product_id': product_id, 'quantity': quantity})
    return jsonify({'message': f'Restock request added for {quantity} of {product.name}.'}), 201

@app.route('/products/restock/process', methods=['POST'])
def process_restock_request():
    if restock_queue.is_empty():
        return jsonify({'error': 'No restock requests in the queue'}), 400

    restock_request = restock_queue.dequeue()
    product_id = restock_request['product_id']
    quantity = restock_request['quantity']

    product = product_list.find_product(product_id)
    if product:
        product.stock += quantity
        return jsonify({'message': f'Successfully restocked {quantity} of {product.name}.'}), 200
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/products/restock/queue', methods=['GET'])
def view_restock_queue():
    queue_items = list(restock_queue.items)
    return jsonify(queue_items)

@app.route('/products/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '').lower()
    products = product_list.get_products()
    filtered_products = [
        product for product in products 
        if query in product['name'].lower() or query in product['category'].lower()
    ]
    return jsonify(filtered_products)

@app.route('/customers/search', methods=['GET'])
def search_customers():
    query = request.args.get('query', '').lower()
    customers = []
    current = customer_list.head
    while current:
        if query in current.name.lower():
            customers.append({'customer_id': current.customer_id, 'name': current.name})
        current = current.next
    return jsonify(customers)

@app.route('/undo', methods=['POST'])
def undo():
    if undo_stack.is_empty():
        return jsonify({'error': 'No actions to undo'}), 400

    action = undo_stack.pop() # Pop the last undone action
    redo_stack.push(action)  # Push the undone action to the redo stack

    if action['action'] == 'add_product':
        product = action['product']
        product_list.delete_product(product['product_id'])
    elif action['action'] == 'register_customer':
        customer = action['customer']
        current = customer_list.head
        prev = None
        while current:
            if current.customer_id == customer['customer_id']:
                if prev:
                    prev.next = current.next
                else:
                    customer_list.head = current.next
                break
            prev = current
            current = current.next
    elif action['action'] == 'edit_product':
        previous = action['previous']
        product_list.update_product(
            previous['product_id'],
            name=previous['name'],
            category=previous['category'],
            price=previous['price'],
            stock=previous['stock']
        )
    elif action['action'] == 'sell':
        product = action['product']
        customer = action['customer']
        quantity = action['quantity']

        # Revert stock and purchased items
        product.stock += quantity
        for _ in range(quantity):
            customer.purchased_items.pop()

    return jsonify({'message': 'Undo successful'}), 200


@app.route('/redo', methods=['POST'])
def redo():
    if redo_stack.is_empty():
        return jsonify({'error': 'No actions to redo'}), 400

    action = redo_stack.pop()  # Pop the last undone action
    undo_stack.push(action)  # Push it back onto the undo stack after reapplying

    if action['action'] == 'add_product':
        product = action['product']
        product_list.add_product(
            product['product_id'], product['name'], product['category'], product['price'], product['stock']
        )
    elif action['action'] == 'register_customer':
        customer = action['customer']
        customer_list.add_customer(customer['customer_id'], customer['name'])
    elif action['action'] == 'edit_product':
        updated = action.get('updated')
        product_list.update_product(
            updated['product_id'],
            name=updated.get('name'),
            category=updated.get('category'),
            price=updated.get('price'),
            stock=updated.get('stock')
        )
    elif action['action'] == 'sell':
        product = action['product']
        customer = action['customer']
        quantity = action['quantity']
        product.stock -= quantity  # Decrease the stock again
        for _ in range(quantity):
            customer.purchased_items.append(product)  # Add products back to the customer

    return jsonify({'message': 'Redo successful'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)