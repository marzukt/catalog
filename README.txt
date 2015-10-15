Book Catalog
A Catalog display app that displays a catalog of books by category
Allows users to add their own books as private or publicly viewable.
Books can belong to any number of categories
User can create private categories for their own books

What's included
:
README.txt - this file
application.py - main application file to run the webserver
client_secrets.json - client secret file for connecting to google
database_setup.py  - database model 
lots_of_books.py - script to insert some seed data into the schema
static/
book.jpg - placeholder image
styles.css - stylesheet


/templates - html for site
addbook.html
addcategory.html
book.html
books.html
categories.html
category.html
deletebook.html
deletecategory.html
editbook.html
editcategory.html
header.html
login.html
main.html
newcategory.html
templates

Prerequisites:
python 2.7.6
Flask==0.10.1
Jinja2==2.7.2
MarkupSafe==0.18
SQLAlchemy==0.8.4
Werkzeug==0.9.4
httplib2==0.9.1
oauth2client==1.4.12
psycopg2==2.4.5
pyOpenSSL==0.13
requests==2.2.1

How to run
1)  run `python lots_of_books.py` to create some catalog entries
2) run `python application.py` to run the web server
3) connect to http://localhost:8000 in you browser to access the site

A JSON endpoint is available at http://localhost:8000/catalog/JSON

