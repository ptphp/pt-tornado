# -*- coding: utf8 -*- 

from sqlalchemy import create_engine #@UnresolvedImport
from sqlalchemy import Column, Integer, String, DateTime , Date , Boolean #@UnresolvedImport
from sqlalchemy import Sequence #@UnresolvedImport
from sqlalchemy import ForeignKey #@UnresolvedImport
from sqlalchemy.orm import relationship, backref #@UnresolvedImport
from sqlalchemy.orm import sessionmaker #@UnresolvedImport
from sqlalchemy.orm import scoped_session #@UnresolvedImport
from sqlalchemy.ext.declarative import declarative_base #@UnresolvedImport

Base = declarative_base()

def init_db(engine):
    Base.metadata.create_all(bind=engine)

class Authors(Base):
    __tablename__ = "authors"
    __table_args__ = {
        'mysql_charset': 'utf8',
        'mysql_engine': 'InnoDB',
    }
    id = Column(Integer, primary_key = True)
    email = Column(String(100))
    name = Column(String(100))
    #mysql_engine='InnoDB'
    #mysql_charset='utf8'
    def __init__(self, name, email):
        self.name = name
        self.email = email
    def __repr__(self):
        return "<Authors('%s','%s')>" % (self.name, self.email)


class User(Base):
    __tablename__ = "user"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id       = Column(Integer, primary_key=True)
    username = Column(String(30))
    password = Column(String(40))
    email    = Column(String(100),default = "")
    addtime  = Column(DateTime)
    userinfo = relationship("Userinfo", uselist=False, backref="user")

class Userinfo(Base):
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    __tablename__ = "userinfo"
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey('user.id'))
    realname    = Column(String(5))
    email       = Column(String(60))
    birth       = Column(Date)
    sex         = Column(Boolean)
    mobile      = Column(Integer)
    address     = Column(String(254))
    phone       = Column(String(20))
    zip         = Column(String(6))


class Auth(Base):
    __tablename__ = "auth"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id        = Column(Integer, primary_key = True)
    user_id   = Column(Integer, ForeignKey("user.id"))
    user      = relationship("User", backref=backref('auth', order_by=id))
    secret    = Column(String(64))
    addtime   = Column(DateTime)

class Company(Base):
    __tablename__ = "company"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id        = Column(Integer, primary_key = True)
    logo      = Column(String(125))
    name      = Column(String(20))
    url       = Column(String(50))
    status    = Column(Boolean)    
    addtime   = Column(DateTime)

class Game(Base):
    __tablename__ = "game"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id        = Column(Integer, primary_key = True)
    name      = Column(String(20))
    company_id= Column(Integer, ForeignKey('company.id'))
    company   = relationship("Company", backref=backref('games', order_by=id))
    url       = Column(String(50))
    status    = Column(Boolean)    
    addtime   = Column(DateTime)

class Product(Base):
    __tablename__ = "product"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }        
    id        = Column(Integer, primary_key = True)      
    game_id   = Column(Integer, ForeignKey('game.id'))
    game      = relationship("Game", backref=backref('products', order_by=id))
    level     = Column(Integer)
    price     = Column(Integer)
    promo     = Column(Integer)
    
class Order(Base):
    __tablename__ = "order"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id        = Column(Integer, primary_key = True) 
    orderno   = Column(String(50)) 
    pro_id    = Column(Integer, ForeignKey('product.id'))
    product   = relationship("Product", backref=backref('orders', order_by=id))
    
    user_id   = Column(Integer, ForeignKey("user.id"))
    user      = relationship("User", backref=backref('orders', order_by=id))
    status    = Column(Boolean)
    price     = Column(Integer)
    addtime   = Column(DateTime)
    
class Ship(Base):
    __tablename__ = "ship"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id        = Column(Integer, primary_key = True)
    order_id  = Column(Integer, ForeignKey('order.id'))
    order     = relationship("Order", backref=backref('ship', order_by=id))
    
class IProduct(Base):
    __tablename__ = "iproduct"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id        = Column(Integer, primary_key = True)
    pro_id    = Column(Integer, ForeignKey('product.id'))
    product   = relationship("Product", backref=backref('iproduct', order_by=id))
    user_id   = Column(Integer, ForeignKey("user.id"))
    user      = relationship("User", backref=backref('iproduct', order_by=id))
    #激活
    isActive  = Column(Boolean)    


    
class Admin(Base):
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    
    __tablename__ = "admin"
    id          = Column(Integer, primary_key=True)
    username    = Column(String(30))
    password    = Column(String(40))

class Menu(Base):
    __table_args__ = {
        'mysql_charset': 'utf8',
    }    
    __tablename__ = "menu"
    id          = Column(Integer, primary_key=True)
    title       = Column(String(30))
    parent      = Column(Integer)
    msg         = Column(Integer)
    def __init__(self,title,parent,msg):
        self.title = title
        self.parent = parent
        self.msg = msg        


class Category(Base):
    __table_args__ = {
        'mysql_charset': 'utf8',
    }    
    __tablename__ = "category"
    id          = Column(Integer, primary_key=True)
    title       = Column(String(30))
    parent      = Column(Integer)
    def __init__(self,title,parent,msg):
        self.title = title
        self.parent = parent
        self.msg = msg

class Article(Base):
    __tablename__ = "article"
    __table_args__ = {
        'mysql_charset': 'utf8',
    }
    id        = Column(Integer, primary_key = True)
    cat_id    = Column(Integer, ForeignKey("category.id"))
    Category  = relationship("Category", backref=backref('article', order_by=id))
    Title     = Column(String(64))
    Img       = Column(String(120))
    content   = Column(String(500))
    addtime   = Column(DateTime)


