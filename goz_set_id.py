import c4d
from c4d import gui

GoZ_CONTAINER_ID = 2000000

#Fill this string in with the one you get from goz_get_id
pathStr = "C:/Users/Public/Pixologic/GoZProjects/Default/ben_affleck_color_uv_v1"

def main():
    bc = op.GetData();
    bc.SetData(GoZ_CONTAINER_ID, pathStr);
    print(" - wrote ZBrushID: " + bc.GetData(GoZ_CONTAINER_ID));
    op.SetData(bc);

if __name__=='__main__':
    main()
