#!/usr/bin/env python
# -*- coding=utf-8 -*-

#使用装饰器(decorator),   
def singleton(cls, *args, **kw):  
    instances = {}  
    def _singleton():  
        if cls not in instances:  
            instances[cls] = cls(*args, **kw)  
        return instances[cls]  
    return _singleton  