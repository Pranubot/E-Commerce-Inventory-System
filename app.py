from flask import Flask, request, jsonify, abort

app = Flask(__name__) 

# Our classes for the in-memory database
products = {}
warehouses = {}
inventory = {}

# endpoints, used internet and ChatGPT to help create these endpoints

#for my reference, status codes:
# 201 - Created
# 204 - No Content
# 400 - Bad Request
# 404 - Not Found

#ENDPOINTS FOR PRODUCTS
@app.route('/api/products', methods = ['GET']) # get all products
def get_all_products():
    return jsonify([product for product in products.values()])

@app.route('/api/products/<sku>', methods = ['GET']) # get product by sku
def get_product(sku):
    product = products.get(sku)
    if not product:
        abort(404, description = f"Product {sku} not found") # error handling in all endpoints (found on internet)
    return jsonify(product)

@app.route('/api/products', methods = ['POST']) # allows user to create product
def create_product():
    data = request.get_json()
    sku = data['sku']
    if sku in products:
        abort(400, description = "Product SKU already exists")
    products[sku] = data
    return jsonify(data), 201

@app.route('/api/products/<sku>', methods = ['PUT']) # update product (identify by sku)
def update_product(sku):
    if sku not in products:
        abort(404, description = "Product not found")
    data = request.get_json()
    products[sku].update(data)
    return jsonify(products[sku])

@app.route('/api/products/<sku>', methods = ['DELETE']) # allows user to delete product
def delete_product(sku):
    if sku not in products:
        abort(404, description="Product not found") 
    del products[sku]
    return '', 204

# ENDPOINTS FOR WAREHOUSES
@app.route('/api/warehouses', methods = ['GET']) # get all warehouses
def get_all_warehouses():
    return jsonify([warehouse for warehouse in warehouses.values()])

@app.route('/api/warehouses/<id>', methods = ['GET']) # get warehouse by id
def get_warehouse(id):
    warehouse = warehouses.get(id)
    if not warehouse:
        abort(404, description = f"Warehouse {id} not found")
    return jsonify(warehouse)

@app.route('/api/warehouses', methods = ['POST']) # allows user to create warehouse
def create_warehouse():
    data = request.get_json()
    warehouse_id = generate_id('WH', warehouses)
    data['id'] = warehouse_id
    warehouses[warehouse_id] = data
    return jsonify(data), 201

@app.route('/api/warehouses/<id>', methods = ['PUT']) # update warehouse (identify by id)
def update_warehouse(id):
    if id not in warehouses:
        abort(404, description="Warehouse not found")
    data = request.get_json()
    warehouses[id].update(data)
    return jsonify(warehouses[id])

@app.route('/api/warehouses/<id>', methods = ['DELETE']) # allows user to delete warehouse by its id
def delete_warehouse(id):
    if id not in warehouses:
        abort(404, description = "Warehouse not found")
    del warehouses[id]
    return '', 204

# ENDPOINTS FOR INVENTORY
@app.route('/api/inventory', methods = ['GET']) # get all inventory
def get_inventory():
    inventory_list = []
    for sku, inv in inventory.items():
        product = products.get(sku)
        total_quantity = sum([entry['quantity'] for entry in inv]) 
        inventory_list.append({
            "product": product,
            "inventory": inv,
            "totalQuantity": total_quantity
        })
    return jsonify(inventory_list)

@app.route('/api/inventory/product/<sku>', methods = ['GET']) # get inventory by product sku
def get_inventory_by_product(sku):
    inv = inventory.get(sku, [])
    if not inv:
        abort(404, description="Inventory not found for this product")
    product = products.get(sku)
    total_quantity = sum([entry['quantity'] for entry in inv])
    return jsonify({ 
        "product": product,
        "inventory": inv,
        "totalQuantity": total_quantity
    })

@app.route('/api/inventory/warehouse/<id>', methods = ['GET']) # get inventory by warehouse id
def get_inventory_by_warehouse(id):
    warehouse_inventory = []
    for sku, inv in inventory.items():
        product = products.get(sku)
        for entry in inv:
            if entry['warehouseId'] == id:
                warehouse_inventory.append({
                    "product": product,
                    "warehouseId": id,
                    "quantity": entry['quantity']
                })
    return jsonify(warehouse_inventory)

@app.route('/api/inventory', methods = ['POST']) # updting inventory (this was the hardest part and I'm unsure if this is correct)
def update_inventory():
    data = request.get_json()
    sku = data['sku']
    warehouse_id = data['warehouseId']
    quantity = data['quantity']

    if sku not in products: # error handling for product and warehouse
        abort(404, description = "Product not found")
    if warehouse_id not in warehouses:
        abort(404, description = "Warehouse not found")

    # update inventory
    if sku not in inventory:
        inventory[sku] = []
    
    # check if product exists in wharehouse inventory
    for entry in inventory[sku]:
        if entry['warehouseId'] == warehouse_id:
            entry['quantity'] += quantity
            return jsonify(entry)
        
    # if it isn't we qadd new entry
    inventory[sku].append({
        "warehouseId": warehouse_id,
        "warehouseName": warehouses[warehouse_id]['name'],
        "quantity": quantity
    })
    return jsonify(inventory[sku][-1]), 201 
        

if __name__ == '__main__': # for running the app
    app.run(debug=True, port=3000)