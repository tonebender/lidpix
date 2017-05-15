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
---------------------

En databasfil till hela sajtens gallerier
En galleritabell med gallerierna
En bildtabell per galleri
En egen tabell med kommentarerna
En standardmapp med bilder per galleri - kan köras över med bildsökväg


Databasfil.db
|
|  Databas med gallerier: gallery
|
|  ID    Gallerinamn  Beskrivning            Tid skapad        Användare R   Användare W   Grupp R   Grupp W
|  ---------------------------------------------------------------------------------------------------------
|  0     halsingland  Hälsingland mars 2017  2017-03-31 12:27  henrik        henrik        forsa     osv
|             \____________________
|                                  \
|                                   \
|  Exempel på databas med bilder: halsingland
|  
|  ID    Bildfil     Beskrivning   Tid foto          Tid i db          Användare R   Användare W   Grupp R   Grupp W
|  -------------------------------------------------------------------------------------------------------------------------
|  0     bild1.jpg   Anna på berg  2017-03-02 13:37  2017-05-10 18:45  henrik;nisse  henrik        forsa            
|  1     /a/b/c.jpg  Henrik ute                                        henrik        henrik        forsa            
|  2
|  ...

