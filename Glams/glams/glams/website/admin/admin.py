# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 11:09:16 2013

@author: kyle
"""

import cherrypy
from glams.databaseInterface.connect import db, db2
from glams.checkpassword.checkpassword import *
from glams.glamsTemplate import glamsTemplate
from glams.checkpassword.checkpassword import checkPassword
import hashlib
import urllib2
from lxml import etree
from lxml.builder import E



    
    
def getAdmin():
    username=checkPassword()
    if not username or username!='admin':
        return """<meta http-equiv="refresh" content="0;url=/home/login" />"""
########################  CREATE ARTICLE ###############################################################################
        
    ###### ADMIN
    changepass=E.div(E.h2('Change admin password:'),
                      E.form(
                             E.div(E.label('Current password:'), E.input({'name':'oldpassword', 'type':'password'})),
                             E.div(E.label('New password:'),E.input({'name':'newpassword1', 'type':'password'})),
                             E.div(E.label('Confirm new password:'),E.input({'name':'newpassword2', 'type':'password'})),
                             E.a({'class':'button-link','onclick':"changepassword($(this).parent().serialize());"},'Change password')))
                             
    changeemail=E.div(E.h2('Change admin email address:'),
                      E.form(
                                 E.div(E.label('Password:'),   E.input({'name':'password','id':'emailpassword', 'type':'password'})),
                                 E.div(E.label('New email:'),  E.input({'name':'newemail1', 'id':'newemail1','type':'text'})),
                                 E.div(E.label('Confirm new email:'),  E.input({'name':'newemail2', 'id':'newemail2','type':'text'})),
                                 E.a({'class':'button-link','onclick':"changeemail($(this).parent().serialize());"},'Change email')))
                                 
                                 
                                 
                                 
    ###### USERS
    adduser=E.div(E.h2('Add User:'),
                      E.form({'id':'adduserform'},
                             E.div(E.label('User name:'),E.input({'name':'newusername', 'type':'text'})),
                             E.div(E.label('Email address:'),E.input({'name':'email', 'type':'text'})),
                             E.div(E.label('User password:'),E.input({'name':'newpassword1', 'type':'password'})),
                             E.div(E.label('Confirm user password:'),E.input({'name':'newpassword2', 'type':'password'})),
                             E.a({'class':'button-link','onclick':"adduser($(this).parent().serialize());"},'Add user')))
    
    userlist=E.select({'name':'user'})
    vals=db.execute("SELECT name FROM lab_members")
    if vals==[]:
        userlist.append(E.option(''))
    else:
        for val in vals:
            userlist.append(E.option(val[0]))
    removeuser=E.div(E.h2('Remove User:'),
                      E.form(
                             E.div(E.label('User name:'),userlist),
                             E.a({'class':'button-link','onclick':"removeuser($(this).parent().serialize());"},'Remove user')))



    
    ##### GENES
    addgene=E.div(E.h2('Add Gene:'),
                  E.form(   
                      E.div(E.label('Gene Name:'),E.input({'name':'genename','type':'text'})),
                      E.div(E.label('Wild Type Presence:'),E.select({'name':'genedefaultstatus'},E.option('+'),E.option('-') )),
                      E.a({'class':'button-link','onclick':"addgene($(this).parent().serialize());"},'Add gene')))
    genelist=E.select({'name':'gene'})
    vals=db.execute("SELECT name FROM genes")
    if vals==[]:
        genelist.append(E.option(''))
    else:
        for val in vals:
            genelist.append(E.option(val[0]))
    removegene=E.div(E.h2('Remove Gene:'),
                  E.form(  
                      E.div(E.label('Gene Name:'),genelist),
                      E.a({'class':'button-link','onclick':"removegene($(this).parent().serialize());"},'Remove gene')))



    ##### STRAINS
    addstrain=E.div(E.h2('Add Strain:'),
                  E.form(
                      E.div(E.label('Strain Name:'),E.input({'name':'strainname','type':'text'})),
                      E.a({'class':'button-link','onclick':"addstrain($(this).parent().serialize());"},'Add Strain')))
    strainlist=E.select({'name':'strain'})
    vals=db.execute("SELECT name FROM strains")
    if vals==[]:
        strainlist.append(E.option(''))
    else:
        for val in vals:
            strainlist.append(E.option(val[0]))
    removestrain=E.div(E.h2('Remove strain:'),
                  E.form({'class':'form'}, 
                         E.div(E.label('Strain Name:'),strainlist),
                         E.a({'class':'button-link','onclick':"removestrain($(this).parent().serialize());"},'Remove strain')))
    
    
    ### PUT ALL THE PIECES TOGETHER
    article=E.div(
                E.div({'id':'notification'},''),
                E.div({'class':'tabs'},
                    E.ul(E.li(E.a({'href':'#tab1'},'Admin')), 
                         E.li(E.a({'href':'#tab2'},'Users')),
                         E.li(E.a({'href':'#tab3'},'Genes')),
                         E.li(E.a({'href':'#tab4'},'Strains'))),
                    E.div(            
                        E.div({'id':'tab1'},changepass, changeemail),
                        E.div({'id':'tab2'},adduser, removeuser),
                        E.div({'id':'tab3'}, addgene,removegene),
                        E.div({'id':'tab4'}, addstrain, removestrain),
                    )
                )
            )
        
    article=etree.tostring(article, pretty_print=True)
                                
                            
####################### STYLE AND JAVASCRIPT #############################################################################            
    style=""" 
h2    {
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #D8D8D8;
    }
input{
    webkit-border-radius: 8px;
    -moz-border-radius: 8px;
    border-radius: 8px;
    padding: 4px;
}

table{
    width:500px;
    margin:10px;
}
#notification{
    display:none;
    padding:5px;
    margin:3px;
    background-color:#FFFF66;
    webkit-border-radius: 8px;
    -moz-border-radius: 8px;
    border-radius: 8px;}
label{
    display: inline-block;
    float: left;
    clear: left;
    width: 200px;
    margin-right: 10px;
    white-space: nowrap;}
    
form .button-link{
    margin-left:0px;
}
form div{margin-bottom:10px;}
    """
    javascript=""" 
var t;
function notify(data){
    $('#notification').html(data);
    $('#notification').show();
    var fadefunc="$('#notification').hide('fade', {}, 200);";
    t=setTimeout(fadefunc,15000);
}


function changepassword(fields){
    $.post('/home/ajax/changepassword/',{fields:fields}, function(data){ notify(data);});}
function changeemail(fields){
    alert(fields);
    $.post('/home/ajax/changeemail/',{fields:fields}, function(data){ notify(data);});}
    
function adduser(fields){
    $.post('/admin/adduser/',{fields:fields}, function(data){ notify(data);});}
function removeuser(fields){
    $.post('/admin/removeuser/',{fields:fields}, function(data){ notify(data);});}
    

 

function addgene(fields){
    $.post('/admin/addgene/',{fields:fields}, function(data){ notify(data);refreshgenes();});}
function removegene(fields){
    $.post('/admin/removegene/',{fields:fields}, function(data){ notify(data);refreshgenes();});}
function refreshgenes(){
    $.post('/admin/refreshgenes/', function(data){ $("select[name='gene']").html(data);});}  
function addstrain(fields){
    $.post('/admin/addstrain/',{fields:fields}, function(data){ notify(data);refreshstrains();});}
function removestrain(fields){
    $.post('/admin/removestrain/',{fields:fields}, function(data){ notify(data);refreshstrains();});}
function refreshstrains(){
    $.post('/admin/refreshstrains/', function(data){ $("select[name='strain']").html(data);});}  


$(document).ready(function(){
   $( ".tabs" ).tabs();
});

    """
    resources="<style type='text/css'>"+style+'</style><script type="text/javascript">'+javascript+'</script>'
    return glamsTemplate(article, username, resources=resources)


class Admin:
    @cherrypy.expose
    def index(self):
        return getAdmin()
        
    @cherrypy.expose
    def adduser(self,fields):
        d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        name=d['newusername']
        if name=='':
            return 'You must enter a username'
        if d['newpassword1']!=d['newpassword2']:
            return "Your passwords don't match"
        password=d['newpassword1']
        if len(password)<5:
            return 'Your password needs to be at least 5 characters long'
        email=d['email']
        hashedpassword=hashlib.md5((password+salt).encode('utf-8')).hexdigest()
        #CHECK IF USER ALREADY EXISTS!!!
        db.execute(""" INSERT INTO lab_members SET name=%s, password=%s, email=%s, viewtype='mouse', columns='mousename,,cagename,,cagename2,,genetics,,' """, (name, hashedpassword, email))
        return "Successfully added '{}' to database".format(name)
    @cherrypy.expose
    def removeuser(self,fields):
        if checkPassword()!='admin':
            return "Only the admin can do this"
        d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        if d['user']=='admin':
            return "You cannot delete the user 'admin'"
        nexperiments=db.execute("""SELECT COUNT(*) FROM lab_members INNER JOIN experiments AS mr ON lab_members.id=mr.lab_member_id WHERE lab_members.name=%s""",(d['user'],))[0][0]
        ncages=db.execute("""SELECT COUNT(*) FROM lab_members INNER JOIN care_taker ON lab_members.id=care_taker.lab_member_id WHERE lab_members.name=%s""",(d['user'],))[0][0]
        if ncages>0 or nexperiments>0:
            return "Unable to remove '{0}' from the database because '{0}' has '{1}' experiments and '{2}' cages in the database".format(d['user'],nexperiments,ncages)
        db.execute('DELETE FROM lab_members WHERE name=%s',(d['user'],))
        return "Sucessfully removed '{0}' from the database".format(d['user'])
        
    @cherrypy.expose
    def addgene(self,fields):
        if checkPassword()!='admin':
            return "Only the admin can do this"
        d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        if d['genedefaultstatus']=='+':
            d['genedefaultstatus']=True
        elif d['genedefaultstatus']=='-':
            d['genedefaultstatus']=False
        if db.execute('SELECT COUNT(*) FROM genes WHERE name=%s',(d['genename'],))[0][0]>0:
            return 'This gene has already been added to the database.'
        db.execute('INSERT INTO genes SET name=%s, default_presence=%s',(d['genename'],d['genedefaultstatus']))
        return "Successfully added '{0}' to the database".format(d['genename'])
    @cherrypy.expose
    def removegene(self,fields):
        if checkPassword()!='admin':
            return "Only the admin can do this"
        d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        ntimesused=db.execute("""SELECT COUNT(*) FROM genetics LEFT JOIN genes ON genetics.gene_id=genes.id WHERE genes.name=%s""",(d['gene'],))[0][0]
        if ntimesused>0:
            return "Unable to remove '{0}' from the database because it is used {1} times.".format(d['gene'],ntimesused)
        db.execute('DELETE FROM genes WHERE name=%s',(d['gene'],))
        return "Sucessfully removed '{0}' from the database".format(d['gene'])
    @cherrypy.expose
    def addstrain(self,fields):
        if checkPassword()!='admin':
            return "Only the admin can do this"
        d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        if db.execute('SELECT COUNT(*) FROM strains WHERE name=%s',(d['strainname'],))[0][0]>0:
            return 'This strain has already been added to the database.'
        db.execute('INSERT INTO strains SET name=%s',(d['strainname'],))
        return "Successfully added '{0}' to the database".format(d['strainname'])
    @cherrypy.expose
    def removestrain(self,fields):
        if checkPassword()!='admin':
            return "Only the admin can do this"
        try:
            d={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        except IndexError:
            return "Server Error.  The function removestrain() was passed variable '{0}'. Try refreshing the page.".format(fields)
        ntimesused=db.execute("""SELECT COUNT(*) FROM mice WHERE strain=%s""",(d['strain'],))[0][0]
        if ntimesused>0:
            return "Unable to remove '{0}' from the database because it is used {1} times.".format(d['strain'],ntimesused)
        db.execute('DELETE FROM strains WHERE name=%s',(d['strain'],))
        return "Sucessfully removed '{0}' from the database".format(d['strain'])
    @cherrypy.expose
    def refreshstrains(self):
        article=''
        vals=db.execute("SELECT name FROM strains")
        if vals==[]:
            article='<option></option>'
        else:
            for val in vals:
                article+='<option>{0}</option>'.format(val[0])
        return article
    @cherrypy.expose
    def refreshgenes(self):
        article=''
        vals=db.execute("SELECT name FROM genes")
        if vals==[]:
            article='<option></option>'
        else:
            for val in vals:
                article+='<option>{0}</option>'.format(val[0])
        return article
        
        
        
        
        
        
        
    
