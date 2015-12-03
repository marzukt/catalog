from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Book, Category, BookCategory

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

User1 = User(name='Nemo', email = 'nemo@gamil.com')
session.add(User1)
session.commit()

User2 = User(name='Donkey', email = 'donkey@gamil.com')
session.add(User2)
session.commit()

user_id = session.query(User).filter_by(name='Nemo').first()
Category1 =Category(name = 'Action')
session.add(Category1)
session.commit()

Category2 =Category(name = 'Drama')
session.add(Category2)
session.commit()

Category3 =Category(name = 'Comedy')
session.add(Category3)
session.commit()

Category4 =Category(name = 'Tragedy')
session.add(Category4)
session.commit()

Category5 =Category(name = 'Nemos books',
                    user_id = User1.id)
session.add(Category5)
session.commit()


Book1 = Book(name = 'Frankenstein',
             description = 'Dr Frankenstein makes a monster',
             cover = 'https://upload.wikimedia.org/wikipedia/commons/3/35/Frankenstein_1818_edition_title_page.jpg',
             guttenberg_url = 'https://www.gutenberg.org/cache/epub/84/pg84.txt',
             user_id = user_id.id)
session.add(Book1)
session.commit()

BookCategory1 = BookCategory(book_id = Book1.id,
                            category_id = Category1.id)
session.add(BookCategory1)
session.commit()

Book2 = Book(name = "Alice's Adventures in Wonderland",
             description = 'Alice goes on an adventure',
             cover = 'https://upload.wikimedia.org/wikipedia/en/3/3f/Alice_in_Wonderland%2C_cover_1865.jpg',
             guttenberg_url = 'https://www.gutenberg.org/ebooks/11.txt.utf-8',
             user_id = user_id.id)
session.add(Book2)
session.commit()

BookCategory2 = BookCategory(book_id = Book1.id,
                            category_id = Category2.id)
session.add(BookCategory1)
session.commit()

Book3 = Book(name = " Nemo Private book",
             description = 'should not be seen other than by user Nemo',
             cover = 'https://upload.wikimedia.org/wikipedia/en/3/3f/Alice_in_Wonderland%2C_cover_1865.jpg',
             guttenberg_url = 'https://www.gutenberg.org/ebooks/11.txt.utf-8',
             public = False,
             user_id = User1.id)
session.add(Book3)
session.commit()

BookCategoryNemo = BookCategory(book_id = Book3.id,
                            category_id = Category5.id)
session.add(BookCategoryNemo)
session.commit()

Book4 = Book(name = " Donkey Private book",
             description = 'should not be seen other than by user Nemo',
             cover = 'https://upload.wikimedia.org/wikipedia/en/3/3f/Alice_in_Wonderland%2C_cover_1865.jpg',
             guttenberg_url = 'https://www.gutenberg.org/ebooks/11.txt.utf-8',
             public = False,
             user_id = User2.id)
session.add(Book4)
session.commit()

Book5 = Book(name = "Great Expectations",
             description = ' some stuff happens',
             isbn = '9780333546079',
             user_id = user_id.id)
session.add(Book5)
session.commit()

BookCategory3 = BookCategory(book_id = Book5.id,
                            category_id = Category3.id)
session.add(BookCategory3)
session.commit()

Book6 = Book(name = "Exciting tales",
             description = "somewhat boring stories",
             user_id = user_id.id)
session.add(Book6)
session.commit()

BookCategory4 = BookCategory(book_id = Book6.id,
                            category_id = Category4.id)
session.add(BookCategory4)
session.commit()

Book7 = Book(name = "Life of Snail",
             description = 'Life in the fast lane',
             cover = 'https://en.wikipedia.org/wiki/File:Alice_in_Wonderland,_cover_1865.jpg',
             guttenberg_url = 'https://www.gutenberg.org/ebooks/11.txt.utf-8',
             user_id = user_id.id)
session.add(Book7)
session.commit()

BookCategory5 = BookCategory(book_id = Book7.id,
                            category_id = Category1.id)
session.add(BookCategory5)
session.commit()

Book8 = Book(name = "Homer's oddessy",
             description = 'Homer stays at home and watches tv',
             guttenberg_url = 'https://www.gutenberg.org/ebooks/11.txt.utf-8',
             user_id = user_id.id)
session.add(Book8)
session.commit()

BookCategory6 = BookCategory(book_id = Book8.id,
                            category_id = Category2.id)
session.add(BookCategory6)
session.commit()

Book9 = Book(name = "Shantaram",
             isbn = "0312330529",
             user_id = user_id.id)
session.add(Book9)
session.commit()

BookCategory7 = BookCategory(book_id = Book9.id,
                            category_id = Category2.id)
session.add(BookCategory7)
session.commit()