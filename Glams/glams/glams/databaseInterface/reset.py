# encoding: utf-8
import os
if __name__=='__main__':
    from connect import db, importconfig
    rootDirectory=os.path.abspath('../..')
    
else:
    from .connect import db, importconfig
    rootDirectory=os.getcwd()
import hashlib

def reset():
    #How to add a column to an existing table without reset:  ALTER TABLE oldtable ADD newfield BOOL; 

    print('Starting Database Reset')
    db.execute("DROP TABLE IF EXISTS strains",commit=True);             print('    Dropped Table "strains"')
    db.execute("DROP TABLE IF EXISTS litters",commit=True);             print('    Dropped Table "litters"')
    db.execute("DROP TABLE IF EXISTS care_taker",commit=True);          print('    Dropped Table "care_taker"')
    db.execute("DROP TABLE IF EXISTS housing",commit=True);             print('    Dropped Table "housing"')
    db.execute("DROP TABLE IF EXISTS cages",commit=True);               print('    Dropped Table "cages"')
    db.execute("DROP TABLE IF EXISTS experiments",commit=True);   print('    Dropped Table "experiments"')
    db.execute("DROP TABLE IF EXISTS genetics",commit=True);            print('    Dropped Table "genetics"')
    db.execute("DROP TABLE IF EXISTS lineage",commit=True);             print('    Dropped Table "lineage"')
    db.execute("DROP TABLE IF EXISTS genes",commit=True);               print('    Dropped Table "genes"')
    db.execute("DROP TABLE IF EXISTS lab_members",commit=True);         print('    Dropped Table "lab_members"')
    db.execute("DROP TABLE IF EXISTS mice",commit=True);                print('    Dropped Table "mice"')



    queries=[]
    
    
    queries.append("""
            CREATE TABLE mice (
                                    
                                    id              INT NOT NULL AUTO_INCREMENT,  PRIMARY KEY(id),
                                    name            VARCHAR(255) CHARACTER SET utf8 collate utf8_bin NOT NULL UNIQUE,
                                    strain          VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    genotyped       BOOL,
                                    sex             VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    life_status     VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    breeding_status VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    DOB             DATETIME,
                                    DOD             DATETIME,
                                    cause_of_death  VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    tag             VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    notes           TEXT(65535) CHARACTER SET utf8 collate utf8_bin
            )""")
    queries.append("""
            CREATE TABLE lab_members (
                                    
                                    id              INT NOT NULL AUTO_INCREMENT,  PRIMARY KEY(id),
                                    name            VARCHAR(255) CHARACTER SET utf8 collate utf8_bin UNIQUE,
                                    password        VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    email           VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    viewtype        VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    columns         VARCHAR(500) CHARACTER SET utf8 collate utf8_bin,
                                    sortby          VARCHAR(255) CHARACTER SET utf8 collate utf8_bin
            )""")
            
    queries.append("""
            CREATE TABLE genes (
                                    
                                    id              INT NOT NULL AUTO_INCREMENT,  PRIMARY KEY(id),
                                    name            VARCHAR(255) CHARACTER SET utf8 collate utf8_bin UNIQUE,
                                    default_presence BOOL
            )""")
            
    queries.append("""
            CREATE TABLE strains (
                                    
                                    id              INT NOT NULL AUTO_INCREMENT,  PRIMARY KEY(id),
                                    name            VARCHAR(255) CHARACTER SET utf8 collate utf8_bin UNIQUE
            )""")
    queries.append("""
            CREATE TABLE cages
            (
                                    id                  INT NOT NULL AUTO_INCREMENT,  PRIMARY KEY(id),
                                    name                VARCHAR(255) CHARACTER SET utf8 collate utf8_bin NOT NULL UNIQUE,
                                    active              BOOL,
                                    expectingpl         BOOL,
                                    notes               TEXT(65535) CHARACTER SET utf8 collate utf8_bin,
                                    cagegroup           VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    date_activated      DATE,
                                    date_inactivated    DATE,
                                    location            VARCHAR(255) CHARACTER SET utf8 collate utf8_bin
            )""")
    queries.append("""
            CREATE TABLE genetics
            (
                                    mouse_id                INT NOT NULL, 
                                    FOREIGN KEY(mouse_id)   REFERENCES mice(id) ON DELETE CASCADE,
                                    gene_id                 INT NOT NULL,
                                    FOREIGN KEY(gene_id)    REFERENCES genes(id) ON DELETE CASCADE,
                                    zygosity                VARCHAR(255) CHARACTER SET utf8 collate utf8_bin
            )""")
    queries.append("""
            CREATE TABLE lineage
            (
                                    mother_id                 INT NOT NULL, 
                                    FOREIGN KEY(mother_id)    REFERENCES mice(id) ON DELETE CASCADE,
                                    father_id                 INT NOT NULL,
                                    FOREIGN KEY(father_id)    REFERENCES mice(id) ON DELETE CASCADE,
                                    child_id                  INT NOT NULL UNIQUE,
                                    FOREIGN KEY(child_id)     REFERENCES mice(id) ON DELETE CASCADE
            )""")
    queries.append("""
            CREATE TABLE experiments
            (
                                    id                              INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(id),
                                    mouse_id                        INT NOT NULL, 
                                    FOREIGN KEY(mouse_id)           REFERENCES mice(id) ON DELETE CASCADE,
                                    lab_member_id                   INT NOT NULL,
                                    FOREIGN KEY(lab_member_id)      REFERENCES lab_members(id) ON DELETE CASCADE,
                                    date                            DATETIME,
                                    description                     VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    notes                           TEXT(65535) CHARACTER SET utf8 collate utf8_bin,
                                    status                          VARCHAR(255) CHARACTER SET utf8 collate utf8_bin,
                                    filenames                       TEXT(65535) CHARACTER SET utf8 collate utf8_bin
            )""")

    queries.append("""
            CREATE TABLE housing
            (
                                    mouse_id                    INT NOT NULL, 
                                    FOREIGN KEY(mouse_id)       REFERENCES mice(id) ON DELETE CASCADE,
                                    cage_id                     INT NOT NULL, 
                                    FOREIGN KEY(cage_id)        REFERENCES cages(id) ON DELETE CASCADE,
                                    start_date                  DATETIME,
                                    end_date                    DATETIME,
                                    currentcage                 BOOL
            )""")
    queries.append("""
            CREATE TABLE care_taker
            (
                                    cage_id                     INT NOT NULL, 
                                    FOREIGN KEY(cage_id)        REFERENCES cages(id) ON DELETE CASCADE,
                                    lab_member_id               INT NOT NULL,
                                    FOREIGN KEY(lab_member_id)  REFERENCES lab_members(id) ON DELETE CASCADE
            )""")
    queries.append("""
            CREATE TABLE litters
            (
            
                                    cage_id                     INT NOT NULL, 
                                    FOREIGN KEY(cage_id)        REFERENCES cages(id) ON DELETE CASCADE,
                                    DOB                         DATETIME,
                                    notes                       TEXT(65535) CHARACTER SET utf8 collate utf8_bin,
                                    mother_id                   INT NOT NULL, 
                                    FOREIGN KEY(mother_id)      REFERENCES mice(id) ON DELETE CASCADE,
                                    father_id                   INT NOT NULL,
                                    FOREIGN KEY(father_id)      REFERENCES mice(id) ON DELETE CASCADE
            )""")
            
    for query in queries:
        print('executing query')
        db.execute(query,commit=True)
    
    print('Reset Finished')
    print('Adding admin.')
    password='password'
    config=importconfig()
    salt=config['salt']
    hashedpassword=hashlib.md5((password+salt).encode('utf-8')).hexdigest()
    db.execute(""" INSERT INTO lab_members SET name='admin', password=%s, email='', viewtype='mouse', columns='mousename,,cagename,,cagename2,,genetics,,' """,(hashedpassword,))
    print('Finished adding admin.')

if __name__=='__main__':
    print('I turned this function off for safety')
    #reset()
