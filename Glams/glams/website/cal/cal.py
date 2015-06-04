# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 18:07:51 2014

@author: kyle
"""
import cherrypy
from glams.checkpassword.checkpassword import checkPassword
from glams.glamsTemplate import glamsTemplate
from glams.databaseInterface.connect import importconfig


config=importconfig()
calTag=str(config['calendarTag'])

class Ajax:
    @cherrypy.expose
    def updatecalendar(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes an unknown user to the login screen
        return 'This button does nothing... yet'
        

class Calendar:
    ajax=Ajax()
    @cherrypy.expose
    def index(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes the unknown user to login
        article="<p id='notification'></p>"
        article+=calTag
        rightbar="<p style='position:absolute;padding:3px 5px;display: block;width: 120px;'><a  class='button-link' onclick='updatecal();'>Update</a></p>"
        style="""
#notification{
    display:none;
    padding:5px;
    margin:3px;
    background-color:#FFFF66;
    webkit-border-radius: 8px;
    -moz-border-radius: 8px;
    border-radius: 8px;}
    """
        javascript="""
var t;
function notify(data){
    $('#notification').html(data);
    $('#notification').show();
    var fadefunc="$('#notification').hide('fade', {}, 200);";
    t=setTimeout(fadefunc,15000);
}
function updatecal(){$.post('/calendar/ajax/updatecalendar/', function(data){ notify(data);});}
    """
        resources="<style type='text/css'>"+style+'</style><script type="text/javascript">'+javascript+'</script>'
        return glamsTemplate(article, username,resources=resources,rightbar=rightbar)