# encoding: utf-8

def glamsTemplate(article, username=None, resources='', rightbar=''):
    '''Wraps an article string in the html template'''
    if username:
        userLogin="""<a href="/home">""" + username +"""</a>"""
    else:
        userLogin="""<a href="/home/login/">Login</a>"""
    webpage="""<!DOCTYPE HTML>
            <html>
            <head>
                <title>Glams</title>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                <link href='http://fonts.googleapis.com/css?family=Belleza' rel='stylesheet' type='text/css'>
                <link rel="stylesheet" type="text/css" href="/support/css/almanacstyle.css" />
                <link rel="stylesheet" type="text/css" href="/support/css/searchform.css" />
                <link rel="stylesheet" type="text/css" href="/support/css/sharebubble.css" />
                <script type="text/javascript" src="/support/javascript/jquery.js"></script>
                <script type="text/javascript" src="/support/javascript/jquery-ui.js"></script>
                <script type="text/javascript" src="/support/javascript/glamsscript.js"></script>
                <script type="text/javascript" src="/support/javascript/jquery-color.js"></script>   
                <link rel="icon" type="image/png" href="/support/images/neurons.png">
                """+resources+"""
            </head>
            <body>
                <div class='bubble' style='display:none;'></div>
                <div id="everything">
                <header>
                        <div id='logo'><a href='/'> <p style="color: white;font-family:'Belleza', sans-serif;">Glams Database</p> </a></div>
             <!--       <form id='topsearchform' method="post"  action="/search/" class="searchform">
                        <input class="searchfield" name="tags" type="text" value="Search..." onfocus="if (this.value == 'Search...') {this.value = '';}" onblur="if (this.value == '') {this.value = 'Search...';}" />
                        <input class="searchbutton" type="submit" value="Go" />
                    </form> -->
                    <div  id='userLoginBox'>
                        <div  id='userLogin'>"""+userLogin+"""</div>"""
    if username:
        webpage+="""
                        <ul id='userLoginList'>
                            <li><a class='button-link' href='/home/logout/'>Log out</a></li>
                            <li><a class='button-link' href='/home/settings/'>Account Settings</a></li>
                        </ul>"""
    webpage+="""
                        </div>
                </header>
                <div id="content">
                    <article>"""
    webpage+=       article+"""</article>
                    <div id='between_article_and_aside'></div>
                        <aside>"""
    webpage+=rightbar+"""</aside>
                    </div>
                </div>
            <footer><a href='http://scitru.com/kyleellefsen/'>Kyle Ellefsen. © 2015-2016  </footer>
            </body>
            </html>"""
    return webpage
