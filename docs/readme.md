easy_install sqlalchemy
easy_install jinja2
easy_install simplejson
easy_install pil

yum install python-devel
yum install mysql-devel
wget http://downloads.sourceforge.net/project/mysql-python/mysql-python/1.2.3/MySQL-python-1.2.3.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fmysql-python%2Ffiles%2Fmysql-python%2F1.2.3%2FMySQL-python-1.2.3.tar.gz%2Fdownload&ts=1359902964&use_mirror=nchc

tar xzvf MySQL-python-1.2.3.tar.gz -C /data/soft/install
cd /data/soft/install/MySQL-python-1.2.3
python setup.py build
python setup.py install

python server.py --mode=dev
python server.py --mode=deploy --port=80


supervisorctl reload
supervisord

tornado MySQL server has gone away
http://www.google.com.hk/search?hl=zh-CN&newwindow=1&safe=strict&tbo=d&site=&source=hp&q=tornado+MySQL+server+has+gone+away&btnK=Google+%E6%90%9C%E7%B4%A2

关于sqlalchemy的mysql server has gone away错误
http://www.91python.com/archives/568


SQLAlchemy报错“2006, MySQL server has gone away”
http://hi.baidu.com/limpid/item/e37c37ffd12a0d11ff35825d

lucyzhang2009@126.com  lucyzhang19791016
