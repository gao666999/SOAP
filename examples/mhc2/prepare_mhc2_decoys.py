import SOAP.decoys
import shutil
import os
import sys
import glob
import pickle

# define the paths for the decoys; assume they are found under the directory
# containing this script
workingPath = os.path.abspath(os.path.dirname(sys.argv[0]))
originalDecoyPath = os.path.join(workingPath,'mhc2_original')
preparedDecoyPath = os.path.join(workingPath,'mhc2')
decoySetName='mhc2'

#copy the files from originalDecoyPath to target path
"""The pre-prepared decoys directory should look like the following:
    root:
        decoySet1: could use the PDB code of the receptor here
            Decoy files
            [*base*]: if this file is present in this directory, it should be the receptor file shared by all decoys, and the final decoys are generated by combining this
            rmsd.pickle
        decoySet2
        ...
"""
fl=os.listdir(originalDecoyPath)
for f in fl:
    if not os.path.isdir(os.path.join(originalDecoyPath,f)):
        continue
    shutil.rmtree(os.path.join(preparedDecoyPath,f), ignore_errors=True)
    os.makedirs(os.path.join(preparedDecoyPath,f))
    os.chdir(os.path.join(preparedDecoyPath,f))
    for d in glob.glob(os.path.join(originalDecoyPath,
                                    f, 'selected_peptides','*')):
        shutil.copy(d, '.')
    shutil.move('pMHC_'+f+'.pdb', 'base.pdb')
    # Touch
    open('needattachtobase', 'w')
    rl=open(os.path.join(originalDecoyPath,f,'all_scores.txt')).read().split('\n')
    rmsddict={}
    scoredict={}
    for item in rl:
        if len(item)<10:
            continue
        il=item.split(',')
        rmsddict[il[0].strip()[:-4]]=float(il[2])
        scoredict[il[0].strip()[:-4]]=float(il[1])
    pickle.dump(rmsddict,open('rmsd.pickle','w'))
    pickle.dump(scoredict,open('score.pickle','w'))
        
# the decoys are now in the format that SOAP can process;
# use SOAP.decoys to build the decoyset
do=SOAP.decoys.decoyset(dsname=decoySetName, sourcedir=preparedDecoyPath)
do.build()
