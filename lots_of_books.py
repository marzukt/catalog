from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Book, Category, BookCategory, Author

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

User1 = User(name='Nemo', email = 'nemo@gamil.com')
session.add(User1)
session.commit()

user_id = session.query(User).filter_by(name='Nemo').first()
Book1 = Book(name = 'Frankenstein',
             description = 'Dr Frankenstein makes a monster',
             cover = 'https://en.wikipedia.org/wiki/File:Frankenstein_1818_edition_title_page.jpg',
             guttenberg_url = 'https://www.gutenberg.org/cache/epub/84/pg84.txt',
             user_id = user_id.id)
session.add(Book1)
session.commit()

Book2 = Book(name = "Alice's Adventures in Wonderland",
             description = 'Alice goes on an adventure',
             cover = 'https://en.wikipedia.org/wiki/File:Alice_in_Wonderland,_cover_1865.jpg',
             guttenberg_url = 'https://www.gutenberg.org/ebooks/11.txt.utf-8',
             user_id = user_id.id)
session.add(Book2)
session.commit()
