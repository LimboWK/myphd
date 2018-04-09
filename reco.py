#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################
#
# Stuck? Ask for help at questions.belle2.org
#
# This tutorial demonstrates how to load generated final
# state particles (MCParticle objects) as Particles and
# create ParticleLists for each final state particle
# type: gamma/e/mu/pi/K/proton/K_L.
#
# All analysis modules and tools (e.g. making combinations, ...)
# have interfaces for ParticleLists so this step is
# neccessary if analysis tools are to be used.
#
# Contributors: A. Zupanc (June 2014)
#
######################################################

from basf2 import *
from modularAnalysis import analysis_main
from modularAnalysis import *
from modularAnalysis import inputMdst 
from stdCharged import *
from stdPi0s import *
from stdV0s import *
from vertex import *
import os.path
import sys
if not os.path.isfile('RootOutput_BGx0.root'):
    sys.exit('Required input file (RootOutput.root) does not exist. '
             )

# load input ROOT file
inputMdst('default', 'RootOutput_BGx0.root')

# print contents of the DataStore before loading MCParticles


# create and fill gamma/e/mu/pi/K/p ParticleLists
# second argument are the selection criteria: '' means no cut, take all
#stdPhotons() enable this when we have to look at the pi0s->2gamma
stdPi('all')
stdLoosePi()
stdPi0s()
#stdKshorts()


"""
#standard libs from scripts examples
pi0 = ('pi0:gen', '')
pions = ('pi+:gen','') #pi-:gen will be created as well 
Kshort = ('K_S0:gen', '')
photons = ('gamma:gen','')
fillParticleListsFromMC([photons, pions, pi0])
"""

#reconstruction of the decay B0->KsKsKs
# frist Ks reconstruction 
cutAndCopyList('pi-:mine','pi-:all','piid > 0. and chiProb > 0.001')
reconstructDecay('K_S0:cha1 -> pi+:mine pi-:mine','0.45 < M < 0.55',1) #same as stdKs
vertexRave('K_S0:cha1', 0.0, "K_S0:cha1 -> ^pi+:mine ^pi-:mine")

matchMCTruth('K_S0:cha1')
#reconstructDecay('K_S0:chi2 -> pi0 pi0','',2) enable it when considering pi0 channel
#then B0

reconstructDecay('B0:3Ks -> K_S0:cha1 K_S0:cha1 K_S0:cha1','Mbc > 5.0 and abs(deltaE) < 0.5')
vertexRave('B0:3Ks', 0.0, "B0 -> ^K_S0:cha1 ^K_S0:cha1 ^K_S0:cha1","iptube")
buildRestOfEvent('B0:3Ks')

#MCmatching for B0:3Ks
matchMCTruth('B0:3Ks')

#tagV
TagV('B0:3Ks','breco')

#offline data creation 
toolsB = ['EventMetaData', '^B0']
toolsB += ['InvMass', '^B0 -> ^K_S0 ^K_S0 ^K_S0']
toolsB += ['CMSKinematics', '^B0 -> ^K_S0 ^K_S0 ^K_S0']
toolsB += ['PID', 'B0 -> [K_S0 -> ^pi+ ^pi-] [K_S0 -> ^pi+ ^pi-] [K_S0 -> ^pi+ ^pi-]']
toolsB += ['Track', 'B0 -> [K_S0 -> ^pi+ ^pi-] [K_S0 -> ^pi+ ^pi-] [K_S0 -> ^pi+ ^pi-]']
toolsB += ['MCTruth', '^B0']
toolsB += ['TagVertex','^B0']
toolsB += ['MCTagVertex', '^B0']
toolsB += ['DeltaT','^B0']
toolsB += ['MCDeltaT','^B0']

toolsB += ['Vertex','^B0 -> ^K_S0 ^K_S0 ^K_S0']
toolsB += ['CustomFloats[isSignal]', '^B0 -> ^K_S0 ^K_S0 ^K_S0']

# write out the flat ntuple
ntupleFile('B2KsKsKs_Reconstruction.root')
ntupleTree('tree', 'B0:3Ks', toolsB)
# print contents of the DataStore after loading MCParticles
printDataStore()
# the difference

# print contents of the DataStore after loading MCParticles
# the difference is that DataStore now contains StoreArray<Particle>
# filled with Particles created from generated final state particles


# print out the contents of each ParticleList

# print out the summary
analysis_main.add_module('PrintCollections')
#analysis_main.add_module('Interactive')
process(analysis_main)
print(statistics)

