# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 14:04:32 2013

@author: kyle
"""
import cherrypy
from glams.glamsTemplate import glamsTemplate
from glams.databaseInterface.connect import db, db2
from glams.checkpassword.checkpassword import *
from glams.website.database.database import getPrettyText
import datetime
from glams.website.database.classes import date2str, getAge

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

class Ajax:
    @cherrypy.expose
    def refresh(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />""" #This takes an unknown user to the login screen
        article="<thead><tr>"    
        #########################   
        #########   CREATE HEADER 
        columns=['mousename','life_status','DOB','DOD','mouse_notes','reserve_date','reserve_description','reserve_lab_member']
        for h in columns:
            article+="<th data-header='{0}' filter class='header'>{1}".format(h,getPrettyText(h))
            article+="<img src='/support/images/drag-handle.png' class='col-handle'></th>"
        article+="</tr></thead><tbody>"
        query= """SELECT m.name AS mousename, m.DOB, m.DOD, m.life_status, m.notes AS mouse_notes, 
                    lab_members.name AS reserve_lab_member, mice_reservations.date AS reserve_date, mice_reservations.description AS reserve_description 
                    FROM mice_reservations 
                    LEFT JOIN lab_members ON mice_reservations.lab_member_id=lab_members.id 
                    LEFT JOIN mice AS m ON m.id=mice_reservations.mouse_id"""
        answer=db2.execute(query)
        if answer!=[]:
            for entry in answer:
                article+="<tr>"
                for col in columns:
                    if entry[col]==None:
                        entry[col]='-'
                    elif type(entry[col])==type(datetime.datetime.now()):
                        entry[col]=date2str(entry[col])
                    elif entry[col]==0:
                        entry[col]='No'
                    elif entry[col]==1:
                        entry[col]='Yes'
                    if col=='mouse_notes':
                        text=html_escape(entry[col])
                        article+="<td class='{0} tooltip' title='{1}'>{2}</td>".format(col,text,text[:20])   #only display the first 20 characters, tooltip the rest
                    else:
                        article+="<td class='{0}'>{1}</td>".format(col,entry[col])                
                article+="</tr>"
            
        article+="</tbody>"
        return article
            
class Experimentlog:
    ajax=Ajax()
    @cherrypy.expose
    def index(self):
        username=checkPassword()
        if not username:
            return """<meta http-equiv="refresh" content="0;url=/home/login" />"""
            
        style=""" 
            #db {
                 border-collapse: collapse;
                 border: 0;
             }
             table{
                  width:100%;
                  text-align:center;
             }
            #db th{
                 white-space: nowrap;
                background: none repeat scroll 0 0 #B0C4DE;  
                font-weight: normal;
            }
            #db th:hover {background-color: #C0D0E5
            }
            
            #db td{ 
                    font-family: arial,sans-serif;
                    overflow: hidden; 
                    text-overflow: ellipsis;
                    /*word-wrap: break-word; */
                    white-space: nowrap; 
            }

            td{
                font-size: small; 
                padding:6px;
                line-height:120%;
            }
            td a{
                text-decoration: none;
            }
            h1{
                text-align:center;
            }


            """
        javascript="""
        $( document ).ready(function(){
            
        });
        """

        resources= "<style type='text/css'>"+style+"</style>"
        resources+="<script type='text/javascript'>"+javascript+"</script>"
        resources+="<link rel='stylesheet' href='/support/css/dragtable.css' type='text/css' />"
        resources+="<script type='text/javascript' src='/support/javascript/jquery.dragtable.js'></script>"
        resources+="<script type='text/javascript' src='/support/javascript/experimentlog.js'></script>" 
        resources+="<script type='text/javascript' src='/support/javascript/jquery.tablesorter.js'></script> "
        
        
        resources+="<link rel='stylesheet' type='text/css' href='/support/thirdparty/tooltipster/css/tooltipster.css' />"
        resources+="<script type='text/javascript' src='/support/thirdparty/tooltipster/js/jquery.tooltipster.js'></script>"
        
#        viewtype,cols=db.execute("SELECT viewtype, columns FROM lab_members WHERE name=%s",(username,))[0]
#        if viewtype is None:
#            cols=['mousename','']
#        else:
#            cols=cols.split(',')
#        if viewtype=='mouse':
#            c=['checked','']
#        else:
#            c=['','checked']
        article= """<h1 style='margin-bottom: 20px;'>Experiment log</h1>
                    <table id='db' class="tablesorter"></table>"""
        
        
        rightbar= ''
        return glamsTemplate(article, username, resources=resources, rightbar=rightbar)
