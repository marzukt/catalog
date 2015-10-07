from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# import schema from database_setup
from database_setup import Base, User, Book, Category, BookCategory, Author

app = Flask(__name__)
# Connect to a database and create a database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Show all books
@app.route('/book/')
def showBooks():
    books = session.query(Book).all()
    output = ''
    for book in books:
        output += 'id: {} , name: {}'.format(book.id, book.name)
        output += '</br>'
    return output

# Show a book
@app.route('/book/<int:book_id>/')
def showBook(book_id):
    book = session.query(Book).filter_by(id = book_id).one()
    output = ''
    output += 'id: {} , name: {}'.format(book.id, book.name)
    output += '</br>'
    return output

# Add a book
@app.route('/book/new/')
def newBook():
    return 'Page to add a new book'

# Edit a book
@app.route('/book/<int:book_id>/edit/')
def editBook(book_id):
    return 'Page to edit  book {}'.format(book_id)

# Delete a book
@app.route('/book/<int:book_id>/delete/')
def deleteBook(book_id):
    return 'Page to delete book'

## List all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    output = ''
    for category in categories:
        output += '<h1> Categories </h1>'
        output += category.name
        output += '</br>'
    return 'Page to show categories'

@app.route('/category/new/')
def newCategory():
    return 'page for adding a new Category'

# Edit a category
@app.route('/category/<int:category_id>/edit/')
def editCategory(category_id):
    return 'This is a page for editing the catalog with the id {}'.format(category_id)

# Delete a category
@app.route('/category/<int:category_id>/delete/')
def deleteCategory(category_id):
    return 'page for deleting category {}'.format(category_id)

# Test page
@app.route('/test/')
def showTest():
    return 'This is a test page'

if __name__ == '__main__':
    app.secret_key = 'change_me_to_something_secure'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)

