#Book Catalog
A Catalog display app that displays a catalog of books by category
Allows users to add their own books as private or publicly viewable.
Books can belong to any number of categories
User can create private categories for their own books

## What's included
:
README.txt - this file
application.py - main application file to run the webserver
client_secrets.json - client secret file for connecting to google
database_setup.py  - database model 
lots_of_books.py - script to insert some seed data into the schema
requirements.txt - required packages
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


## How to run
1. Run `pip install -requirements.txt` to install dependencies
2. Run `python lots_of_books.py` to create some catalog entries
3. Run `python application.py` to run the web server
4. Connect to http://localhost:8000 in you browser to access the site

A JSON endpoint is available at http://localhost:8000/catalog/JSON
A XML endpoint is available at http://localhost:8000/catalog/XML

