import c4d, csv
from c4d import gui

def main():
    f = open('H:/Documents/asset_library/color_chart/macbeth_chart_data.txt')
    
    reader = csv.reader(f,delimiter=',')
    
    for name, r, g, b in reader:
        mat = c4d.BaseMaterial(c4d.Mmaterial)
        mat.SetName(name)
        color = c4d.Vector(float(r)/255, float(g)/255, float(b)/255)
        print color
        
        mat[c4d.MATERIAL_COLOR_COLOR] = color
        
        doc.InsertMaterial(mat)
        
    f.close()
    
    c4d.EventAdd()
    
if __name__=='__main__':
    main()
