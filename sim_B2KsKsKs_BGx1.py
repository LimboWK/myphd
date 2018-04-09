#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Descriptor: B0_3KS_3pi+pi-

#############################################################
# Steering file for official MC production of signal samples
# with beam backgrounds (BGx1).
#
# January 2017 - Belle II Collaboration
#############################################################

from basf2 import *
from simulation import add_simulation
from reconstruction import add_reconstruction, add_mdst_output
from L1trigger import add_tsim
from ROOT import Belle2
import glob

# decay file
decfile = Belle2.FileSystem.findFile('B2KsKsKs.dec')

# background (collision) files
bg = glob.glob('./BG/*.root')

#: number of events to generate, can be overriden with -n
num_events = 100 # subject to change 
#: output filename, can be overriden with -o
output_filename = "RootOutput_BGx1.root"

# create path
main = create_path()

# specify number of events to be generated
main.add_module("EventInfoSetter", expList=1, runList=1, evtNumList=num_events)

# generate BBbar events
evtgeninput = register_module('EvtGenInput')
evtgeninput.param('userDECFile', decfile)
main.add_module(evtgeninput)


bkgmixer = register_module('BeamBkgMixer')
bkgmixer.param('backgroundFiles', bg)
main.add_module(bkgmixer)

# detector simulation
add_simulation(main, bkgfiles=bg)

# remove the cache for background files to reduce memory
set_module_parameters(main, "BeamBkgMixer", cacheSize=0)

# trigger simulation
add_tsim(main)

# reconstruction
add_reconstruction(main)

# Finally add mdst output
add_mdst_output(main, filename=output_filename, additionalBranches=['TRGGDLResults', 'KlIds', 'KLMClustersToKlIds'])

# process events and print call statistics
process(main)
print(statistics)


