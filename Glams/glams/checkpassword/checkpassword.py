# encoding: utf-8
import cherrypy
from glams.databaseInterface.connect import db
from glams.databaseInterface.connect import importconfig

def isUser(name, hashedpassword):
    data=db.execute("""SELECT password FROM lab_members WHERE name=%s """, (name,), commit=False)
    try:
        data=data[0][0]
    except IndexError:
        return False
    if data==hashedpassword:
        return True
    else:
        return False

def checkPassword():
    '''Simply checks if a cookie is set.  If it is, return users name'''
    cookie = cherrypy.request.cookie
    if len(cookie)>0:
        try:
            name = cookie['sida'].value
            hashedpassword = cookie['sidb'].value
            if isUser(name, hashedpassword):
                return name
        except KeyError:
            pass
    return None

config=importconfig()
salt=config['salt']
            

    
