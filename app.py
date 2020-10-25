import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "static/images/products-images"
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif' }

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create database obiect
db = SQL("sqlite:///shop.db")

# Create tables
def createTables():
    db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT, role TEXT DEFAULT 'user', createdAt datetime DEFAULT CURRENT_TIMESTAMP, modifiedAt datetime DEFAULT CURRENT_TIMESTAMP)")
    db.execute("CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, createdAt datetime DEFAULT CURRENT_TIMESTAMP,modifiedAt datetime DEFAULT CURRENT_TIMESTAMP)")
    db.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price NUMERIC, discount NUMERIC default 0,category_id INTEGER, image TEXT, createdAt datetime DEFAULT CURRENT_TIMESTAMP, modifiedAt datetime DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(category_id) REFERENCES categories(id))")
    db.execute("CREATE TABLE IF NOT EXISTS carts(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, createdAt datetime DEFAULT CURRENT_TIMESTAMP, modifiedAt datetime DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))")
    db.execute("CREATE TABLE IF NOT EXISTS cart_items(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, cart_id INTEGER, quantity INTEGER, FOREIGN KEY(product_id) REFERENCES products(id), FOREIGN KEY(cart_id) REFERENCES carts(id))")
    db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, email TEXT, phone TEXT, address TEXT, status INTEGER DEFAULT 0, createdAt datetime DEFAULT CURRENT_TIMESTAMP, modifiedAt datetime DEFAULT CURRENT_TIMESTAMP,  FOREIGN KEY(user_id) REFERENCES users(id))")
    db.execute("CREATE TABLE IF NOT EXISTS order_items(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, order_id INTEGER, quantity INTEGER, FOREIGN KEY(product_id) REFERENCES products(id), FOREIGN KEY(order_id) REFERENCES orders(id))")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You are not logged in. Log in here.", 'danger')
            return render_template("sign-in.html")
        return f(*args, **kwargs)
    return decorated_function


def allow_only_admin(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session['user_id'])
        if rows[0]['role'] != 'admin':
            flash("You don't have acccess to this request.", 'danger')
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# Custom filter
app.jinja_env.filters["usd"] = usd

createTables()

@app.route('/')
def sho_index(): 
    new_products = db.execute("SELECT products.*, categories.name as category_name FROM products LEFT JOIN categories on products.category_id = categories.id ORDER BY products.createdAt desc LIMIT 5")
    products = db.execute("SELECT products.*, categories.name as category_name FROM products LEFT JOIN categories on products.category_id = categories.id LIMIT 8")
    return render_template("index.html", new_products=new_products, products=products, path='/')

@app.route('/about')
def render_about():
    return render_template('about.html', path='/about')

@app.route('/contact')
def render_contact():
    return render_template('contact.html', path='/contact')    

@app.route('/signup', methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":
        # Check username was submitted
        if not request.form.get("username"):
            flash("Username is empty")
            return redirect('/signup')

        # Check password was submitted
        elif not request.form.get("email"):
            flash("Email is empty")
            return redirect('/signup')


        # Check password was submitted
        elif not request.form.get("password"):
            flash("Password is empty")
            return redirect('/signup')

        # Check password match
        elif not request.form.get("password") == request.form.get("confirmpass"):
            flash("Passwords don't match", 'danger')
            return render_template("sign-up.html")
        
        
        
        hash = generate_password_hash(request.form.get("password"))
        new_user_id = db.execute("INSERT INTO users (name, email, password) VALUES(:name, :email, :password)", name=request.form.get("username"), email=request.form.get("email"), password=hash)
        print(new_user_id)
        db.execute("INSERT INTO carts (user_id) VALUES(:user_id)", user_id=new_user_id)
        flash("Registered", 'success')
        return redirect('/')
       
    else:
        return render_template("sign-up.html")


# Sign in route 
@app.route('/signin', methods=["POST", "GET"])
def sign_in():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # POST Request submitted from the login form
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            flash("Email is empty", danger)
            return render_template("sign-in.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Password is empty", 'danger')
            return render_template("sign-in.html")

        # hash = generate_password_hash(request.form.get("password"))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("Invalid username and/or password", 'danger')
            return render_template("sign-in.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        cart = db.execute("SELECT * FROM carts WHERE user_id = :user_id", user_id=rows[0]["id"])

        session["cart_id"] = cart[0]['id']
        session["role"] = rows[0]['role']
        flash("Login successful")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sign-in.html")


# Logout route
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Shop route, show products 
@app.route("/products")
def show_products_shop():
    products = []
    category_id = 0
    if request.args.get("category_id"):
        category_id = int(request.args.get("category_id"))
        products = db.execute("SELECT products.*, categories.name as category_name FROM products LEFT JOIN categories ON products.category_id = categories.id WHERE products.category_id = :category_id ORDER BY modifiedAt desc", category_id=request.args.get("category_id"))
    else:
        products = db.execute("SELECT products.*, categories.name as category_name FROM products LEFT JOIN categories ON products.category_id = categories.id ORDER BY modifiedAt desc")
    categories = db.execute("SELECT * FROM categories")
    
    return render_template("shop.html", products=products, categories=categories, path="/products", category_id=category_id)

# Shop route, show specific product 
@app.route("/products/<id>")
def show_specific_product(id):
    id = int(request.view_args['id'])
    products = db.execute("SELECT products.*, categories.name as category_name FROM products LEFT JOIN categories ON products.category_id = categories.id WHERE products.id = :id", id=id)
    return render_template("product-detail.html", product=products[0])

# Admin route, show products 
@app.route("/admin")
@login_required
@allow_only_admin
def show_products():
    products = db.execute("SELECT products.*, categories.name as category_name FROM products LEFT JOIN categories ON products.category_id = categories.id ORDER BY modifiedAt desc")
    return render_template("admin/admin-panel.html", products=products, path="/admin")

# Admin route, category 
@app.route("/admin/category/")
@login_required
@allow_only_admin
def show_categories():

    categories = db.execute("SELECT * FROM categories ORDER BY modifiedAt desc")
    return render_template("admin/category.html", categories=categories, path="/admin/category")

# Add category route
@app.route("/admin/category/add", methods=["POST", "GET"])
@login_required
@allow_only_admin
def add_category():
    if request.method == "POST":
        if not request.form.get('category'):
            flash("Category name is empty")
            return render_template("admin/add-category.html")

        rows = db.execute("INSERT INTO categories (name) VALUES(:name)", name=request.form.get('category'))
        flash(f"Category {request.form.get('category')} is Added", 'success')

        return redirect('/admin/category')
    else:
        return render_template('admin/add-category.html')


# Update Category route
@app.route("/admin/category/edit", methods=["POST", "GET"])
@login_required
@allow_only_admin
def update_category():
    if request.method == "POST":
        if not request.form.get('category'):
            flash("Category name is empty")
            return render_template("admin/edit-category.html")

        rows = db.execute("UPDATE categories SET name = :name, modifiedAt= :modified WHERE id = :id", name=request.form.get('category'), modified=datetime.now(), id=request.form.get('id'))
        flash("Updated", 'success')

        return redirect('/admin/category')
    else:
        id = request.args.get("id")
        rows = db.execute("SELECT * FROM categories WHERE id = :id", id=id)

        if len(rows) != 1:
            flash("Invalid Category", 'danger')
            return redirect('/admin/category')

        category = rows[0]
        return render_template('admin/edit-category.html', category=category)


# Delete Category route
@app.route("/admin/category/delete")
@login_required
@allow_only_admin
def delete_category():
    id = request.args.get("id")
    rows = db.execute("delete FROM categories WHERE id = :id", id=id)
    flash("Deleted", 'success')
    return redirect('/admin/category')


# Check file type
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add product route
@app.route("/admin/product/add", methods=["POST", "GET"])
@login_required
@allow_only_admin
def add_product():
    categories = db.execute("SELECT * FROM categories")
    if request.method == "POST":
        discount = request.form.get('discount')
        if not request.form.get('discount'):
            discount = 0

        if not request.form.get('product'):
            flash("Product name is empty", 'danger')
            return render_template("admin/add-product.html", categories=categories)

        elif not request.form.get('price'):
            flash("Product price is empty", 'danger')
            return render_template("admin/add-product.html", categories=categories)

        elif not request.form.get('quantity'):
            flash("Product Quantity is empty", 'danger')
            return render_template("admin/add-product.html", categories=categories)

        elif not request.form.get('category_id'):
            flash("Category name is empty", 'danger')
            return render_template("admin/add-product.html", categories=categories)
        
        elif not request.form.get('description'):
            flash("Description is empty", 'danger')
            return render_template("admin/add-product.html", categories=categories)

        if 'file' not in request.files:
            flash("No file apart", 'danger')
            return render_template("admin/add-product.html", categories=categories)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected', 'danger')
            return render_template("admin/add-product.html", categories=categories)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            try:
                price = float(request.form.get('price'))
                db.execute("INSERT INTO products (name, price, discount, category_id, image, quantity, description) VALUES(:name, :price, :discount, :category_id, :image, :quantity, :description)", name=request.form.get('product'), price=price, discount=discount, category_id=int(request.form.get('category_id')), image=filename, quantity=int(request.form.get('quantity')), description=request.form.get('description'))
            except ValueError:
                flash("Enter the valid information", 'danger')
                return render_template("admin/add-product.html", categories=categories)

            

        flash(f"{request.form.get('product')} is added to the Galaxy SHOP", "success")
        return redirect("/admin")
    else:
        return render_template("admin/add-product.html", categories=categories)


# Update product route
@app.route("/admin/product/edit", methods=["POST", "GET"])
@login_required
@allow_only_admin
def update_product():
    categories = db.execute("SELECT * FROM categories")
    if request.method == "POST":
        id = request.form.get("id")
        
        discount = request.form.get('discount')
        if not request.form.get('discount'):
            discount = 0

        if not request.form.get('product'):
            flash("Product name is empty", 'danger')
            return render_template("admin/edit-product.html", categories=categories)

        elif not request.form.get('price'):
            flash("Product price is empty", 'danger')
            return render_template("admin/edit-product.html", categories=categories)

        elif not request.form.get('quantity'):
            flash("Product Quantity is empty", 'danger')
            return render_template("admin/edit-product.html", categories=categories)

        elif not request.form.get('category_id'):
            flash("Category name is empty", 'danger')
            return render_template("admin/edit-product.html", categories=categories)
        
       
        if 'file' not in request.files:
            flash("No file apart", 'danger')
            return render_template("admin/edit-product.html", categories=categories)

        file = request.files['file']

        if file.filename == '':
            db.execute("UPDATE products SET name = :name,price=:price,discount=:discount,category_id=:category_id, quantity=:quantity,modifiedAt= :modified  WHERE id = :id", name=request.form.get('product'), price=float(request.form.get('price')), discount=discount,category_id=int(request.form.get('category_id')), quantity=int(request.form.get('quantity')), modified=datetime.now(), id=int(request.form.get("id")))

        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            try:
                price = float(request.form.get('price'))
                db.execute("UPDATE products SET name = :name,price=:price,discount=:discount,category_id=:category_id, image=:image, modifiedAt= :modified  WHERE id = :id", name=request.form.get('product'), price=float(request.form.get('price')), discount=discount,category_id=int(request.form.get('category_id')), image=filename, modified=datetime.now(), id=int(request.form.get("id")))
            except ValueError:
                flash("Enter the valid information", 'danger')
                return render_template("admin/edit-product.html", categories=categories)

            

        flash(f"Successfully updated", "success")
        return redirect("/admin")
    else:
        id = request.args.get("id")
        rows = db.execute("SELECT * FROM products WHERE id = :id", id=id)

        if len(rows) != 1:
            flash("Invalid Product", 'danger')
            return redirect('/admin')

        product = rows[0]
        return render_template("admin/edit-product.html", product=product,categories=categories)

# Delete Product route
@app.route("/admin/product/delete")
def delete_product():
    id = request.args.get("id")
    rows = db.execute("delete FROM products WHERE id = :id", id=id)
    flash("Deleted", 'success')
    return redirect('/admin')

@app.route("/admin/order")
@login_required
def show_orders():
    orders = db.execute("SELECT * from orders ORDER BY createdAt desc")
    items = []
    items = orders
    for i in range(len(orders)):
        items[i]['order_items'] = []
        items[i]['total'] = 0
    
    for i in range(len(orders)):
        items[i]['order_items'] = db.execute("SELECT order_items.*, products.id as product_id, products.name, products.price, products.discount  from order_items LEFT JOIN products ON order_items.product_id = products.id where order_items.order_id =  :order_id", order_id=orders[i]['id'])
       
        for j in range(len(items[i]['order_items'])):
            items[i]['total'] = items[i]['total'] + ((items[i]['order_items'][j]["price"] - (items[i]['order_items'][j]["price"] * items[i]['order_items'][j]["discount"] / 100 )) * items[i]['order_items'][j]['quantity'])
    
    return render_template('admin/order.html', items=items, path="/admin/order")

# Cart
@app.route("/cart", methods=["POST", "GET"])
@login_required
def show_cart():
    cart_items = db.execute("SELECT cart_items.*, products.name, products.price, products.discount  from cart_items LEFT JOIN products ON cart_items.product_id = products.id where cart_items.cart_id =  :cart_id", cart_id=session['cart_id'])
    total = 0
    for cart_item in cart_items:
        total = total + ((cart_item["price"] - (cart_item["price"] * cart_item["discount"] / 100 )) * cart_item['quantity'])

    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session['user_id'])
    return render_template('cart.html', cart_items=cart_items, total=total, user=rows[0])

# Clear Cart
@app.route("/cart/clear", methods=["POST", "GET"])
@login_required
def clear_cart():
    db.execute("DELETE FROM cart_items WHERE cart_id = :cart_id", cart_id=session['cart_id'])
    cart_items = []
    total = 0
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session['user_id'])
    flash("Cleared Cart", 'success')
    return render_template('cart.html', cart_items=cart_items, total=total, user=rows[0])

 
# Add to cart
@app.route("/cart/add", methods=["POST"])
@login_required
def add_cart():
    
    if not request.form.get("product_id"):
        flash("Product id is empty", 'danger')
        return redirect('/products')

    elif not request.form.get("quantity"):
        flash("Product Quantity is empty", 'danger')
        return redirect('/products/'+request.form.get("product_id"))
    
    products = db.execute("SELECT products.*, categories.name as category_name FROM products LEFT JOIN categories ON products.category_id = categories.id WHERE products.id = :id", id=int(request.form.get("product_id")))
    if int(request.form.get("quantity")) > products[0]['quantity']:
        flash("You can't add quantity greater than current stocks", 'danger')
        return render_template("product-detail.html", product=products[0])

    cart_items = db.execute("SELECT * FROM cart_items WHERE cart_id = :cart_id", cart_id=session['cart_id'])
    if len(cart_items) > 0:
        for item in cart_items:
            row = db.execute("SELECT quantity FROM cart_items WHERE id = :id and cart_id = :cart_id", id=item['id'], cart_id=session['cart_id'])
            if(item['product_id'] == int(request.form.get("product_id"))):
                db.execute("UPDATE cart_items SET quantity = :qty WHERE id = :id and cart_id = :cart_id", qty=row[0]['quantity'] + int(request.form.get("quantity")), id=item['id'], cart_id=session['cart_id'])
                flash("Added to Cart", 'success')
                return render_template("product-detail.html", product=products[0])
            else:
                db.execute("INSERT INTO cart_items (product_id, cart_id, quantity) VALUES(:product_id, :cart_id, :quantity)", product_id=int(request.form.get("product_id")),cart_id=session["cart_id"],quantity=int(request.form.get("quantity")))
                flash("Added to Cart", 'success')
                return render_template("product-detail.html", product=products[0])
    else:
        db.execute("INSERT INTO cart_items (product_id, cart_id, quantity) VALUES(:product_id, :cart_id, :quantity)", product_id=int(request.form.get("product_id")),cart_id=session["cart_id"],quantity=int(request.form.get("quantity")))
        flash("Added to Cart", 'success')
        return render_template("product-detail.html", product=products[0])       

    
    flash("Fail to Add", 'danger')
    return render_template("product-detail.html", product=products[0])  
    
    
@app.route("/cart/delete")
@login_required
def delete_cart():    
    if not request.args.get("id"):
        flash("Invalid Cart Item", 'danger')
        return redirect("/cart")

    id = int(request.args.get("id"))
    db.execute("DelETE from cart_items WHERE id = :id", id=id)
    cart_items = db.execute("SELECT cart_items.*, products.name, products.price, products.discount  from cart_items LEFT JOIN products ON cart_items.product_id = products.id where cart_items.cart_id =  :cart_id", cart_id=session['cart_id'])
    total = 0
    for cart_item in cart_items:
        total = total + (((cart_item["price"] - (cart_item["price"] * cart_item["discount"] / 100 )) * cart_item["quantity"]) * cart_item['quantity'])

    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session['user_id'])
    flash("Removed from Cart", 'success')
    return render_template('cart.html', cart_items=cart_items, total=total, user=rows[0])

# Order route
@app.route("/order/add", methods=["POST", "GET"])
@login_required
def add_order():
    rows = db.execute("SELECT * FROM users WHERE id = :id", id=session['user_id'])
    name = request.form.get("name")
    email = request.form.get("email")
    if not request.form.get("name"):
        name = rows[0]['name']

    elif not request.form.get("email"):
        email = rows[0]['email']

    elif not request.form.get("phone"):
        flash("Phone Number is empty", 'danger')
        return redirect("/cart")

    elif not request.form.get("address"):
        flash("Address is empty", 'danger')
        return redirect("/cart")
    
    
    order_id = db.execute("INSERT INTO orders (user_id, name, email, phone, address) VALUES(:user_id, :name, :email, :phone, :address)", user_id=session['user_id'], name=name, email=email, phone=request.form.get("phone"), address=request.form.get("address"))

    cart_items = db.execute("SELECT cart_items.*, products.name, products.price, products.discount  from cart_items LEFT JOIN products ON cart_items.product_id = products.id where cart_items.cart_id =  :cart_id", cart_id=session['cart_id'])

    for item in cart_items:
        db.execute("INSERT INTO order_items(product_id, order_id, quantity) VALUES(:product_id, :order_id, :quantity)", product_id=int(item['product_id']), order_id=order_id, quantity=int(item['quantity'])) 

    db.execute("DELETE FROM cart_items WHERE cart_id = :cart_id", cart_id=session['cart_id'])
    flash("Order submitted successfully", 'success')
    return redirect("/orders")

# Deliver Order
@app.route("/admin/order/mark")
@login_required
@allow_only_admin
def deliver_order():
    if not request.args.get("id"):
        flash("Invalid Order", 'danger')
        return redirect("/admin/order")
    
    if not request.args.get("status"):
        flash("Invalid statsu", 'danger')
        return redirect("/admin/order")

    db.execute("UPDATE orders set status=:status, modifiedAt = :modifiedAt where id = :id", status=request.args.get("status"), modifiedAt=datetime.now(), id=request.args.get("id"))
    orders = db.execute("SELECT * from orders")
    items = []
    items = orders
    for i in range(len(orders)):
        items[i]['order_items'] = []
        items[i]['total'] = 0

    for i in range(len(orders)):
        items[i]['order_items'] = db.execute("SELECT order_items.*, products.name, products.price, products.discount  from order_items LEFT JOIN products ON order_items.product_id = products.id where order_items.order_id =  :order_id", order_id=orders[i]['id'])

        for j in range(len(items[i]['order_items'])):
            items[i]['total'] = items[i]['total'] + ((items[i]['order_items'][j]["price"] - (items[i]['order_items'][j]["price"] * items[i]['order_items'][j]["discount"] / 100 )) * items[i]['order_items'][j]['quantity'])
        
    flash("Mark as Delivered", 'success')
    return render_template('admin/order.html', items=items)


# order route, user view, show orders of current user
@app.route("/orders")
@login_required
def show_myorders():

    orders = db.execute("SELECT * from orders WHERE user_id = :user_id ORDER BY createdAt desc", user_id=session['user_id'])
    items = []
    items = orders
    for i in range(len(orders)):
        items[i]['order_items'] = []
        items[i]['total'] = 0
    
    for i in range(len(orders)):
        items[i]['order_items'] = db.execute("SELECT order_items.*, products.id as product_id, products.name, products.price, products.discount  from order_items LEFT JOIN products ON order_items.product_id = products.id where order_items.order_id =  :order_id", order_id=orders[i]['id'])
       
        for j in range(len(items[i]['order_items'])):
            items[i]['total'] = items[i]['total'] + ((items[i]['order_items'][j]["price"] - (items[i]['order_items'][j]["price"] * items[i]['order_items'][j]["discount"] / 100 )) * items[i]['order_items'][j]['quantity'])
    
    return render_template('user-orders.html', items=items)
