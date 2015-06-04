# encoding: utf-8
import hashlib,cherrypy
from glams.databaseInterface import databaseInterface as DI
from glams.checkpassword.checkpassword import *
from glams.glamsTemplate import glamsTemplate
    
def getlogin(args):
    
###################################################################################################################
#                                                                                             STYLE AND JAVASCRIPT
###################################################################################################################    
    style=""" 
h1 {
    text-align: center; 
    border-bottom:1px solid #D8D8D8;
    padding-bottom: 6px;
}
h1 span {
    font-size: large;
    text-shadow: none;
}
table{
    padding-top:10px;
    width:100%;
    table-layout:fixed;
        -webkit-border-radius: 10px; 
    -moz-border-radius: 10px; 
    border-radius: 10px; 
}

table td{
    width:50%;
    vertical-align: top;
    text-align:left;
}
input {
    -webkit-border-radius: 10px; 
    -moz-border-radius: 10px; 
    border-radius: 10px; 
    padding:2px;
}

    """
    javascript=""" 


    """
    resources="<style type='text/css'>"+style+'</style><script type="text/javascript">'+javascript+'</script>'
    
###################################################################################################################
#                                                                                             SUBMISSION FORMS  
###################################################################################################################           
    existingUserSubmissionForm= """
                                            <table>
                                                <form method="post" action='/home/login/' autocomplete="off" >
                                                    <tr>
                                                        <td>Username:</td>
                                                        <td><input name="username" type="text"/></td>
                                                    </tr>
                                                    <tr>
                                                        <td>Password:</td>
                                                        <td><input name="password" type="password"  /></td>
                                                    </tr>
                                                    <tr>
                                                        <td>
                                                            <input type="submit" value="Submit" />
                                                        </td>
                                                    </tr>
                                                </form>
                                            </table>"""
###################################################################################################################
#                                                                                             ARTICLE
###################################################################################################################    
    article="""<h1 style="text-align:center">Log In</h1>
                <table style="width: 100%;table-layout: fixed; background:-webkit-linear-gradient(bottom, white, #FCFDFF);">
                    <tr>
                        <td>
                            """+existingUserSubmissionForm+"""
                        </td>
                    </tr>
                </table>"""

    name=checkPassword() #Check if user already has correct cookie
    if name is not None:
        return """<meta http-equiv="refresh" content="0;url=/home/" />"""
    # else if there wasn't a cookie, or if it didn't have the right values:
    cookie = cherrypy.response.cookie

        
###################################################################################################################
#                USER LOGIN
###################################################################################################################    
    if 'username' in args and 'password' in args and args['username']!='' and args['password']!='':
        print(args)
        sida=args['username']
        sidb=hashlib.md5((args['password']+salt).encode('utf-8')).hexdigest()
        if DI.isUser(sida,sidb):
            cookie['sida']=sida
            cookie['sida']['expires'] = 12 * 30 * 24 * 60 * 60
            cookie['sida']["path"] = "/"
            cookie['sidb']=sidb
            cookie['sidb']['expires'] = 12 * 30 * 24 * 60 * 60
            cookie['sidb']["path"] = "/"
            cherrypy.request.cookie=cookie
            article= """<meta http-equiv="refresh" content="0;url=/home/" /><h1>Login Sucessful!</h1>"""
        else:
            article= '''<p>Incorrect login.  Please try again.</p>''' + article
    else:
        article= '''<p>Enter username and password.</p>''' + article
        

    return glamsTemplate(article, name, resources=resources)

