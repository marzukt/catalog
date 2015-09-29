from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# import schema from database_setup
from database_setup import Base, Category

app = Flask(__name__)
# Connect to a database and create a database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# List all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    output = ''
    for category in categories:
        output += '<h1> Categories </h1>'
        output += category.name
        output += '</br>'
    return output

@app.route('/category/<int:category_id>/edit/')
def editCategory(category_id):
    return 'this is a page for editing the catalog with the id {}'.format(category_id)

# Test page
@app.route('/test/')
def showTest():
    return 'This is a test page'

if __name__ == '__main__':
    app.secret_key = 'change_me_to_something_secure'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)

