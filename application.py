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

#Show all books if no category is passed otherwise just show books for that category
@app.route('/books/')
@app.route('/category/<int:category_id>/books/')
def showBooks(category_id = None):
    if category_id:
        books = session.query(Book).filter(Book.id.in_(session.query(BookCategory.book_id).filter_by(category_id = category_id))).all()
    else:
        books = session.query(Book).all()
    return render_template('books.html', books = books, category_id = category_id)

# Show a single book
@app.route('/book/<int:book_id>/')
def showBook(book_id):
    book = session.query(Book).filter_by(id = book_id).one()
    output = ''
    output += 'id: {} , name: {}'.format(book.id, book.name)
    output += '</br>'
    return output

# Add a book
@app.route('/books/new/', methods=['GET','POST'])
@app.route('/category/<int:category_id>/books/new', methods=['GET','POST'])
def newBook(category_id = None):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if request.method == 'POST':
        newBook = Book(name = request.form['name'],
                       description = request.form['description'],
                       cover = request.form['cover'],
                       guttenberg_url = request.form['guttenberg_url'],
                       amazon_url = request.form['amazon_url']
                       )
        session.add(newBook)
        session.commit()
        # uncomment to make a lack of category cause an error
        #if request.form['category']:
        addBookCategory(newBook.id, request.form.getlist('category'))
        flash('New Book {} successfully created'.format(newBook.name))
        return redirect(url_for('showBooks'))
    else:
        return render_template('addbook.html', categories = categories, category_id = category_id)

# Edit a book
@app.route('/books/<int:book_id>/edit/', methods=['GET','POST'])
def editBook(book_id):
    editedBook = session.query(Book).filter_by(id = book_id).one()
    categories = session.query(Category).order_by(asc(Category.name)).all()
    editedBookCategories = session.query(BookCategory).filter_by(book_id = book_id).all()

    # flask template can't iterate a generator send ids as a list
    #editedBookCategoriesIDs = (cat.category_id for cat in editedBookCategories)
    editedBookCategoriesIDs = []
    for cat in editedBookCategories:
        editedBookCategoriesIDs.append(cat.category_id)

    if request.method == 'POST':
        if request.form['name']:
            editedBook.name = request.form['name']
        if request.form['description']:
            editedBook.description = request.form['description']
        if request.form['cover']:
            editedBook.cover = request.form['cover']
        if request.form['guttenberg_url']:
            editedBook.guttenberg_url = request.form['guttenberg_url']
        if request.form['amazon_url']:
            editedBook.amazon_url = request.form['amazon_url']
        session.add(editedBook)
        session.commit()
        # uncomment to make a lack of category cause an error
        #if request.form['category']:
        addBookCategory(editedBook.id, request.form.getlist('category'))
        return redirect(url_for('showBooks'))
    else:
        return render_template('editBook.html',
                               book_id = book_id,
                               book = editedBook,
                               categories = categories,
                               editedBookCategoriesIDs = editedBookCategoriesIDs)

# Delete a book
@app.route('/books/<int:book_id>/delete/', methods = ['GET','POST'])
def deleteBook(book_id):
    bookToDelete = session.query(Book).filter_by(id = book_id).one()
    if request.method == 'POST':
        #delete category associations first
        addBookCategory(book_id)
        session.delete(bookToDelete)
        session.commit()
        return redirect(url_for('showBooks'))
    else:
        return render_template('deletebook.html', book = bookToDelete)
    return 'Page to delete book'

def addBookCategory(book_id,category_list=[]):
    """Add categories for  a book
    """
    # clear old categories
    oldCategories = session.query(BookCategory).filter_by(book_id = book_id).all()
    if oldCategories:
        for oldCategory in oldCategories:
            session.delete(oldCategory)
        session.commit()

    # add new categories
    for category in category_list:
        newBookCategory = BookCategory(book_id = book_id,
                                       category_id = category)
        session.add(newBookCategory)
        session.commit()
    return

## List all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    return render_template('categories.html', categories = categories)

@app.route('/category/new/', methods = ['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'],
                       description = request.form['description']
                       )
        session.add(newCategory)
        session.commit()
        flash('New Category {} successfully created'.format(newCategory.name))
        return redirect(url_for('showCategories'))
    else:
        return render_template('addcategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods = ['GET','POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        if request.form['description']:
            editedCategory.description = request.form['description']
        session.add(editedCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html', category = editedCategory)

# Delete a category
@app.route('/category/<int:category_id>/delete/', methods = ['GET','POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id = category_id).one()
    books = session.query(Book).filter(Book.id.in_(
        session.query(BookCategory.book_id).filter_by(category_id = category_id))).all()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deletecategory.html', category = categoryToDelete, books = books)

# Test page
@app.route('/test/')
def showTest():
    return 'This is a test page'

if __name__ == '__main__':
    app.secret_key = 'change_me_to_something_secure'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)

