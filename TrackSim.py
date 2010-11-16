#!/usr/bin/env python


import TrackUtils			# for ClipTracks(), CreateVolData(), CleanupTracks(), track_dtype
import numpy				# for Numpy
import os				# for os.sep, os.makedirs(), os.path.exists()

import Sim
import ParamUtils 			        # for SaveSimulationParams(), SetupParser()
from TrackFileUtils import *		# for writing the track data


#####################################################################################
#  Track Maker Functions
trackMakers = {}

def MakeTrack(cornerID, initModel, motionModel, probTrackEnds, maxLen) :
    aPoint = Sim.TrackPoint(cornerID, probTrackEnds, initModel, motionModel, maxLen)
    return numpy.fromiter(aPoint, TrackUtils.track_dtype)

trackMakers['MakeTrack'] = MakeTrack
###################################################################################


def MakeTracks(trackGens, noiseModels,
               procParams, currGen,
               trackCnt, prob_track_ends, maxTrackLen,
               tLims, cornerID=0, simState=None) :
    theTracks = []
    theFAlarms = []

    noisesToApply = procParams.get('noises', [])
    trackCnt = int(procParams.get('cnt', trackCnt))
    prob_track_ends = float(procParams.get('prob_track_ends', prob_track_ends))
    maxTrackLen = int(procParams.get('maxTrackLen', maxTrackLen))

    if simState is None :
        simState = {'theTracks': [],
                    'theFAlarms': [],
                    'theTrackLens': []}

    # Generate this model's set of tracks
    tracks, falarms, cornerID = currGen(cornerID, trackCnt, simState, prob_track_ends, maxTrackLen)
    TrackUtils.CleanupTracks(tracks, falarms)
    trackLens = [len(aTrack) for aTrack in tracks]

    # Add them to this node's set of tracks
    theTracks.extend(tracks)
    theFAlarms.extend(falarms)

    # Add them to this branch's set tracks
    # currState collects the tracks in a way that
    # any subnodes are aware of those tracks.
    # This "memory" does not carry across parallel branches.
    currState = {'theTracks': simState['theTracks'] + tracks,
                 'theFAlarms': simState['theFAlarms'] + falarms,
                 'theTrackLens': simState['theTrackLens'] + trackLens}
    
    # Loop over the node's sub-branch generators
    for aGen in procParams.sections :
        # Recursively perform track simulations using this loop's simulation
        #   This is typically done to restrict splits/merges on only the
        #   storm tracks and allow for clutter tracks to be made without
        #   any splitting/merging done upon them.
        # This will also allow for noise models to be applied to specific
        #   subsets of the tracks.
        subTracks, subFAlarms, cornerID = MakeTracks(trackGens, noiseModels,
                                                     procParams[aGen],
                                                     trackGens[aGen],
                                                     trackCnt, prob_track_ends, maxTrackLen,
                                                     tLims, cornerID, currState)

        # Add this branch's tracks to this node's set of tracks
        theTracks.extend(subTracks)
        theFAlarms.extend(subFAlarms)


    # Noisify the all the tracks of this node
    for aNoise in noisesToApply :
        noiseModels[aNoise](theTracks, theFAlarms, tLims)
        TrackUtils.CleanupTracks(theTracks, theFAlarms)

    return theTracks, theFAlarms, cornerID


###################################################################################################

def MakeModels(modParams, modelList) :
    models = {}
    defType = modParams.get("type", None)

    for modname in modParams.sections :
        # We need to pop off the 'type' so that it won't be
        # sent to the constructor of the model.
        typename = modParams[modname].pop('type', defType)
        models[modname] = modelList[typename][0](**modParams[modname])
        # Restore the value after creating the model
        modParams[modname]['type'] = typename

    return models

def MakeGenModels(modParams, initModels, motionModels, gen_modelList, trackMakers) :
    models = {}
    defMotion = modParams.get("motion", None)
    defInit = modParams.get("init", None)
    defType = modParams.get("type", None)
    defMaker = modParams.get("trackmaker", None)

    for modname in modParams.sections :
        params = modParams[modname]
        # We need to pop off these off so that it won't be
        # sent to the constructor of the model.
        typename = params.pop('type', defType)
        initName = params.pop('init', defInit)
        motName = params.pop('motion', defMotion)
        makeName = params.pop('trackmaker', defMaker)

        genType = gen_modelList[typename][0]

        models[modname] = genType(initModels[initName],
                                  motionModels[motName],
                                  trackMakers[makeName],
                                  **params)

        # Restore those values after creating the model
        params['type'] = typename
        params['init'] = initName
        params['motion'] = motName
        params['trackmaker'] = makeName

    return models

#############################
#   Track Simulator
#############################
def TrackSim(simConfs,
             tLims, totalTracks, endTrackProb,
             **simParams) :
    """
    totalTracks acts as the top-most default value to use for the sim generators.
    prob_track_ends also acts as the top-most default value.
    The difference between the elements of tLims also acts as the top-most
        default value for the maxTrackLen parameter.
    """
    initModels = MakeModels(simConfs['InitModels'], Sim.init_modelList)
    motionModels = MakeModels(simConfs['MotionModels'], Sim.motion_modelList)
    noiseModels = MakeModels(simConfs['NoiseModels'], Sim.noise_modelList)

    simGens = MakeGenModels(simConfs['TrackGens'], initModels, motionModels,
                            Sim.gen_modelList, trackMakers)

    rootGenerator = Sim.NullGenerator()
    rootNode = simConfs['SimModels']['Processing']

    # These are global defaults
    trackCnt = int(rootNode.get("cnt", totalTracks))
    endTrackProb = float(rootNode.get("prob_track_ends", endTrackProb))
    maxTrackLen = int(rootNode.get("maxTrackLen", max(tLims) - min(tLims)))


    true_tracks, true_falarms, cornerID = MakeTracks(simGens, noiseModels,
                                                     rootNode, rootGenerator,
					                                 trackCnt, endTrackProb, maxTrackLen,
                                                     tLims)

    return true_tracks, true_falarms

def SingleSimulation(simConfs,
                     xLims, yLims, tLims,
                     seed, **simParams) :
    frames = numpy.arange(simParams['frameCnt']) + 1
    # Seed the PRNG
    numpy.random.seed(seed)

    true_tracks, true_falarms = TrackSim(simConfs, tLims=tLims, **simParams)

    # Clip tracks to the domain
    clippedTracks, clippedFAlarms = TrackUtils.ClipTracks(true_tracks,
                                                          true_falarms,
                                                          xLims, yLims,
                                                          frameLims=(1, simParams['frameCnt']))

    
    volume_data = TrackUtils.CreateVolData(true_tracks, true_falarms,
                                           frames, tLims, xLims, yLims)


    noise_volData = TrackUtils.CreateVolData(clippedTracks, clippedFAlarms,
                                             frames, tLims, xLims, yLims)

    return {'true_tracks': true_tracks, 'true_falarms': true_falarms,
            'noisy_tracks': clippedTracks, 'noisy_falarms': clippedFAlarms,
            'true_volumes': volume_data, 'noisy_volumes': noise_volData}



def SaveSimulation(theSimulation, simParams, simConfs,
                   automake=True, autoreplace=True, path='.') :

    simDir = path + os.sep + simParams['simName'] + os.sep
    # Create the simulation directory.
    if (not os.path.exists(simDir)) :
        if automake :
            os.makedirs(simDir)
        else :
            raise ValueError("%s does not exist and automake==False in SaveSimulation()" % simDir)
    else :
        if not autoreplace :
            raise ValueError("%s already exists and autoreplace==False in SaveSimulation()" % simDir)
    
    ParamUtils.SaveSimulationParams(simDir + "simParams.conf", simParams)
    SaveTracks(simDir + simParams['simTrackFile'], theSimulation['true_tracks'], theSimulation['true_falarms'])
    SaveTracks(simDir + simParams['noisyTrackFile'], theSimulation['noisy_tracks'], theSimulation['noisy_falarms'])
    SaveCorners(simDir + simParams['inputDataFile'], simDir + simParams['corner_file'], theSimulation['noisy_volumes'])
    ParamUtils.SaveConfigFile(simDir + simParams['simConfFile'], simConfs)



		    
if __name__ == '__main__' :

    import argparse	                    # Command-line parsing

    parser = argparse.ArgumentParser(description="Produce a track simulation")
    parser.add_argument("simName",
		      help="Generate Tracks for SIMNAME", 
		      metavar="SIMNAME", default="NewSim")
    ParamUtils.SetupParser(parser)

    args = parser.parse_args()


    simParams = ParamUtils.ParamsFromOptions(args)

    simConfFiles = ["InitModels.conf", "MotionModels.conf",
                    "GenModels.conf", "NoiseModels.conf",
                    "SimModels.conf"]

    simConfs = ParamUtils.LoadSimulatorConf(simConfFiles)

    print "Sim Name:", args.simName
    print "The Seed:", simParams['seed']

    theSimulation = SingleSimulation(simConfs, **simParams)

    SaveSimulation(theSimulation, simParams, simConfs)

