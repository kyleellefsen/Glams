# -*- coding: utf-8 -*-

import os, cherrypy
os.chdir(os.path.split(os.path.realpath(__file__))[0])
try:
    from glams.website.database.database import Database #this will fail if database is not set up correctly
    from glams.website.info.info import Info
    from glams.website.home.home import Home
    from glams.website.experimentlog.experimentlog import Experimentlog
    from glams.website.admin.admin import Admin
    from glams.website.cal.cal import Calendar
    webpage="""<!DOCTYPE HTML>
    <html>
    <head>
        <title>GLAMS</title>
        <link href="/support/css/almanacstyle.css" rel="stylesheet" type="text/css" />
        <link href="/support/css/homepage.css" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="/support/javascript/jquery.js"></script>
        <script type="text/javascript" src="/support/javascript/jquery-ui.js"></script>
        <link rel="stylesheet" type="text/css" href="/support/css/searchform.css" />
    
        <script type="text/javascript">
        $(document).ready(function () {
            var t;
            $('#menu').hover(
                function(){
                    clearTimeout(t);
                    $('.menu_body').show("fade", {}, 700);
                },function(){
                t=setTimeout("$('.menu_body').hide('fade', {}, 700);",3000);
            });
            $('#menu').click(function(){
                $('.menu_body').show("fade", {}, 700);
            });
        });
        </script>
    </head>
    
    
    <body>
    <div class=wrapper>
        <div id='menu'>
            <h2 class="menu_head">Glams</h2>
            <ul class="menu_body"> 
                <li><a href="/database/">Database</a></li>
                <li><a href="/info/">Information</a></li>
                <li><a href="/home/login/">Log in</a></li>
            </ul>
        </div>
    </div>  
    
    
    </body>
    </html>"""
    class Root:
        database=Database()
        info=Info()
        experimentlog=Experimentlog()
        home=Home()
        admin=Admin()
        calendar=Calendar()
        webpage= webpage
        @cherrypy.expose
        def index(self):
            return Root.webpage
            
except IOError:
    from setup_glams import setup_glams, Ajax
    webpage=setup_glams()
    class Root:
        webpage=webpage
        ajax=Ajax()
        @cherrypy.expose
        def index(self):
            return Root.webpage



 


rootDirectory=os.getcwd()
config={
        'global':{
            'server.thread_pool':15
        },
        '/': {
                'tools.staticdir.root' : rootDirectory,
                'tools.encode.encoding':'utf-8',
                'tools.encode.on' :True,
                'tools.decode.on' : True,
            },
        '/support':{
                'tools.staticdir.on': True,
                'tools.staticdir.dir' : 'support',
            },
    }
cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 80}) #To bind on port 80, you must have root privileges.  To run it in the wild, bind to port 80.  For testing, do port 8080 .

cherrypy.quickstart(Root(), config=config)
