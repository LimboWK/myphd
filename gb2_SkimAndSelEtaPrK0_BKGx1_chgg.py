#!/usr/bin/env python

######################################################
#
# Get started with B0 -> eta'(eta (gamma gamma) pi+pi-) K0
#
# These are the channels that are going to be
# investigated:
#   B0->eta'(->eta(->gamma gamma)pi+pi-)K0S(pi+pi-)
#
# Author: Stefano Lacaprara  <lacaprara@pd.infn.it>  INFN Padova
# Modified by: A. Morda'  <morda@pd.infn.it> INFN Padova
#
#
#####################################################

import sys

from basf2 import *
from vertex import *
from modularAnalysis import *
from reconstruction import *
from stdFSParticles import *
from variables import variables
from stdCharged import *
from stdPhotons import *
from stdPi0s import *
from stdV0s import *
from stdLightMesons import *
from ROOT import Belle2
from glob import glob
from flavorTagger import *


set_log_level(LogLevel.ERROR)

do_fill_myPL = True #Default True
do_KS0_reco = False #Default False
do_chgd_pi_sel = True #Default True
do_vtx_fits = True #Default True


gb2_setuprel="release-00-09-01"


# BG0
#inputMdstList('default','mdst_000001_prod00000991_task00000001.root')
#inputMdstList('default','sub00/mdst_000007_prod00000990_task00000007.root')
inputMdstList('default','sub00/mdst_000013_prod00002522_task00000013_chgg_bg1_mc9.root')
# ch4 BG0 mdst_000004_prod00000997_task00000004.root
# ch1 BG1 mdst_000007_prod00000990_task00000007.root


prefix_fit = ''
if(do_vtx_fits):
    prefix_fit = '-vtx_fit'
else:
    prefix_fit = '-no_vtx_fit'

prefix_Kreco = ''
if(do_KS0_reco):
    prefix_Kreco = '-K0reco'
else:
    prefix_Kreco = '-no_K0reco'

prefix_chgpisel = ''
if(do_chgd_pi_sel):
     prefix_chgpisel = '-chpisel'
else:
    prefix_chgpisel = '-no_chpisel'

outFile = 'ntuple_chgg_out'+prefix_fit+prefix_Kreco+prefix_chgpisel+'_mc9_bg1.root'

if(do_fill_myPL):
# create lists of FSPs
    #loadStdGoodPhoton()
    stdPhotons("pi0")
    pions     = ('pi-:all',     '')
    fillParticleLists([pions])

if(do_chgd_pi_sel):
    cutAndCopyList('pi-:mine','pi-:all','piid > 0. and chiProb > 0.001')
else:
    cutAndCopyList('pi-:mine','pi-:all','')

# reconstruct eta->gg
reconstructDecay('eta:gg -> gamma:pi0 gamma:pi0', '0.400 < M < .700')
matchMCTruth('eta:gg')

# reconstruct eta'->gg2pi
reconstructDecay("eta' -> eta:gg pi+:mine pi-:mine", '0.5 < M < 1.3')
matchMCTruth("eta'")

# Ks ->pi+pi-
if(not do_KS0_reco):
    fillParticleList('K_S0:mdst','0.3 < M < 0.7')
else:
    reconstructDecay('K_S0:mdst -> pi+:mine pi-:mine', '0.3 < M < 0.7')

if(do_vtx_fits):
    vertexRave('K_S0:mdst', 0.0, "K_S0:mdst -> ^pi+:mine ^pi-:mine")

matchMCTruth('K_S0:mdst')

# channel eta'rg K+-
reconstructDecay("B0 -> eta' K_S0:mdst", 'Mbc > 5.0 and abs(deltaE) < 0.5')
if(do_vtx_fits):
    vertexRave('B0', 0.0, "B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] ^K_S0:mdst","iptube")

matchMCTruth('B0')

# get the rest of the event:
buildRestOfEvent('B0')

# get tag vertex ('breco' is the type of MC association)
TagV('B0', 'breco', confidenceLevel=1.E-3)

# get continuum suppression (needed for flavor tagging)
cleanMask = ('cleanMask', 'useCMSFrame(p)<=3.2', 'p >= 0.05 and useCMSFrame(p)<=3.2')
appendROEMasks('B0', [cleanMask])#, path=main)
buildContinuumSuppression('B0', 'cleanMask')#, path=main)


"""
use_central_database("GT_gen_prod_003.11_release-00-09-01-FEI-a")

# Flavour tagger
categories=[
        'Electron',
        'IntermediateElectron',
        'Muon',
        'IntermediateMuon',
        'KinLepton',
        'IntermediateKinLepton',
        'Kaon',
        'SlowPion',
        'FastPion',
        'Lambda',
        'FSC',
        'MaximumPstar',
        'KaonPion']
flavorTagger( particleLists=['B0'],
        weightFiles='B2JpsiKs_muBGx0')
"""

# create and fill flat Ntuple with MCTruth and kinematic information
toolsBsig = ['EventMetaData', '^B0']

#VARIABLES FOR SIGNAL SELECTION AND BACKGROUND REJECTION

#KINEMATICS
#in the lab frame
toolsBsig += ['InvMass', "B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] ^K_S0:mdst"]
toolsBsig += ['InvMass[BeforeFit]', "^B0 -> [^eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] K_S0:mdst"]
toolsBsig += ['Charge', "B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] K_S0:mdst"]
toolsBsig += ['Kinematics', "^B0 -> [^eta' -> [^eta:gg -> ^gamma:pi0 ^gamma:pi0] ^pi+:mine ^pi-:mine] ^K_S0:mdst"]
toolsBsig += ['DeltaEMbc', '^B0']
#in the cms

##im the Y(4S) RF
toolsBsig += ['CMSKinematics', "^B0 -> [^eta' -> [^eta:gg -> ^gamma:pi0 ^gamma:pi0] ^pi+:mine ^pi-:mine] ^K_S0:mdst"]

#TOPOLOGICAL

##fitted vertexes
toolsBsig += ['Vertex', "^B0 -> [^eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] ^K_S0:mdst"]


##wrt B0 decay vertex
###K_S0
toolsBsig += ['FlightInfo', "^B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] ^K_S0:mdst"]
toolsBsig += ['MomentumVectorDeviation', "^B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] ^K_S0:mdst"]
###eta'
toolsBsig += ['FlightInfo', "^B0 -> [^eta' -> [eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] K_S0:mdst"]
toolsBsig += ['MomentumVectorDeviation', "^B0 -> [^eta' -> [eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] K_S0:mdst"]
###eta
toolsBsig += ['FlightInfo', "^B0 -> [eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] K_S0:mdst"]
toolsBsig += ['MomentumVectorDeviation', "^B0 -> [eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] K_S0:mdst"]


#TRACK, CALO, & PID variables
toolsBsig += ['Cluster', "B0 -> [eta' -> [eta:gg -> ^gamma:pi0 ^gamma:pi0] pi+:mine pi-:mine] K_S0:mdst"]
toolsBsig += ['Track', "B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] K_S0:mdst"]
toolsBsig += ['TrackHits', "B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] K_S0:mdst"]
toolsBsig += ['PID', "B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] K_S0:mdst"]
toolsBsig += ['DeltaLogL', "B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] K_S0:mdst"]
toolsBsig += ['DetectorStatsSim',"B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] K_S0:mdst"]
toolsBsig += ['DetectorStatsRec',"B0 -> [eta' -> [eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] K_S0:mdst"]



#ACTUAL VARIABLES FOR THE CP ASYMMETRY MEASUREMENT
toolsBsig += ['DeltaT', '^B0']
toolsBsig += ['TagVertex', '^B0']

#Variables for Continuum suppression
toolsBsig += ['ContinuumSuppression', '^B0']
toolsBsig += ['CustomFloats[isSignal]', "^B0 -> [^eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] ^K_S0:mdst"]
toolsBsig += ['CustomFloats[isContinuumEvent]', "^B0"]

#Variables for Rest Of Event
toolsBsig += ['ROEMultiplicities', "^B0"]

####### MC INFO
toolsBsig += ['MCTruth', "^B0 -> [^eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] ^K_S0:mdst"]
toolsBsig += ['MCHierarchy', "^B0 -> [^eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] pi+:mine pi-:mine] ^K_S0:mdst"]
toolsBsig += ['MCVertex', "^B0 -> [^eta' -> [^eta:gg -> gamma:pi0 gamma:pi0] ^pi+:mine ^pi-:mine] ^K_S0:mdst"]
toolsBsig += ['MCTagVertex', '^B0']
toolsBsig += ['MCDeltaT', '^B0']

toolsBsig += ['FlavorTagging[TMVA-FBDT, FANN-MLP, qrCategories]', '^B0']

# save stuff to root file
ntupleFile(outFile)
ntupleTree('B0', 'B0', toolsBsig)

toolsMine = ['EventMetaData']
#ntupleTree('All', '', toolsAll)

# print out some further info
summaryOfLists(['eta:gg',"eta'",'B0'])

# Process the events
process(analysis_main)

# print out the summary
print(statistics)

