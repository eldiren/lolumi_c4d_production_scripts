import c4d, loutils
from c4d import gui, utils

# takes an object with poly selection and breaks it up so the
# selection are children of the parent, also keeps child material
# assignments. created to address the current limitation of Arnold
# Alembic/MaterialX, you can't shade polygon groups
def main():
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)

    for obj in objs:
        loutils.polyselectionbreak(doc, obj)

if __name__=='__main__':
    main()