# encoding: utf-8
import cherrypy
from glams.glamsTemplate import glamsTemplate
from glams.checkpassword.checkpassword import *
from glams.website.home.ajax.ajax import Ajax
from glams.website.home.settings import getsettings
from glams.website.home.login import getlogin
from lxml import etree
from lxml.builder import E



def logout():
    cookie=cherrypy.response.cookie
    cherrypy.request.cookie=cookie #clears incoming cookie
    cookie['sida']=''
    cookie['sida']['expires']=0
    cookie['sida']["path"] = "/"
    cookie['sidb']=''
    cookie['sidb']['expires']=0
    cookie['sidb']["path"] = "/"

def getHome(username):
    table=E.table({'id':'create_view'},
              E.tr(E.th('Create'),E.th('View')),
              E.tr(
                  E.td({'id':'create'}),
                    E.p('Nothing to create yet!'),
                  E.td({'id':'view'}),
                      E.p(E.a({'href':'/database/'},'Database')),
                      #E.p(E.a({'href':'/calendar/'},'Calendar')) #KE leaving this commented until I can completely integrate the calendar
              )
          )

    article=E.div(E.h1(username,E.span('(',E.a({'href':'/home/logout/'},'log out'),')')),table)
    resources=   """<link rel="stylesheet" type="text/css" href="/support/css/home/home.css" />"""
    
    article=etree.tostring(article, pretty_print=True)
    return glamsTemplate(article, username, resources=resources)
            
class Home:
    ajax=Ajax()
    @cherrypy.expose
    def index(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />"""
        if username=='admin':
            return """<meta http-equiv="refresh" content="0;url=/admin/" />"""
        return getHome(username)

    @cherrypy.expose
    def login(self, **args):
        return getlogin(args)

    @cherrypy.expose
    def logout(self):
        logout()
        return glamsTemplate("Logged out sucessfully!")

    @cherrypy.expose
    def settings(self):
        return getsettings()
    
    
    
    


