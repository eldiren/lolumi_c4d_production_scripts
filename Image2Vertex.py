import c4d
import os
from c4d import bitmaps, storage
from c4d import utils,gui
from c4d.gui import GeDialog
from c4d.modules import render
import math


chlist = []
scaleart =  0
button = 0
alpha = 0
orig = bitmaps.BaseBitmap()
objekttext = ""
showo = False
shows = False
bitmapfile = ""


# Dialog erstellen
class Dialog(GeDialog):
    global objekttext, showo, shows
    def __init__(self):
        pass
    
    # Layout definieren
    def CreateLayout(self):
        # Objektname in Beschreibungstext einfügen
        objekttext = "Selected object is: " + op.GetName()
        self.SetTitle("RenameTexture")    # Titel definieren
        
        self.GroupBegin(1000,c4d.BFH_CENTER|c4d.BFH_SCALE|c4d.BFH_FIT,0,8)
        self.AddStaticText(1001,c4d.BFH_CENTER|c4d.BFH_SCALE|c4d.BFH_FIT,800,10,"This is a simple image to vertex map converter!",0);
        self.AddStaticText(1007,c4d.BFH_CENTER|c4d.BFH_SCALE|c4d.BFH_FIT,800,10,"Use at your own risk - Please save Document before use!",0);
        self.AddSeparatorH(0,c4d.BFV_FIT)
        self.AddStaticText(1009,c4d.BFH_CENTER|c4d.BFH_SCALE|c4d.BFH_FIT,800,10,"1) Please select an object.",0);
        self.AddStaticText(1011,c4d.BFH_CENTER|c4d.BFH_SCALE|c4d.BFH_FIT,800,10,"2) Plugin use the first uvw tag of the select polygon object.",0);
        self.AddStaticText(1012,c4d.BFH_CENTER|c4d.BFH_SCALE|c4d.BFH_FIT,800,10,"3) Please select a textur tag at the object.",0);
        self.AddStaticText(1012,c4d.BFH_CENTER|c4d.BFH_SCALE|c4d.BFH_FIT,800,10,"4) Choose a button for use color map, alpha map or load a bitmap file.",0);
        self.AddSeparatorH(0,c4d.BFV_FIT)
        self.GroupEnd()

        self.GroupBegin(1010,c4d.BFH_LEFT,1,1)
        self.AddStaticText(1008,c4d.BFH_LEFT,800,10,objekttext,0);
        self.AddSeparatorH(0,c4d.BFV_FIT)
        self.GroupEnd()
        self.GroupBegin(1010,c4d.BFH_LEFT,2,4)
        self.AddCheckbox(1003,c4d.BFH_LEFT,10,10,"Bitmap COLOR Channel\n To Vertex Map!")
        self.AddStaticText(1012,c4d.BFH_LEFT,800,10,"Show Bitmap in the picture manager",0);
        self.AddCheckbox(1004,c4d.BFH_LEFT,10,10,"Bitmap COLOR Channel\n To Vertex Map!")
        self.AddStaticText(1014,c4d.BFH_LEFT,800,10,"Show scaled bitmap in picture manager",0);
        self.GroupEnd()

        self.GroupBegin(1000,c4d.BFH_LEFT|c4d.BFH_SCALE|c4d.BFH_FIT,1,3)
        self.AddStaticText(1001,c4d.BFH_LEFT,800,10,"How much scale the bitmap before check color :",0);
        self.AddEditSlider(1002,c4d.BFH_LEFT|c4d.BFH_SCALE|c4d.BFH_FIT, 10, 0)      
        self.GroupEnd()

        self.AddSeparatorV(0,c4d.BFV_FIT)
        
        self.GroupBegin(1020,c4d.BFV_CENTER,3,1)
        self.AddButton(1022,c4d.BFH_CENTER,0,40,"Bitmap COLOR Channel\n To Vertex Map!")
        self.AddButton(1023,c4d.BFH_CENTER,0,40,"Bitmap ALPHA Channel\n To Vertex Map!")
        self.AddButton(1024,c4d.BFH_CENTER,0,40,"Load a Bitmap File\n To Vertex Map!")
        self.GroupEnd()
        return True

    
    # Dialog Verarbeitung definieren
    def Command(self,id,msg):
        global chlist, scaleart, orig, alpha, button, showo, shows, bitmapfile
        
        button = id    # Variable button für Benutzung im Hauptprogramm speichern
        if(id < 1002 or id > 1005):# Wurde nur der Slider, oder die Checkboxen verändert? Dann mit True zurückgeben
            if(id == 1022 or id == 1023): # Button links oder mitte (Color oder Alpha) wurde gedrückt
                # Button 1 (Alpha Channel) gedrückt
                if (id == 1023): alpha = 1                
                #Scalierungs Slider speichern
                scaleart = int (self.GetReal(1002) * 0.1)    
                showo= self.GetBool(1003)        
                shows= self.GetBool(1004)        
                self.Close()    # Fenster schließen und weiter im Hauptprogramm
                return True
            else:
                if (id == 1024):# Der Button rechts für die Datei-Auswahl wurde gedrückt
                    # Datei-Dialog öffnen
                    bitmapfile = c4d.storage.LoadDialog (type=c4d.FILESELECTTYPE_IMAGES, title="Select a bitmap file for mapping!", flags=c4d.FILESELECT_LOAD)
                    if not bitmapfile:
                        gui.MessageDialog("no File loading!")
                        return False
                    scaleart = int (self.GetReal(1002) * 0.1)    
                    showo= self.GetBool(1003)        
                    shows= self.GetBool(1004)   
                    self.Close()
                    return True
                else:
                    self.Close()
                    return False
        return True




def main():
    # globale Variablen übernehmen
    global scaleart, orig, alpha, button, showo, shows, bitmapfile

    c4d.CallCommand(13957) # Pythonkonsole leeren
    
    # Objekt ausgewählt? Sonst Fehlerausgabe und beenden
    if not op:
        gui.MessageDialog("Please select a object!")
        return False                        # EXIT
    
    # Prüfen ob das Objekt ein Polygonobjekt ist
    if (op.GetType()== 5100):           # 5100 ist der Type für das Polygonobjekt
        print
    else:
        gui.MessageDialog("ERROR - Object is not a polygon object?")
        return False
        
    # Erstes UVTag auslesen
    uvtag = op.GetTag(c4d.Tuvw)
    # Kein UVW Tag? Sonst Fehlerausgabe und beenden
    if not uvtag:
        gui.MessageDialog("Please assign UVW to the object")
        return
    
    # Dialog aufrufen
    dlg = Dialog();
    dlg.Open(c4d.DLG_TYPE_MODAL)
    if (button == 0): return False    # Kein Button gedrückt (z.B. beim Fenster schließen über Fensterelement X)
    
    # Bitmap Variablen vorbereiten
    smallbitm = bitmaps.BaseBitmap()
    bitmap = bitmaps.BaseBitmap()       
    bitmapPath = bitmapfile

    if (button == 1024):
        abspath = bitmapfile
        bitmapPath = bitmapfile
    else:
        #  Selektiertes Tag auslesen
        ttag = doc.GetActiveTag()
        if (not ttag or not ttag.CheckType(c4d.Ttexture) ) : # Falls kein Material Tag vorhanden oder/und ausgewählt - abbrechen
            gui.MessageDialog("Please attach AND SELECT a Material to the object!")
            return False

        # Material der Variable mat zuweisen
        mat = ttag.GetMaterial()
    
        # Kein Material übernehmen können? Dann Fehlerausgabe und beenden
        if not mat:
            gui.MessageDialog("Please attach a Material with simple bitmap in color Channel to the object!")
            return False # EXIT

        # Farbkanal auslesen falls Variable alpha = 0 (Button links gedrückt)
        if (alpha == 0):
            if (mat[c4d.MATERIAL_USE_COLOR] == True): # ist der Color kanal des Materials aktiv?
                shader = mat[c4d.MATERIAL_COLOR_SHADER] # dann Shader auslesen
            else:
                gui.MessageDialog("Miss COLOR Channel!")
                return False # Exit
        # Alphakanal auslesen falls Variable alpha = 1 (Button mitte gedrückt)
        if (alpha == 1):
            if (mat[c4d.MATERIAL_USE_ALPHA] == True): # ist der Alpha kanal des Materials aktiv?
                shader = mat[c4d.MATERIAL_ALPHA_SHADER] # dann Shader auslesen
            else:
                gui.MessageDialog("Miss ALPHA Channel!")
                return False # Exit
        
        # Farbkanal / Alphakanal konnte nicht gelesen werden?
        if shader is None:
            if (alpha == 0): gui.MessageDialog("Can't get the Shader!\nPlease check that the COLOR Channel is not empty!")
            if (alpha == 1): gui.MessageDialog("Can't get the Shader!\nPlease check that the ALPHA Channel is not empty!")
            return False # EXIT
        
        
        # Shader vor dem auslesen erst abrufbar machen!!!
        bitmapPath = shader[c4d.BITMAPSHADER_FILENAME]
        # Shadertyp und Filename bei Bitmapshader auslesen
        name, path = shader.GetName(), shader[c4d.BITMAPSHADER_FILENAME]
            
        #if bitmapPath is´nt absolute
        if not os.path.dirname(bitmapPath):
            #the document has´nt been saved already ->picture in user library
            if not doc.GetDocumentPath():
                abspath= c4d.storage.GeGetStartupWritePath()+"/"+"tex"+"/"+bitmapPath
            #the picture should be inside the asset´s texture folder    
            else:
                abspath= doc.GetDocumentPath()+"/"+bitmapPath
        else:
            abspath = bitmapPath

    
    
    #  
    if op is not None:    
        
        # Bitmap mit vollem Pfad und Dateinamen Initialisieren:
        result = bitmap.InitWith(abspath)

        if (button <> 1024): irs = render.InitRenderStruct()
        else: irs = True
        if (button <> 1024): shader.InitRender(irs)
        if irs:

            
            # Bitmapdateien in Shadern können absolut oder relativ gespeichert werden.
            # Also muss geprüft werden ob der komplette Pfad ausgelesen wurde!


            # Falls Bitmap ordnungsgemäß verarbeitet wurde:
            if result:
                
                # Die Variable bitmap wurde jetzt auf eine von 3 Arten befüllt:
                if bitmap is not None: # hats geklappt? Dann weiter:
                    width, height = bitmap.GetSize()       # Pixel-Maße  der Bilddatei auslesen
                    bits = bitmap.GetBt()                  # Bittiefe auslesen
                    pixelzahl = width*height               # Gesamtpixelanzahl ermitteln
                    punktezahl = uvtag.GetDataCount()      # Punkteanzahl der UVW-Map ermitteln


                    # Scalierung auf basis des Skalierungs-Sliders berechnen
                    # Aufgrund der Differenz der Auflösung der Bilddatei
                    # und der Auflösung des Polygonmesh (bzw. der UVW-Map)
                    # berechnet sich die Scalierung der Bilddatei.
                    # Die Bilddatei wird skaliert damit in einer hohen Bildauflösung
                    # ein einzelner ausgerissener Pixel den Punkt in einem niedrig aufgelösen Mesh                        # nicht so stark beeinflusst beeinflusst. nur weil der UV-Punkt genau auf diesem Pixel liegt.
                    
                    differenz = pixelzahl - punktezahl             # Differenz ermitteln
                    if scaleart == 10: diffadd = float(differenz)/1000    # Neue Bildgröße = Anzahl der Punkte der UV-Map + Differenz geteilt durch 1000
                    if scaleart == 9: diffadd = float(differenz)/500     # Neue Bildgröße = Anzahl der Punkte der UV-Map + Differenz geteilt durch 500
                    if scaleart == 8: diffadd = float(differenz)/100      # Neue Bildgröße = Anzahl der Punkte der UV-Map + Differenz geteilt durch 100
                    if scaleart == 7: diffadd = float(differenz)/50       # Neue Bildgröße = Anzahl der Punkte der UV-Map + Differenz geteilt durch 50                        
                    if scaleart == 6: diffadd = float(differenz)/20       # Neue Bildgröße = Anzahl der Punkte der UV-Map + Differenz geteilt durch 20
                    if scaleart == 5: diffadd = float(differenz)/10       # Neue Bildgröße = Anzahl der Punkte der UV-Map + Differenz geteilt durh 10
                    if scaleart == 4: diffadd = float(differenz)/5        # Neue Bildgröße = Anzahl der Punkte der UV-Map + Differenz geteilt durch 5
                    if scaleart == 3: diffadd = float(differenz)/3        # Neue Bildgröße = Anzahl der Punkte der UV-Map + ein Drittel der Differenz
                    if scaleart == 1: diffadd = float(differenz)/2        # Neue Bildgröße = Anzahl der Punkte der UV-Map + die Hälfte der Differenz
                    if scaleart == 2: diffadd = float((differenz/3))*2    # Neue Bildgröße = Anzahl der Punkte der UV-Map + Zwei Drittel der Differenz
                    if scaleart == 0: diffadd = differenz          # Neue Bildgröße = Anzahl der Punkte der UV-Map + komplette Defferenz - Also volle Auflösung!

                    # Geladenes Bild bestimmt das Seitenverhältnis. Anhand der alten Menge an Pixel,
                    # der zur Verfügung stehenden Punkte im UV-Mesh und dem Grad der Skalierung (Slider)
                    # wird die neue Bildgröße berechnet. mit gleich bleibenden Seitenverhältnis.

                    # Scalierungsfaktor berechnen: Punkte+Pixelreduzierung geteilt durch Pixelanzahl
                    scalefaktor =  float(punktezahl+diffadd) / (pixelzahl)
                    # Anhand des Skalierungsfaktors der Fläche die Seitenlängen berechnen                        
                    scale_width = int(width * math.sqrt(scalefaktor))           
                    scale_height = int(height * math.sqrt(scalefaktor))
                                               

                    # Kleinere Version der Bitmap erstellen
                    smallbitm.Init(scale_width, scale_height, bits)    # Kleinere Maße, gleiche Bittiefe, gleiches Seitenverhältnis

                    # Copy&Scale Original Bitmap zu Kleine Bitmap
                    bitmap.ScaleBicubic(smallbitm, 0, 0, width-1, height-1, 0, 0, scale_width-1, scale_height-1)
                    
                    if (showo == True): bitmaps.ShowBitmap(bitmap)
                    if (shows == True): bitmaps.ShowBitmap(smallbitm)
                    bitmap = smallbitm

                else:
                    gui.MessageDialog("Bitmap-Error")
                    return False

                if (button <> 1024): shader.FreeRender()
                
                # Abbrechen falls Bitmap nicht übergeben werden konnte
                if bitmap is None:
                    gui.MessageDialog("Bitmap can't load")
                    return False
                        
            else:
                # Im Kanal steckt keine einfache Bitmap-Datei. Wahrscheinlich ein prozeduraler Shader, oder Ebenen ect.
                gui.MessageDialog("In channel ist not a simple bitmap")
                return False                           # EXIT
                
            # Es wird eine Vertexmap erstellt die gleichviele Punkte enthält wie das Polygonobjekt
            vtag = c4d.VariableTag(c4d.Tvertexmap, op.GetPointCount())
            bitmap_w = bitmap.GetBw()              # Breite der Bitmap auslesen
            bitmap_h = bitmap.GetBh()              # Höhe der Bitmap auslesen 
            pixel = (bitmap_w * bitmap_h)          # Pixelanzahl des Skalierten Bildes
            points = uvtag.GetDataCount()          # Punktanzahl des UVW-Tags
            if (op.GetPointCount() > 0):           # Prüfen ob das Objekte Punkte zum auslesen hat
                vertexList = op.GetPointCount() * [0]  # Die Variable für die Vertagsmap-Befüllung mit der Anzahl an Punkten des selektierten Objektesvorbereiten
            else:
                gui.MessageDialog("Object have no read able points! Is it a polygon object?")
                return False
            
            # Schleife liest jedes UVW-tag Polygon aus. Ein Punkt eines UVW-Tags kann mehreren Polygonobjekt-Punkten zugewisen sein
            # Es wird der Reihe nach jedes UV-Polygon ausgelesen. Dann wird das zugehörige Polygon des Objektes ausgelesen und
            # dessen Punkte mit den Farbwerten der Bitmap gefüllt. Die Anzahl der Polygonpunkte müssen nämlich gleich sein mit der Anzahl der Vertexmap-Punkte
            
            # Laut Wiki: Grauwert = 0,299 × Rotanteil + 0,587 × Grünanteil + 0,114 × Blauanteil
            
            for i in xrange(uvtag.GetDataCount()): # Schleife durchläuft Polygone des UVW-Tag
                    uvwdict = uvtag.GetSlow(i)     # UVW-Polygon wird eingelesen
                    objpolygon = op.GetPolygon(i)  # Objekt-Polygon wird eingelesen
                    point_a = op.GetPoint(objpolygon.a) # Objekt Polygon-PunktA ID wird ausgelesen
                    point_b = op.GetPoint(objpolygon.b) # Objekt Polygon-PunktB ID wird ausgelesen
                    point_c = op.GetPoint(objpolygon.c) # Objekt Polygon-PunktC ID wird ausgelesen
                    point_d = op.GetPoint(objpolygon.d) # Objekt Polygon-PunktD ID wird ausgelesen
                    u = uvwdict["a"].x                  # UVW-Koordinate des Punktes A wird ermittelt
                    v = uvwdict["a"].y                  # UVW-Koordinate des Punktes A wird ermittelt
                    w = uvwdict["a"].z
                    ux = bitmap_w*u                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildbreite multipliziert
                    uy = bitmap_h*v                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildhöhe multipliziert
                    color = bitmap.GetPixel(int(ux), int(uy))
                    # "ubjektiver" Helligkeitswert aus RGB ermitteln 
                    weight_a = 0.299 * (float(color[0])/256) + 0.587 * (float(color[1])/256) + 0.114 * (float(color[2])/256)

                    u = uvwdict["b"].x                  # UVW-Koordinate des Punktes B wird ermittelt
                    v = uvwdict["b"].y                  # UVW-Koordinate des Punktes B wird ermittelt
                    w = uvwdict["b"].z
                    ux = bitmap_w*u                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildbreite multipliziert
                    uy = bitmap_h*v                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildhöhe multipliziert
                    color = bitmap.GetPixel(int(ux), int(uy))
                    # "ubjektiver" Helligkeitswert aus RGB ermitteln 
                    weight_b = 0.299 * (float(color[0])/256) + 0.587 * (float(color[1])/256) + 0.114 * (float(color[2])/256)

                    u = uvwdict["c"].x                  # UVW-Koordinate des Punktes C wird ermittelt
                    v = uvwdict["c"].y                  # UVW-Koordinate des Punktes C wird ermittelt
                    w = uvwdict["c"].z
                    ux = bitmap_w*u                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildbreite multipliziert
                    uy = bitmap_h*v                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildhöhe multipliziert
                    color = bitmap.GetPixel(int(ux), int(uy))
                    # "ubjektiver" Helligkeitswert aus RGB ermitteln 
                    weight_c = 0.299 * (float(color[0])/256) + 0.587 * (float(color[1])/256) + 0.114 * (float(color[2])/256)

                    u = uvwdict["d"].x                  # UVW-Koordinate des Punktes D wird ermittelt
                    v = uvwdict["d"].y                  # UVW-Koordinate des Punktes D wird ermittelt
                    w = uvwdict["d"].z
                    ux = bitmap_w*u                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildbreite multipliziert
                    uy = bitmap_h*v                     # UV-Koordinate liegt zwischen 0-1 und wird mit der Bildhöhe multipliziert
                    color = bitmap.GetPixel(int(ux), int(uy))
                    # "ubjektiver" Helligkeitswert aus RGB ermitteln 
                    weight_d = 0.299 * (float(color[0])/256) + 0.587 * (float(color[1])/256) + 0.114 * (float(color[2])/256)

                    # Helligkeitswerte der Vertexmap Wert-Variable zuweisen
                    vertexList[objpolygon.a] = weight_a
                    vertexList[objpolygon.b] = weight_b
                    vertexList[objpolygon.c] = weight_c
                    vertexList[objpolygon.d] = weight_d
                        
            if vtag: # falls die Vertexmap auch wirlich erstellt wurde kann es weiter gehen:
                op.InsertTag(vtag) # Vertexmap wird an dem objekt erstellt

                vtag.SetAllHighlevelData(vertexList) # erstellte Vertexmap wird mit den ermittelten Werten gefüllt
                        
            c4d.EventAdd() # Veränderung in der Szene mitteilen, damit C4D aktualisiert.
        else:
            # Das Vorbereiten der Bitmapinitialisierung hat fehlgeschlagen:
            gui.MessageDialog("Can Not Init Shader")
            if irs == c4d.INITRENDERRESULT_OUTOFMEMORY: gui.MessageDialog("Out Of Memory")
            if irs == c4d.INITRENDERRESULT_ASSETMISSING: gui.MessageDialog("Texture Not Assigned")
            if irs == c4d.INITRENDERRESULT_UNKNOWNERROR: gui.MessageDialog("Unknown Error")
            if irs == c4d.INITRENDERRESULT_THREADEDLOCK: gui.MessageDialog("Threaded Lock")
        
        gui.MessageDialog(" - Finish - ")

if __name__=='__main__':
    main()
