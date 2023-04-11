# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask,render_template,url_for,request,session,logging,redirect,flash,jsonify
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine,MetaData
import sqlalchemy as db
from sqlalchemy.orm import scoped_session,sessionmaker
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

stripe_keys = {
  'secret_key': os.environ.get('STRIPE_SECRET_KEY'),
  'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY')
}

stripe.api_key = stripe_keys['secret_key']

#Database Details
app.secret_key = '53465436554654654654'
app.config['MYSQL_HOST'] = 'b4sanlbkcskhhv4tvs1s-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'u3jsdmlflqqlgn5x'
app.config['MYSQL_PASSWORD'] = 'uooacYZzVYVkPP8hJUdz'
app.config['MYSQL_DB'] = 'b4sanlbkcskhhv4tvs1s'

# Intialize MySQL
mysql = MySQL(app)

# Url of Database
url = f"mysql://u3jsdmlflqqlgn5x:uooacYZzVYVkPP8hJUdz@b4sanlbkcskhhv4tvs1s-mysql.services.clever-cloud.com/b4sanlbkcskhhv4tvs1s"

# Create the Metadata Object
metadata_obj = MetaData()

# Create Database and check if it exists
engine = create_engine(url, echo=True)
conn = engine.connect()
if not database_exists(engine.url):
    create_database(engine.url)
else:
    # Connect the database if exists.
    conn

# Creates table if it does not exists
if not engine.dialect.has_table(conn,"products"):
    products = db.Table(
    'products',                                        
    metadata_obj,                                    
    db.Column('ID', db.Integer, primary_key=True,autoincrement=True),  
    db.Column('name', db.String(100)),                    
    db.Column('Price', db.Integer),                
    )
    
    # Create the profile table
    metadata_obj.create_all(engine)

# Creates table if it does not exists
if not engine.dialect.has_table(conn,"Userdata"):
    products = db.Table(
    'Userdata',                                        
    metadata_obj,                                    
    db.Column('ID', db.Integer, primary_key=True,autoincrement=True),  
    db.Column('Name', db.String(100)),                    
    db.Column('Email', db.String(100)),
    db.Column('Password',db.String(100)),                
    )
    
    # Create the profile table
    metadata_obj.create_all(engine)

# Creates table if it does not exists
if not engine.dialect.has_table(conn,"users"):
    products = db.Table(
    'users',                                        
    metadata_obj,                                    
    db.Column('ID', db.Integer, primary_key=True,autoincrement=True),  
    db.Column('username', db.String(100)),                    
    db.Column('first_name', db.String(100)),
    db.Column('last_name', db.String(100)),
    db.Column('Password',db.String(100)),                
    )
    
    # Create the profile table
    metadata_obj.create_all(engine)

conn.close()

# Creating a Session
db=scoped_session(sessionmaker(bind=engine))

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with Check_Status() function.
def home():
	return render_template("index.html")

@app.route('/login',methods=['POST','GET'])
def login():
    msg = ''
    if request.method == 'POST' and 'f1' in request.form and 'f2' in request.form:
        f1 = request.form.get('f1')
        f2 = request.form.get('f2')
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('SELECT * FROM userdata WHERE Name =%s AND Password = %s', (f1, f2,))
        except:
            cursor.execute('SELECT * FROM userdata WHERE Email =%s AND Password = %s', (f1, f2,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['ID']
            session['username'] = account['Email']
            # Redirect to home page
            print('Logged in successfully!')
            return render_template('navigation.html')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('login.html',msg = msg)

@app.route('/navigation')
def navigation():
    return render_template('navigation.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/create',methods=['POST','GET'])
def create():
    if request.method == 'POST':
        name = request.form.get('f1')
        Price = request.form.get('f2')
        Price = int(Price)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Inserting the Data
        cursor.execute('INSERT INTO products (name,Price) VALUES (%s,%s)', (name, Price,))
        mysql.connection.commit()
        return render_template('create.html')
    return render_template('create.html')

@app.route('/read',methods=['POST','GET'])
def read():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products')
    data = cursor.fetchall()
    print("Data Read Successfully!")
    return render_template('read.html',data=data)

@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('f1')
        Price = request.form.get('f2')
        Price = int(Price)
        id = int(id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE products SET name=%s,Price=%s WHERE ID=%s',(name,Price,id))
        mysql.connection.commit()
        return render_template('update.html')

    return render_template('update.html')

@app.route('/delete',methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        delid = request.form.get('f1')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM products WHERE ID=%s',(delid))
        mysql.connection.commit()
        print("Deleted Successfully!")
        return render_template('delete.html')

    return render_template('delete.html')

@app.route('/pay',methods=['POST','GET'])
def pay():
    return render_template('pay.html',key=stripe_keys['publishable_key'])

@app.route('/checkout', methods=['POST'])
def checkout():

    amount = 0

    customer = stripe.Customer.create(
        email='sample@customer.com',
        source=request.form['stripeToken']
    )

    stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    return render_template('checkout.html', amount=amount)

# Made
@app.route('/wishlist')
def wishlist():
    return render_template('HTML/wishlist.html')

# Made
@app.route('/cart')
def cart():
    return render_template('HTML/Add_to_cart.html')

# Made
@app.route('/templogin',methods=['POST','GET'])
def templogin():
    msg = ''
    if request.method == 'POST':
        # Create variables for easy access
        username = request.form['uname']
        password = request.form['psw']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username =%s AND Password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['ID']
            session['username'] = account['username']
            # Redirect to home page
            print('Logged in successfully!')
            return render_template('index.html')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('HTML/login.html',msg=msg)

@app.route('/signup',methods=['POST','GET'])
def signup():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        username = request.form['uname']
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['psw']
        password2 = request.form['psw-r']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            print("Account exists")
            msg = 'Account already exists!'
            return render_template('HTML/signup.html', msg=msg)
        elif password != password2:
            print("Different Pass")
            msg = 'Different Passwords'
            return render_template('HTML/signup.html', msg=msg)
        else:
            print("Successful Entry")
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users (username, first_name, last_name, Password) VALUES (%s, %s, %s, %s)', (username, fname, lname, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('HTML/signup.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('HTML/signup.html', msg=msg)

@app.route('/temppay')
def temppay():
    return render_template('HTML/Payment.html')

@app.route('/desktopcategory')
def desktopcate():
    return render_template('HTML/Desktopcategory.html')

# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run(debug=True)
