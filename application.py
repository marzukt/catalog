from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# import schema from database_setup
from database_setup import Base, User, Book, Category, BookCategory
# imports for session creation to track state
from flask import session as login_session
# use random and string to generate state token
import random, string
# seasurf for csrf
from flask.ext.seasurf import SeaSurf

#for creating a flow object from client secrets json file
from oauth2client.client import flow_from_clientsecrets
#for catching flow exchange errors
from oauth2client.client import FlowExchangeError
import httplib2
import json
from dict2xml import dict2xml as xmlify
#for creating response object to send to client
from flask import make_response
import requests
# for login required decorator
from functools import wraps

app = Flask(__name__)
csrf = SeaSurf(app)
#load client secrets file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to a database and create a database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def login_required(f):
    """decorator to check login status """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args,**kwargs)
    return decorated_function

# context processor for open library covers
# accesible in templates via {{ openLibraryCoverUrl(isbn) }}
@app.context_processor
def utilityProcessor():
    def openLibraryCoverUrl(isbn):
        """Return open library cover url for a given ISBN"""
        return("{url}/{key}/{value}-{size}.jpg".format(url = "http://covers.openlibrary.org/b",
                                                      key = "isbn",
                                                      value = isbn,
                                                       size = "M" # medium format size
                                                      ))
    return dict(openLibraryCoverUrl = openLibraryCoverUrl)

# JSON APIS
#return whole catalog
def catalogDict():
    """Return a dictionary of the entire catalog"""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    catlist = []
    catbook = {}
    for category in categories:
        books = session.query(Book).filter(Book.id.in_(session.query(
            BookCategory.book_id).filter_by(category_id = category.id))).all()
        catbook = category.serialize
        catbook['Book'] = [book.serialize for book in books]
        catlist.append(catbook)
    catalog = {"Category":catlist}
    return catalog

@app.route('/catalog/JSON')
def catalogJSON():
    """Return entire catalog in json format"""
    return jsonify(Categories = catalogDict())

@app.route('/catalog/XML')
def catalogXML():
    """Return entire catalog in XML format"""
    return app.response_class(xmlify(catalogDict(),wrap="Catalog", indent="   "),
                              mimetype='application/xml')

@app.route('/books/<int:book_id>/JSON')
def bookJSON(book_id):
    """Return  a specific book in JSON format"""
    book = session.query(Book).filter_by(id = book_id).one()
    return jsonify(Book = book.serialize)

@app.route('/books/<int:book_id>/XML')
def bookXML(book_id):
    """Return  a specific book in XML format"""
    book = session.query(Book).filter_by(id = book_id).one()
    return app.response_class(xmlify(book.serialize, wrap="Book",indent = "    "),
                              mimetype='application/xml')


# Create state token
@app.route('/login')
def showLogin():
    #create state token to prevent request forgery
    # use systemRandom().choice as it is more secure
    # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    state = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # validate state token  against the state token server provided
    # this confirms its the actual client
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store one time authorisation code
    code = request.data

    try:
        # Upgrade the authorisation code into a credentials object
        #Create an oauth flow object using info from client secrets
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        #Exchange the one time code for a credentials object
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorisation code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #  If the token comes back check that the access token is valid
    access_token = credentials.access_token
    # use google api server to verify token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    #If there was an error in the access toke info: abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-type'] = 'application/json'

    # Verify that the access token is for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers
        return response

    # check if the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        print 'user already connected'
        response = make_response(json.dumps('Current user is already connected.'),
                                            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in the session for later use
    login_session['credentials'] = credentials.access_token
    print  credentials.access_token
    login_session['gplus_id'] = gplus_id
    print "gplus_id {}".format(gplus_id)

    # get user info the user has just authorised google to provide you
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if the user exists, if it doesn't make a new one

    user_id = getUserID(login_session['email'])
    print('user id = {}'.format(user_id))
    if  not user_id:
        print 'creating user'
        user_id = createUser(login_session)
        print ('after create returned user_id {}'.format(user_id))
    login_session['user_id']= user_id
    output = ''
    output += '<h1>Welcome,'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as {}".format(login_session['username']))
    return output

@app.route('/gdisconnect/')
def gdisconnect():
    #only disconnect a connected user
    print "disconnect entere"
    #print login_session['gplus_id']
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
        json.dumps('Current user not connected.'),401)
        return response
    print credentials
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        print "entered ggisconnect restet"
        # reset the user session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        #del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        #return response
        return redirect(url_for('showBooks'))

    else:
        # token was invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type']  = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


#Show all books if no category is passed otherwise only show books for that category
@app.route('/')
@app.route('/books/')
@app.route('/category/<int:category_id>/books/')
def showBooks(category_id = None):
    # If a category is provided only return books for that category
    # otherwise return all books available to user
    # if user is not logged in only show public books
    categories = getCategories()
    if 'username' not in login_session:
        if category_id:
            books = session.query(Book) \
                .filter(Book.public == True ) \
                .filter(Book.id.in_(session.query(BookCategory.book_id) \
                                    .filter_by(category_id = category_id))) \
                .order_by(asc(Book.name)).all()
        else:
            books = session.query(Book).filter(Book.public == True) \
                .order_by(asc(Book.name)).all()

        return render_template('books.html',
                               books = books,
                               category_id = category_id,
                               categories = categories,
                               )
    # if the user is logged in show their private books as well
    else:
        if category_id:
            books = session.query(Book) \
                .filter((Book.public == True) | (Book.user_id == login_session['user_id']) ) \
                .filter(Book.id.in_(session.query(BookCategory.book_id) \
                                    .filter_by(category_id = category_id))) \
                .order_by(asc(Book.name)).all()
        else:
            books = session.query(Book) \
                .filter((Book.public == True) | (Book.user_id == login_session['user_id'])) \
                .order_by(asc(Book.name)).all()
        return render_template('books.html',
                               books = books,
                               category_id = category_id,
                               categories = categories,
                               user_id = login_session['user_id'])

@app.route('/myBooks/<int:user_id>/')
@login_required
def showMyBooks(user_id):
    # If a category is provided only return books for that category
    # otherwise return all books available to user
    # if user is not logged in only show public books
    if login_session['user_id'] != user_id:
        return "<script>function myFunction() {alert('You are not authorized to view this user's books.');}</script><body onload='myFunction()''>"
    categories = getCategories()
    books = session.query(Book).filter_by(user_id = user_id).order_by(asc(Book.name)).all()

    return render_template('books.html',
                            books = books,
                            categories = categories,
                            category_id = None,
                            user_id = user_id
                            )

# Show a single book
@app.route('/book/<int:book_id>/')
@app.route('/category/<int:category_id>/book/<int:book_id>')
def showBook(book_id,category_id = None):
    categories = getCategories()
    if 'user_id' in login_session:
        user_id = login_session['user_id']
    else:
        user_id = None
    book = session.query(Book).filter_by(id = book_id).one()
    #only a book's creator can remove it
    if not book.public and book.user_id != user_id:
        return "<script>function myFunction() {alert('You are not authorized to view this book.');}</script><body onload='myFunction()''>"
    output = ''
    output += 'id: {} , name: {}'.format(book.id, book.name)
    output += '</br>'
    #return output
    return render_template('book.html',
                           book = book,
                           category_id = category_id,
                           categories = categories,
                           user_id = user_id,
                           )

# Add a book
@app.route('/books/new/', methods=['GET','POST'])
@app.route('/category/<int:category_id>/books/new', methods=['GET','POST'])
@login_required
def newBook(category_id = None):
    # if not logged in redirect to login page before user can see form
    # public categories and user's own categories if they exist
    categories = session.query(Category) \
        .filter((Category.user_id == login_session['user_id']) | (Category.user_id == None)) \
        .order_by(asc(Category.name)).all()
    if request.method == 'POST':
        # Process checkbox to boolean
        # if unchecked it will not be in the returned form
        public = 'public' in request.form
        newBook = Book(name = request.form['name'],
                       description = request.form['description'],
                       cover = request.form['cover'],
                       guttenberg_url = request.form['guttenberg_url'],
                       amazon_url = request.form['amazon_url'],
                       public = public,
                       user_id = login_session['user_id']
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
@app.route('/category/<int:category_id>/books/<int:book_id>/edit/', methods=['GET','POST'])
@login_required
def editBook(book_id,category_id = None):
    # if the user is not logged in redirect to the login page
    editedBook = session.query(Book).filter_by(id = book_id).one()
    # Only the creator can edit a book
    if login_session['user_id'] != editedBook.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this book.');}</script><body onload='myFunction()''>"
    #categories = session.query(Category).order_by(asc(Category.name)).all()
    categories = session.query(Category) \
        .filter((Category.user_id == login_session['user_id']) | (Category.user_id == None)) \
        .order_by(asc(Category.name)).all()
    editedBookCategories = session.query(BookCategory).filter_by(book_id = book_id).all()
    # flask template can't iterate a generator send ids as a list
    # editedBookCategoriesIDs = (cat.category_id for cat in editedBookCategories)
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
        public = 'public' in request.form
        editedBook.public = public
        session.add(editedBook)
        session.commit()
        # modify the books categories
        # if form list is empty only clean up old ones
        addBookCategory(editedBook.id, request.form.getlist('category'))
        flash('Book {} sucessfully edited'.format(editedBook.name))
        return redirect(url_for('showBooks', category_id = category_id))
    else:
        return render_template('editbook.html',
                               book_id = book_id,
                               book = editedBook,
                               categories = categories,
                               category_id = category_id,
                               editedBookCategoriesIDs = editedBookCategoriesIDs)

# Delete a book
@app.route('/books/<int:book_id>/delete/', methods = ['GET','POST'])
@login_required
def deleteBook(book_id):
    bookToDelete = session.query(Book).filter_by(id = book_id).one()
    #only a book's creator can remove it
    if bookToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this book.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        # delete category associations first
        # change model to use cascade to do this automatically on deletion of book
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
@app.route('/category/')
def showCategories():
    categories = getCategories()
    #categories = session.query(Category).order_by(asc(Category.name)).all()
    # If the user is logged in show their custom categories
    if 'username' in login_session:
        userCategories = session.query(Category) \
            .filter(Category.user_id == login_session['user_id']) \
            .order_by(asc(Category.name)).all()
    # otherwise just show the public ones
    else:
        userCategories = None
    return render_template('categories.html', userCategories = userCategories, categories = categories)

def getCategories():
    #categories = session.query(Category).order_by(asc(Category.name)).all()
    # If the user is logged in show their custom categories
    if 'username' in login_session:
        categories = session.query(Category) \
            .filter((Category.user_id == login_session['user_id']) | (Category.user_id == None)) \
            .order_by(asc(Category.name)).all()
    # otherwise just show the public ones
    else:
        categories = session.query(Category) \
            .filter(Category.user_id == None) \
            .order_by(asc(Category.name)).all()
    return categories

@app.route('/category/new/', methods = ['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'],
                       description = request.form['description'],
                        user_id = login_session['user_id']
                       )
        session.add(newCategory)
        session.commit()
        flash('New Category {} successfully created'.format(newCategory.name))
        return redirect(url_for('showCategories'))
    else:
        return render_template('addcategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods = ['GET','POST'])
@login_required
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id = category_id).one()
    if login_session['user_id'] != editedCategory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this category.');}</script><body onload='myFunction()''>"
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
@login_required
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id = category_id).one()
    if login_session['user_id'] != categoryToDelete.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this category.');}</script><body onload='myFunction()''>"
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
    app.run(host = '0.0.0.0', port = 8000)

