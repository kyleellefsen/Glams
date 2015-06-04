# encoding: utf-8
if __name__ == 'users':
    from connect import db
else:
    from .connect import db


def isUser(name, hashedpassword):
    data=db.execute("""SELECT password FROM lab_members WHERE name=%s """, (name,), commit=False)
    try:
        data=data[0][0]
    except IndexError:
        return False
    if data==hashedpassword:
        return True
    else:
        return False
        
 
def userExists(username):
    data=db.execute('''SELECT name FROM lab_members WHERE name=%s''', (username,), commit=False)
    try:
        user=data[0][0]
        return True
    except Exception:
        return False

