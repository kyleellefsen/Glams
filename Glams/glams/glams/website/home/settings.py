# encoding: utf-8

from glams.databaseInterface import databaseInterface as DI
from glams.checkpassword.checkpassword import *
from glams.glamsTemplate import glamsTemplate
from lxml import etree
from lxml.builder import E

def getsettings():
    username=checkPassword()
    if not username:
        return """<meta http-equiv="refresh" content="0;url=/home/login" />"""
########################  CREATE ARTICLE ###############################################################################
    changepass=E.div(E.h2('Change password:'),
                      E.form(
                             E.div(E.label('Current password:'), E.input({'name':'oldpassword', 'type':'password'})),
                             E.div(E.label('New password:'),E.input({'name':'newpassword1', 'type':'password'})),
                             E.div(E.label('Confirm new password:'),E.input({'name':'newpassword2', 'type':'password'})),
                             E.a({'class':'button-link','onclick':"changepassword($(this).parent().serialize());"},'Change password')))
                             
    changeemail=E.div(E.h2('Change email address:'),
                      E.form(
                                 E.div(E.label('Password:'),   E.input({'name':'password','id':'emailpassword', 'type':'password'})),
                                 E.div(E.label('New email:'),  E.input({'name':'newemail1', 'id':'newemail1','type':'text'})),
                                 E.div(E.label('Confirm new email:'),  E.input({'name':'newemail2', 'id':'newemail2','type':'text'})),
                                 E.a({'class':'button-link','onclick':"changeemail($(this).parent().serialize());"},'Change email')))
    article=E.div(
                E.div({'id':'notification'},''),
                    E.div(changepass, changeemail))
    article=etree.tostring(article, pretty_print=True)
                                
                            
####################### STYLE AND JAVASCRIPT #############################################################################            
    style=""" 
h2    {
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #D8D8D8;}
input{
    webkit-border-radius: 8px;
    -moz-border-radius: 8px;
    border-radius: 8px;
    padding: 4px;}

table{
    width:500px;
    margin:10px;}
    
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
    
form .button-link{margin-left:0px;}
    
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
    $.post('/home/ajax/changeemail/',{fields:fields}, function(data){ notify(data);});}

    """
    resources="<style type='text/css'>"+style+'</style><script type="text/javascript">'+javascript+'</script>'
    return glamsTemplate(article, username, resources=resources)










