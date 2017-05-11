# lidpix.py

A in image gallery webapp for handling my images, uploading to social
media, making (more or less) public gallery pages, etc.




LIDPIX
Specar / idéer
--------------

Uppladdning av foton
  inkl filnamnsfix
  
Vising av mapp
  tumnaglar
    toggla tumnaglar/ikoner
  visa mer när man scrollar
  bildinfo
  visa mappnamn X
  välja mapp med både länkar och form X
  sorteringsalternativ
  beskrivningsfält
  sociala medier-uppladdning
  allmänna filoperationer
    cp, mv, etc.
    
Inlogg
  olika rättigheter för olika användare
  spara inställningar?
    
Galleri för uppvisning
  batadas (sql)
  zip-länk
  
Inställningar
  färgteman
  spara i användar-db
 

Tech:

nginx
flask
  wand
  flask-login
css
  sass
jquery


Databas till galleri:

En databasfil till hela sajtens gallerier
En bilddatabas per galleri
En standardmapp med bilder per galleri - kan köras över med bildsökväg
Första raden i galleritabellen har data (namn, rättigheter, osv) för själva galleriet
En egen databas med kommentarerna

Databasnamn: halsingland                                                    Rättigheter__________________________________

        ID    Bildfil     Beskrivning   Tid foto          Tid i db          Användare R   Användare W   Grupp R   Grupp W
-------------------------------------------------------------------------------------------------------------------------
Rad 0   0     Gallerinamn Galleribeskr  -                 (gall. skapande)  henrik        henrik        forsa     osv

Rad 1   1     bild1.jpg   Anna på berg  2017-03-02 13:37  2017-05-10 18:45  henrik;nisse  henrik        forsa            
Rad 2   2     /a/b/c.jpg  Henrik ute                                        henrik        henrik        forsa            
Rad 3   3
...
