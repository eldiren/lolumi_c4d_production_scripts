import c4d
from c4d import gui, utils

# takes an object with poly selection and breaks it up so the
# selection are children of the parent, also keeps child material
# assignments. created to address the current limitation of Arnold
# Alembic/MaterialX, you can't shade polygon groups
def main():
    loutils.polyselectionbreak(doc, op)

if __name__=='__main__':
    main()