import c4d, xparticles
from c4d import gui
from xparticles import *
#Welcome to the world of Python


def main():
    tpmas = doc.GetParticleSystem();
    #print tpmas;
    #print op.GetType(); 
    xpEmitter = op;
    
    print Emitter(xpEmitter);
    
    print Emitter(xpEmitter).GetParticleCount();
    print xpEmitter.GetAliveCount();
    
    #pID = tpmaster.AllocParticle();
    #tpmaster.SetPosition(pID, Input2);
    #tpmaster.SetColor(pID, Input1);
if __name__=='__main__':
    main()
