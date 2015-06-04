# encoding: utf-8
import cherrypy
from glams.databaseInterface import databaseInterface as DI
from glams.databaseInterface.connect import db, db2
from glams.checkpassword.checkpassword import *
import time
from random import *
import urllib2
import string, hashlib
chars = string.ascii_letters + string.digits

class Ajax:
    @cherrypy.expose
    def changepassword(self, fields):
        time.sleep(1)
        d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        oldpassword=d['oldpassword']
        newpassword1=d['newpassword1']
        newpassword2=d['newpassword2']
        user=checkPassword()
        if not user:
            return """You have been logged out.  <a href="/home/login">Log in</a>."""
        if oldpassword=='' or newpassword1=='' or newpassword2=='':
            return 'You need to fill in all the required password data'
        if newpassword1!=newpassword2:
            return "You entered your new password incorrectly.  Please try again."
        elif len(newpassword1)<=5:
            return "<p>Your password needs to be greater than 5 characters</p>" 
        oldpass=hashlib.md5((oldpassword+salt).encode('utf-8')).hexdigest()
        newpass=hashlib.md5((newpassword1+salt).encode('utf-8')).hexdigest()
        ## RESET COOKIE
        cookie = cherrypy.response.cookie
        sida=user
        sidb=newpass
        cookie['sida']=sida
        cookie['sida']['expires'] = 12 * 30 * 24 * 60 * 60
        cookie['sida']["path"] = "/"
        cookie['sidb']=sidb
        cookie['sidb']['expires'] = 12 * 30 * 24 * 60 * 60
        cookie['sidb']["path"] = "/"
        cherrypy.request.cookie=cookie
        
        data=db.execute("""SELECT id FROM lab_members WHERE name=%s AND password=%s""", (user,oldpass), commit=False)
        if len(data)==0:
            return "Your password is incorrect."
        db.execute('''UPDATE lab_members SET  password=%s WHERE name=%s''', (newpass, user))
        return 'Your password has been updated!'
        
    @cherrypy.expose
    def changeemail(self, fields):
        time.sleep(1)
        user=checkPassword()
        if not user:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />"""
        d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        newemail1=d['newemail1']
        newemail2=d['newemail2']
        password=d['password']

        if newemail1=='' or newemail2=='':
            return 'You need to fill in all the required email data'
        if newemail1!=newemail2:
            return "You entered your new email incorrectly.  Please try again."
        password=hashlib.md5((password+salt).encode('utf-8')).hexdigest()
        if not DI.isUser(user, password):
            return "You entered your password incorrectly."

        db.execute('''UPDATE lab_members set email=%s WHERE name=%s ''', (newemail1, user))
        return 'Your email has been updated to <b>{0}</b>'.format(newemail1)
        
    @cherrypy.expose
    def sendusername(self, email):
        names=data=db.execute('''SELECT name FROM lab_members WHERE email=%s ''',(email,), commit=False)
        if len(data)==0:
            return False
        names=[]
        for i in data:
            names.append(i[0])
        if names is False:
            return "That email address isn't associated with an account.  Please enter a different email address."
        if len(names)==1:
            name=names[0]
            text='Your user name is {}'.format(name)
        else:
            text='The user names associated with this email address are: ' + ', '.join(names)
        html='<p>{}</p>'.format(text)
        subject='Your user name for RedRabbitAlmanac.com'
        sendmail(email, subject, html, text)
        return 'Your user name has been sent to {}'.format(email)
        
    @cherrypy.expose
    def resetpassword(self, email):
        names=DI.getusername(email)
        if names is False:
            return "That email address isn't associated with an account.  Please enter a different email address."
        subject='Password reset for Glams'
        newpassword=''.join(choice(chars) for x in range(10))
        if len(names)==1:
            name=names[0]
            text='Your user name is {} '.format(name)
            text+=". Your new password is '{}'.".format(newpassword)
        else:
            text='The user names associated with this email address are: ' + ', '.join(names)
            text+=".  The new password for those accounts is '{}'.".format(newpassword)
        html='<p>{}</p>'.format(text)
        hashedpassword=hashlib.md5((newpassword+salt).encode('utf-8')).hexdigest()
        db.execute('''UPDATE lab_members SET password=%s WHERE email=%s ''', (hashedpassword, email))
        sendmail(email, subject, html, text)
        return "Your password has been reset."
    
    
    
    
        
        
        
