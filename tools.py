# -*- coding=utf-8 -*-
'''
Created on 2013-2-3

@author: Joseph
'''

import subprocess
import time
import os
from config import mysql_config #@UnresolvedImport
from sqlalchemy import create_engine #@UnresolvedImport
from dhole.db.models import *
from sqlalchemy.orm import scoped_session, sessionmaker #@UnresolvedImport
import sys
from dhole.lib import torndb #@UnresolvedImport

reload(sys)
sys.setdefaultencoding('utf-8') #@UndefinedVariable
#print sys.getdefaultencoding()
#mode = "deploy"
mode = "dev"
schema_file = "data/schema.sql"
root_dir =  os.path.join(os.path.dirname(__file__), "data")


def createDbCmd(m):    
    dbname = getDbName(m)
    token = getToken(m)
    cmd = "mysql {0} -e \"CREATE DATABASE IF NOT EXISTS {1}\"".format(token,dbname)    
    exeCmd(cmd)

def dropDbCmd(m):    
    dbname = getDbName(m)
    token = getToken(m)
    cmd = "mysql {0} -e \"DROP DATABASE IF EXISTS {1}\"".format(token,dbname)    
    exeCmd(cmd)
    
def BakDbCmd(m):    
    dbname = getDbName(m)
    filename = getDbBakName(m)
    token = getToken(m)
    cmd = "mysqldump {0} -e --opt -c {1} ".format(token,dbname)
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    fp= open(filename, "w")
    for line in pipe.stdout:
        fp.writelines(line)
    fp.close()    
def RestorebCmd(m):    
    
    c = mysql_config[m] 
    filename = c['schema_file']
    dbname = getDbName(m)
    token = getToken(m)
    cmd = "mysql {0} -e \"use {1}; source {2};\" ".format(token,dbname,filename)
    print cmd
    exeCmd(cmd)
    
def getDbName(m):   
    c = mysql_config[m] 
    dbname = c['mysql_db']   
    return dbname

def getDbResName():       
    return os.path.join(root_dir,'schema.sql')

def getDbBakName(m):       
    dbname = getDbName(m)
    filestamp= time.strftime("%Y-%m-%d-%H-%M-%S")        
    filename = "%s_%s-%s.sql" % (m,dbname, filestamp)
    return os.path.join(root_dir,filename)

def getToken(m):
    c = mysql_config[m]
    cmd = "-u{0} -p{1}".format(c['mysql_user'],c['mysql_pass'])
    return cmd

def echoOutput(stdout):
    for line in stdout:
        print line
        
def exeCmd(command):
    print command
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    echoOutput(pipe.stdout)
    
def createTable(m):
    c = mysql_config[m] 
    engine = create_engine("mysql://{0}:{1}@{2}/{3}?charset=utf8".format(c['mysql_user'],c['mysql_pass'],c['mysql_host'],c['mysql_db']),echo=True)
    init_db(engine)
    
    db = scoped_session(sessionmaker(bind=engine))
    db.add_all([
                Authors("Joseph","liseor@gmail.com"),
                Authors("tom","liseor@gmail.com"),
                Authors("lily","liseor@gmail.com"),
                Authors("susan","liseor@gmail.com"),
                ])
    db.add_all([
                Menu("用户管理".encode('utf-8'),0,0),
                Menu("设置",0,0),
                Menu("全部用户",1,0),
                Menu("密码修改",2,0),
                ])
    
    db.commit()
    
def initDb(m):
    c = mysql_config[m]    
    data_file = os.path.join(os.path.dirname(__file__),"data","schema.sql")
    f = open(data_file,'r')
    data = f.read()
    db = torndb.Connection(c['mysql_host'],c['mysql_db'],c['mysql_user'],c['mysql_pass'])
    db.execute(data)
    print data

if __name__ == '__main__':
    #print getToken(mode)
    #print getDbBakName(mode)
    
    #dropDbCmd(mode)
    #createDbCmd(mode)    
    #createTable(mode)
    
    #RestorebCmd(mode)
    #BakDbCmd(mode)
    #dropDbCmd(mode)
    
    initDb(mode)
    
    