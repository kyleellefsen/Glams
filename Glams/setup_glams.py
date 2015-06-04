# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 14:55:58 2013

@author: kyle
"""
import os.path
import os, cherrypy
import time
from lxml import etree
from lxml.builder import E
import urllib2
import mysql.connector



def setup_glams():
    ''' 1) check if config.txt is created.  If it isn't, display a webpage to create one.'''
    print('Setting up glams...')
    try:
        from glams.databaseInterface.connect import importconfig
    except IOError:
        config={'database': 'glams', 'user': '', 'mysql_IP_address': 'localhost', 'calendarTag': '<div></div>', 'password': '', 'salt': '', 'port': '3306'}
        # config.txt doesn't exist.  This means we have to make it.
        from glams.glamsTemplate import glamsTemplate
        article=E.div(E.div({'id':'notification'},''),
                      E.h2('Configure GLAMS:'),
                      E.form(
                             E.div(E.label('MySQL IP address:'), E.input({'name':'mysql_IP_address', 'value':config['mysql_IP_address'],'type':'text'}), E.span('This is the IP address of your MySQL server. Leave as "localhost" if running on this computer. ')),
                             E.div(E.label('MySQL port:'), E.input({'name':'port', 'value':config['port'],'type':'text'}), E.span('This is the port to access your mysql server. This is almost always "3306".' )),
                             E.div(E.label('GLAMS database name:'), E.input({'name':'database', 'value':config['database'],'type':'text'}), E.span('This is the name of the MySQL database (aka schema).  This should be "glams".')),
                             E.div(E.label('GLAMS database salt:'), E.input({'name':'salt', 'value':config['salt'],'type':'text'}), E.span("This should be 5-10 random characters to use as a salt for better password encryption")),
                             E.div(E.label('MySQL user name:'), E.input({'name':'user', 'value':config['user'],'type':'text'}), E.span("Enter the name of the user you created to access the MySQL database.")),
                             E.div(E.label('MySQL password:'), E.input({'name':'password', 'value':config['password'],'type':'text'}), E.span("This is the above user's password. WARNING: Do not use your regular lab password.  This password will be saved in a textfile.")),
                             E.a({'class':'button-link','onclick':"config_glams($(this).parent().serialize());"},'Save Configuration')))
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
            
            
            function config_glams(fields){
                notify('Testing connection to mysql server...')
                $.post('/ajax/config_glams/',{fields:fields}, function(data){ 
                    notify(data);
                    
                
                });}
            

            
        """
        resources="<style type='text/css'>"+style+'</style><script type="text/javascript">'+javascript+'</script>'
        return glamsTemplate(article, username='None', resources=resources)
        
class Ajax:
    @cherrypy.expose
    def index(self):
        return 'This is the ajax under setup_glams'
    @cherrypy.expose
    def config_glams(self,fields):
        reply=''
        config={urllib2.unquote(i.split('=')[0]):urllib2.unquote(i.split('=')[1]) for i in [tmp for tmp in fields.split('&')]}
        if config['mysql_IP_address']=='':
            return 'You must enter an IP address'
        if config['port']=='':
            return 'You must enter a port'
        if config['database']=='':
            return 'You must enter a database'
        if config['salt']=='':
            return 'You must enter a random set of characters for the salt'
        if len(config['salt'])<5:
            return 'Your salt must be at least 5 characters long'
        if config['user']=='':
            return 'You must enter a MySQL user'
        if config['password']=='':
            return 'You must enter a password for your MySQL user'
        try:
            cnx=mysql.connector.connect(host=str(config['mysql_IP_address']), 
                                            user=str(config['user']), 
                                            database=str(config['database']), 
                                            password=str(config['password']), 
                                            port=int(config['port']))
        except mysql.connector.Error as e:
#            print("Error code:", e.errno)        # error number
#            print("SQLSTATE value:", e.sqlstate) # SQLSTATE value
#            print("Error message:", e.msg)       # error message
#            print("Error:", e)                   # errno, sqlstate, msg values
#            s = str(e)
#            print("Error:", s)                   # errno, sqlstate, msg valuesprint
            if e.errno==1049: #Unknown database
                reply+='Creating GLAMS database. '
                cnx=mysql.connector.connect(host=str(config['mysql_IP_address']), 
                                user=str(config['user']), 
                                password=str(config['password']), 
                                port=int(config['port']))
                cursor=cnx.cursor(buffered=True)
                print(str(config['database']))
                try:
                    f=open('config.txt', 'w')
                except IOError:
                    return 'You must have administrator privledges to save the configuration.  Close GLAMS and reopen as administrator.'
                con='mysql_IP_address={0}\n'.format(config['mysql_IP_address'])
                con+='port={0}\n'.format(config['port'])
                con+='database={0}\n'.format(config['database'])
                con+='salt={0}\n'.format(config['salt'])
                con+='user={0}\n'.format(config['user'])
                con+='password={0}\n'.format(config['password'])
                con+='calendarTag=<p>No Calendar Yet</p>\n'
                f.write(con)
                f.close()
                time.sleep(1)
                #cursor.execute("CREATE DATABASE %s",('glams',))
                cursor.execute("CREATE DATABASE glams")
                print("Database 'glams' created.")
                cursor.execute("GRANT ALL ON glams.* TO '"+config['user']+"'@'localhost'")
                cursor.close()
                cnx.commit()
                cnx.close()
                from glams.databaseInterface.reset import reset
                reset()
                return "Successfully created GLAMS database. Please restart GLAMS by shutting it down and running it again. Then refresh this page. Login as 'admin' with password 'password'. "
            elif e.errno==2003: #Can't connect to mysql server.  Maybe an incorrect IP address?
                return 'Error connecting to MySQL database:'+str(e)
            elif e.errno==1045: #Incorrect password or permissions
                return 'Error connecting to MySQL database:'+str(e)
            
            
        try:
            f=open('config.txt', 'w')
        except IOError:
            return 'You must have administrator privledges to save the configuration.  Close GLAMS and reopen as administrator.'
        con='mysql_IP_address={0}\n'.format(config['mysql_IP_address'])
        con+='port={0}\n'.format(config['port'])
        con+='database={0}\n'.format(config['database'])
        con+='salt={0}\n'.format(config['salt'])
        con+='user={0}\n'.format(config['user'])
        con+='password={0}\n'.format(config['password'])
        con+='calendarTag=<p>No Calendar Yet</p>\n'
        f.write(con)
        f.close()
        reply+="Connection works. Configuration file written. Please restart GLAMS by shutting it down and running it again. Then refresh this page. Login as 'admin' with password 'password'. "
        return reply
        
        

def command_line_setup():
    if os.path.isfile('config.txt'):
        print("""\n\n****WARNING****\n\n DO NOT RUN THIS FILE IF YOU HAVE ALREADY ADDED INFORMATION TO THE DATABASE!!!\n\nTHIS FILE WILL RESET YOUR DATABASE.\n\nYou're trying to run setup.py but you already have a config file. You can edit the information in your config file in a text editor.  If you still want to run this file and reset your database, delete your 'config.txt' file.""")
    else:
        mysql_IP_address=raw_input('Enter the ip address of your mysql server (leave blank if running on this computer): ')
        if mysql_IP_address=='':
            mysql_IP_address='localhost'
        database=raw_input('Enter the name of the MySQL database (e.g. glams): ')
        if database=='':
            database='glams'
        user=raw_input('Enter the name of the user you created to access the mysql database: ')
        password=raw_input("Enter the password for user '{}':".format(user))
        port=raw_input("Enter the port to access your mysql server (leave blank for the default '3306'): ")
        if port=='':
            port='3306'
        salt=raw_input("Enter a 5-10 character random combination of characters to use as a salt for better password encryption: ")
        
        config="""mysql_IP_address={0}
user={1}
database={2}
password={3}
port={4}
salt={5}
calendarTag=<p>No Calendar Yet</p>""".format(mysql_IP_address,user,database,password,port,salt)
        
        f=open('config.txt', 'w')
        f.write(config)
        f.close()
        print('Creating GLAMS database')
        time.sleep(2)
        from glams.databaseInterface.reset import reset
        reset()
        print('Sucessfully created GLAMS database')
        

        
    

if __name__=='__main__':
    command_line_setup()
