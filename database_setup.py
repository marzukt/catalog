from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(250))
    picture = Column(String(250))

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id'        :self.id,
            'name'      :self.name,
            'desc'      :self.description,
        }

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    cover = Column(String(250))
    guttenberg_url = Column(String(250))
    amazon_url = Column(String(250))
    public = Column(Boolean, default = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id'        :self.id,
            'name'      :self.name,
            'desc'      :self.description,
            'cover'     :self.cover,
        }

class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class BookAuthor(Base):
    __tablename__ = 'bookauthor'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship(Book)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship(Author)

class BookCategory(Base):
    __tablename__ = 'bookcategory'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship(Book)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
