import uuid
import binascii
import datetime
from sqlalchemy import desc #@UnresolvedImport
from sqlalchemy import Column #@UnresolvedImport
from sqlalchemy import String #@UnresolvedImport
from sqlalchemy import Integer #@UnresolvedImport
import simplejson as json
from .models import *
from dhole.lib import torndb #@UnresolvedImport
import tornado.web
          
class AbstractDBMixin(object):
    _table_name = None
    def table(self,name):
        self._table_name = name
        return self    
    def _save(self,data):
        pass 
    def remove(self,id):      
        self.dba.execute("DELETE FROM `{0}` WHERE id = %s".format(self._table_name),int(id))
    def getOne(self,id):
        return self.dba.get("SELECT * FROM `{0}` WHERE id = %s".format(self._table_name),int(id))
    def all(self):
        return self.dba.query("SELECT * FROM `{0}` ORDER BY id ASC".format(self._table_name))

class UserDBMixin(AbstractDBMixin):
    def update_newpassword(self,id,pwd):
        self.dba.execute("update user set password = %s where id = %s" ,pwd,int(id))
        
    def get_password_by_id(self,id):
        user = self.dba.get("select password from user where id = %s" ,int(id))
        if user:
            return user.password
        else:
            return False
        
    def get_user_info_by_id(self,id):
        return self.dba.get("select * from user as u left join userinfo as i on i.id = u.id where u.id = %s",int(id))
    
    def update_user_info(self,id,birth,sex,mobile,address,phone,zip):        
        return self.dba.execute("INSERT INTO "
                                  "`userinfo`(id,birth,sex,mobile,address,phone,zip) "
                                  "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                 id,birth,sex,mobile,address,phone,zip
                            )
    def create_user(self,idcard,email,name,password):
        return self.dba.execute("INSERT INTO "
                                  "`user`(username,password,email,name,addtime) "
                                  "VALUES (%s,%s,%s,%s,%s)",
                                 idcard,password,email, name, datetime.datetime.now()
                            )
    def get_user_by_idcard(self,idcard):
        return self.dba.get("select id,email from user where username = %s" ,idcard)
    def gen_password(self):
        pw = binascii.b2a_hex(uuid.uuid4().bytes)
        return pw[0:8]
    def select_member_by_usr_pwd(self, usr, pwd):
        return self.dba.get("select * from user where username = %s and password = %s " , usr , pwd)   
    
    def select_member_by_authed(self):
        return self.dba.query("select u.* from auth as a left join user as u on u.id = a.user_id")
    
    def create_auth(self, user_id):
        secret = binascii.b2a_hex(uuid.uuid4().bytes)
        addtime = datetime.datetime.now()
        id = self.dba.execute("INSERT INTO "
                                  "`auth`(user_id,secret,addtime) "
                                  "VALUES (%s,%s,%s)",
                                user_id, secret, addtime
                            )
        return dict(
                    id=id,
                    secret = secret,
                    user_id = user_id,
                    addtime = addtime
                    )
        
    ''' DELETE '''
    def delete_auth_by_secret(self, secret):
        self.dba.execute("delete from auth where secret = %s" ,secret)
        
    def delete_auth_by_member_id(self, member_id):
        self.dba.execute("delete from auth where user_id = %s" ,member_id)
        
    def delete_member_by_id(self, id):
        self.dba.execute("delete from user where id = %s" ,int(id))
    
    
class OrderDBMixin(AbstractDBMixin):
    def get_orders(self): 
        return self.dba.query("select * from `order`")
    def get_cname_gname_pinfo_by_pid(self,pid):  
        return self.dba.get("select c.name as cname,g.name as gname,p.* from product as p left join game as g on g.id = p.game_id left join company as c on c.id = g.company_id  where p.id = %s limit 1",int(pid))
    def get_order_by_pid_idcard(self,pid,idcard,account):
        return self.dba.get("select * from `order` where status = 1 and account = %s and pro_id = %s and idcard = %s limit 1",account,int(pid),idcard)
    def get_orders_by_uid(self,user_id):
        return self.dba.query("select o.* from `order` as o left join user as u on u.username = o.idcard where u.id = %s" ,int(user_id))
    def update_order_by_orderno(self,orderno):
        self.dba.execute("update `order` set status = 1 where orderno = %s" , orderno)
    def get_order_by_orderno(self,orderno):
        return self.dba.get("select * from `order` where orderno = %s", orderno)
    def get_order_by_id_orderno(self,id,orderno):
        return self.dba.get("select * from `order` where id= %s and orderno = %s", int(id),orderno)
    
    def saveOrder(self,orderno,pro_id,account,email,idcard,name,sex,birth,mobile,phone,address,zip,status,price):
        id = self.dba.execute("INSERT INTO "
                                  "`order`(orderno,pro_id,account,email,idcard,name,sex,birth,mobile,phone,address,zip,status,price,addtime) "
                                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                 orderno,pro_id,account,email,idcard,name,sex,birth,mobile,phone,address,zip,status,price,datetime.datetime.now()
                            )
        return id
class iProductDBMixin(AbstractDBMixin):
    
    def get_baodans(self):
        return self.dba.query("select i.*,o.orderno as baodan ,o.account, g.name as gname,c.name as cname,p.level as level from iproduct as i "
                              " left join `order` as o on o.id = i.orderno "
                              " right join `product` as p on p.id = o.pro_id "
                              " left join game as g on p.game_id = g.id "
                              " left join company as c on c.id = g.company_id "
                              " where o.status = 1 ")
    
    def get_baodan_by_uid(self,user_id):
        return self.dba.query("select i.*,o.orderno as baodan ,o.account, g.name as gname,c.name as cname,p.level as level from iproduct as i "
                              " left join `order` as o on o.id = i.orderno "
                              " right join `product` as p on p.id = o.pro_id "
                              " left join game as g on p.game_id = g.id "
                              " left join company as c on c.id = g.company_id "
                              " where o.status = 1 and i.user_id = %s",int(user_id))
    def get_ipro_by_uid_pid(self,user_id,pro_id,account):
        return self.dba.get("select i.* from iproduct as i left join `order` as o on o.id = i.orderno where i.user_id = %s and o.pro_id = %s and o.account = %s limit 1",user_id,pro_id,account)
    def saveIPro(self,orderno,user_id):
        return self.dba.execute("INSERT INTO "
                                  "iproduct(orderno,user_id,isActive,addtime) "
                                  "VALUES (%s,%s,%s,%s)",
                                  orderno,user_id,0,datetime.datetime.now()
                            )
class ProductDBMixin(AbstractDBMixin):
    def getProductByGameId(self,id):
        return self.dba.query("select * from product where game_id = %s order by price asc",int(id))
    def allProducts(self):
        return self.dba.query("SELECT p.*,g.name as gname FROM product as p LEFT JOIN game as g ON g.id = p.game_id ORDER BY p.id ASC")
    
    def saveProduct(self,data):
        if data['id'] == '':
            id = self.dba.execute("INSERT INTO "
                                  "{0}(level,peichang,price,promo,game_id) "
                                  "VALUES (%s,%s,%s,%s,%s)".format(self.table_name),
                                  data['level'],int(data['peichang']),data['price'],data['promo'],data['game_id']
                            )
            return id
        else:
            r = self.dba.get("select * from {0} where id = %s ".format(self.table_name),int(data['id']))
            if not r: raise tornado.web.HTTPError(404)            
            self.dba.execute("UPDATE {0} set "
                             "level = %s , "
                             "peichang = %s , "
                             "price = %s , "
                             "promo = %s , "
                             "game_id = %s "
                             "where id = %s".format(self.table_name),
                             data['level'],data['peichang'],data['price'],data['promo'],int(data['game_id']),int(data['id']))
            return data['id']
class GameDBMixin(AbstractDBMixin):
    def getGameById(self,id):
        return self.dba.query("select * from game where company_id = %s",int(id))
    def allGames(self):
        return self.dba.query("SELECT g.*,c.name as cname FROM game as g LEFT JOIN company as c on c.id = g.company_id ORDER BY g.id ASC")
    def saveGame(self,data):
        if data['id'] == '':
            id = self.dba.execute("INSERT INTO "
                                  "{0}(name,company_id,url,status,addtime) "
                                  "VALUES (%s,%s,%s,1,%s)".format(self.table_name),
                                  data['name'],int(data['company_id']),data['url'],datetime.datetime.now()
                            )
            return id
        else:
            company = self.dba.get("select * from {0} where id = %s ".format(self.table_name),int(data['id']))
            if not company: raise tornado.web.HTTPError(404)            
            self.dba.execute("UPDATE {0} set "
                             "name = %s , "
                             "company_id = %s , "
                             "url = %s "
                             "where id = %s".format(self.table_name),
                             data['name'],int(data['company_id']),data['url'],int(data['id']))
            return data['id']    
        
class ContentDBMixin(AbstractDBMixin):   
    def getAllNews(self): 
        return self.dba.query("select id,title,addtime from content where cat_id = 1  order by id desc")
    def getTopNews10(self):
        return self.dba.query("select id,title from content where cat_id = 1 order by id desc limit 10")
    def getIndexNews9(self):
        return self.dba.query("select id,title,is_top from content where cat_id = 1 and is_index = 1 and pic = '' order by id desc limit 9 ")
    def getIndexPicNews(self):
        return self.dba.get("select id,title,pic from content where cat_id = 1 and is_index = 1 and pic <> '' order by id desc limit 1 ")
    
    def allContents(self):
        return self.dba.query("select * from content")
    
    def saveContent(self,data):
        if data['id'] == '':
            id = self.dba.execute("INSERT INTO "
                                  "content(title,cat_id,text,pic,is_top,is_index,addtime) "
                                  "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                  data['title'],int(data['cat_id']),data['text'],data['pic'],data['is_top'],data['is_index'],datetime.datetime.now()
                            )
            return id
        else:
            category = self.dba.get("select * from content where id = %s ",int(data['id']))
            if not category: raise tornado.web.HTTPError(404)       
            self.dba.execute("UPDATE content set "
                             "title = %s , "
                             "cat_id = %s , "
                             "text = %s , "
                             "pic = %s , "
                             "is_index = %s , "
                             "is_top = %s"
                             "where id = %s",
                             data['title'],int(data['cat_id']),data['text'],data['pic'],data['is_index'],data['is_top'],int(data['id']))
            return data['id']       

class CategoryDBMixin(AbstractDBMixin):        
    def allCategorys(self):
        return self.dba.query("select * from category")
    def saveCategory(self,data):
        if data['id'] == '':
            id = self.dba.execute("INSERT INTO "
                                  "category(title,parent) "
                                  "VALUES (%s,%s)",
                                  data['title'],data['parent']
                            )
            return id
        else:
            category = self.dba.get("select * from category where id = %s ",int(data['id']))
            if not category: raise tornado.web.HTTPError(404)       
            self.dba.execute("UPDATE category set "
                             "title = %s , "
                             "parent = %s "
                             "where id = %s",
                             data['title'],int(data['parent']),int(data['id']))
            return data['id']       
    
class CompnayDBMixin(AbstractDBMixin):
    def getIndexCompany(self):        
        return self.dba.query("select * from company limit 5")
    def saveCompany(self,data):        
        if data['id'] == '':
            id = self.dba.execute("INSERT INTO "
                                  "company(name,logo,url,status,addtime) "
                                  "VALUES (%s,%s,%s,1,%s)",
                                  data['name'],data['logo'],data['url'],datetime.datetime.now()
                            )
            return id
        else:
            company = self.dba.get("select * from company where id = %s ",int(data['id']))
            if not company: raise tornado.web.HTTPError(404)            
            self.dba.execute("UPDATE company set "
                             "name = %s , "
                             "logo = %s , "
                             "url = %s "
                             "where id = %s",
                             data['name'],data['logo'],data['url'],int(data['id']))
            return data['id']    
        
class AdminDBMixin(object):
    def get_user_bar(self):
        bar = {}
        rows = self.db.query(Menu).all()
        parent = {}
        for row in rows:
            if row.parent == 0:
                parent[row.id] = {'id':row.id,'title':row.title,"son":{}}
        
        for row in rows:
            if row.parent != 0:
                parent[row.parent]['son'][row.id] = {'msg':row.msg,'id':row.id,'title':row.title}                        
        return parent
    
    def get_userinfo(self,username):
        bar = self.get_user_bar()        
        return {"username":username,"bar":bar}

