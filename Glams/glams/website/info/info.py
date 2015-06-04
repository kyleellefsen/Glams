# -*- coding: utf-8 -*-
import cherrypy
from glams.glamsTemplate import glamsTemplate
from glams.checkpassword.checkpassword import checkPassword
from lxml import etree
from lxml.builder import E

class Info:
    @cherrypy.expose
    def index(self):
        username=checkPassword()
        animalinfo=E.div(
                    E.h2('Breeding'),
                    E.ul(
                        E.li("To see if an animal is pregnant, weigh her every 7 days."),
                        E.li("To get an accurate estimate of the birth day, check every day."),
                        E.li("You can look at anatomical features before P5 to identify date of birth."),
                        E.li("The founder line is the first generation. You should mate descendants with the founder line often, to reduce genetic variability."),
                        E.li("Breed females between P56 (8 weeks) to P120 (4 months).  Younger females between P42 (6 weeks) to P56 can be breed but won't be good mothers.  Females older than 4 months can breed, but you must use the 'Whitten effect' by dropping male waste in the cage.  This should induce estrous cycle in female after 1 to 2 days."),
                        E.li("Breed males after they reach sexual maturity at P56 (8 weeks). ")
                    ),
                     E.h2('Weaning'),
                     E.ul(
                         E.li("Wean at P19 to P23.  They need to be able to reach the water at the top of the cage."),
                         E.li("The vet staff will wean at P23. This costs a lot of money, so wean before then."),
                         E.li("To wean, separate out genders in different cages, don't put more than 4 in a cage or they will fight."),
                         E.li("When weaning, look for teeth that curve upwards and sac them.  If you catch early enough, trim teeth with scissors.")
                     ),
                     E.h2('Genotyping'),
                     E.ul(
                         E.li("To genotype, clip P3-P7 toes, mail to ",E.a({'href':'http://www.transnetyx.com/'},'Transnetyx'),"."),
                         E.li("To determine if td-Tomato positive and PV-Cre positive, shine a green laser at the base of the tail and look for fluorescence.")
                     )
                )
        glamsQA=E.div(
                    E.h2('What do the colors over animal names mean?'),
                    E.div("Color indicates gender. Blue means male, red means female, and yellow indicates 'neither' or 'unknown'."),
                    E.h2('I just started GLAMS.  How do I log in?'),
                    E.div("The administrator user name is 'admin' and the default password is 'password'."),
                )
        article=E.div(
                E.div({'class':'tabs'},
                    E.ul(E.li(E.a({'href':'#tab1'},'GLAMS Q&A')), 
                         E.li(E.a({'href':'#tab2'},'Animal Information')),
                         E.li(E.a({'href':'#tab3'},'')),
                         E.li(E.a({'href':'#tab4'},''))),
                    E.div(            
                        E.div({'id':'tab1'},glamsQA),
                        E.div({'id':'tab2'},animalinfo),
                        E.div({'id':'tab3'}),
                        E.div({'id':'tab4'}),
                    )
                )
            )
        article=etree.tostring(article, pretty_print=True)
        style="""
        li{display:block;}
        """
        javascript=""" 
            $(document).ready(function(){
               $( ".tabs" ).tabs();
            });

        """
        resources="<style type='text/css'>"+style+'</style><script type="text/javascript">'+javascript+'</script>'
        return glamsTemplate(article,username, resources=resources)
