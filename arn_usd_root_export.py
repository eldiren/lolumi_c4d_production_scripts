import c4d, loutils
from c4d import gui, utils

# exports each root object and it's children as a USD file

# in the file select it expects a path you want to dump the files
# to, the filename doesn't matter

# from c4d_symbols.h
ARNOLD_SCENE_EXPORT_COMMAND = 1029993

def main():
    filePath = c4d.storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, "Export path...", c4d.FILESELECT_SAVE)
    paths = filePath.rsplit('\\', 1)

    filePath = paths[0] + "/"

    obj = doc.GetFirstObject()
    while(obj):
        doc.SetActiveObject(obj)
        fileName = filePath + obj.GetName() + ".usd"

        options = c4d.BaseContainer()
        options.SetFilename(0, fileName) # file name
        options.SetInt32(6, 0) # start frame
        options.SetInt32(7, 0) # end frame
        options.SetInt32(11, 1) # export selected
        options.SetBool(13, True) #  export object hierarchy
        options.SetInt32(14, 193472369) # Export USD

        doc.GetSettingsInstance(c4d.DOCUMENTSETTINGS_DOCUMENT).SetContainer(ARNOLD_SCENE_EXPORT_COMMAND, options)
        c4d.CallCommand(ARNOLD_SCENE_EXPORT_COMMAND) # export the file

        print(fileName) #debug

        obj = obj.GetNext()

if __name__=='__main__':
    main()