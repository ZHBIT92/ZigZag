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
               procParams,
               currGen,
               trackCnt, prob_track_ends, maxTrackLen,
               tLims, cornerID=0, simState=None) :
    theTracks = []
    theFAlarms = []

    noisesToApply = procParams.pop('noises', [])
    trackCnt = int(procParams.pop('cnt', trackCnt))
    prob_track_ends = float(procParams.pop('prob_track_ends', prob_track_ends))
    maxTrackLen = int(procParams.pop('maxTrackLen', maxTrackLen))

    if simState is None :
        simState = {'theTracks': [],
                    'theFAlarms': [],
                    'theTrackLens': []}

    tracks, falarms, cornerID = currGen(cornerID, trackCnt, simState, prob_track_ends, maxTrackLen)
    TrackUtils.CleanupTracks(tracks, falarms)
    trackLens = [len(aTrack) for aTrack in tracks]



    theTracks.extend(tracks)
    theFAlarms.extend(falarms)

    currState = {'theTracks': simState['theTracks'] + tracks,
                 'theFAlarms': simState['theFAlarms'] + falarms,
                 'theTrackLens': simState['theTrackLens'] + trackLens}
    
    # Loop over various track generators
    for aGen in procParams :
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

        theTracks.extend(subTracks)
        theFAlarms.extend(subFAlarms)

    # Noisify the generated tracks.
    for aNoise in noisesToApply :
        noiseModels[aNoise](theTracks, theFAlarms, tLims)
        TrackUtils.CleanupTracks(theTracks, theFAlarms)

    return theTracks, theFAlarms, cornerID


###################################################################################################

def MakeModels(modParams, modelList) :
    models = {}
    defType = modParams.pop("type", None)

    for modname in modParams :
        typename = modParams[modname].pop('type', defType)
        models[modname] = modelList[typename][0](**modParams[modname])

    return models

def MakeGenModels(modParams, initModels, motionModels, gen_modelList, trackMakers) :
    models = {}
    defMotion = modParams.pop("motion", None)
    defInit = modParams.pop("init", None)
    defType = modParams.pop("type", None)
    defMaker = modParams.pop("trackmaker", None)

    for modname in modParams :
        params = modParams[modname]
        genType = gen_modelList[params.pop('type', defType)][0]
        models[modname] = genType(initModels[params.pop('init', defInit)],
                                  motionModels[params.pop('motion', defMotion)],
                                  trackMakers[params.pop('trackmaker', defMaker)],
                                  **params)

    return models

#############################
#   Track Simulator
#############################
def TrackSim(initParams, motionParams,
             genParams, noiseParams, tracksimParams,
             tLims, xLims, yLims,
             totalTracks, endTrackProb,
             simName,
             **simParams) :
    """
    totalTracks acts as the top-most default value to use for the sim generators.
    prob_track_ends also acts as the top-most default value.
    The difference between the elements of tLims also acts as the top-most
        default value for the maxTrackLen parameter.
    """
    initModels = MakeModels(initParams, Sim.init_modelList)
    motionModels = MakeModels(motionParams, Sim.motion_modelList)
    noiseModels = MakeModels(noiseParams, Sim.noise_modelList)

    simGens = MakeGenModels(genParams, initModels, motionModels,
                            Sim.gen_modelList, trackMakers)

    rootGenerator = Sim.NullGenerator()
    trackCnt = int(tracksimParams['Processing'].pop("cnt", totalTracks))
    endTrackProb = float(tracksimParams['Processing'].pop("prob_track_ends", endTrackProb))
    maxTrackLen = int(tracksimParams['Processing'].pop("maxTrackLen", max(tLims) - min(tLims)))


    true_tracks, true_falarms, cornerID = MakeTracks(simGens, noiseModels,
                                                     tracksimParams['Processing'],
                                                     rootGenerator,
					                                 trackCnt, endTrackProb, maxTrackLen,
                                                     tLims)

    # Clip tracks to the domain
    clippedTracks, clippedFAlarms = TrackUtils.ClipTracks(true_tracks,
                                                          true_falarms,
                                                          xLims, yLims, tLims)


    volume_data = TrackUtils.CreateVolData(true_tracks, true_falarms,
                                           tLims, xLims, yLims)


    noise_volData = TrackUtils.CreateVolData(clippedTracks, clippedFAlarms,
                                             tLims, xLims, yLims)

    return {'true_tracks': true_tracks, 'true_falarms': true_falarms,
            'noisy_tracks': clippedTracks, 'noisy_falarms': clippedFAlarms,
            'true_volumes': volume_data, 'noisy_volumes': noise_volData}

def SingleSimulation(simParams, initParams, motionParams,
                              genParams, noiseParams, tracksimParams) :
    # Seed the PRNG
    numpy.random.seed(simParams['seed'])

    # Create the simulation directory.
    if (not os.path.exists(simParams['simName'])) :
        os.makedirs(simParams['simName'])

    theSimulation = TrackSim(initParams, motionParams,
                             genParams, noiseParams, tracksimParams, **simParams)


    ParamUtils.SaveSimulationParams(simParams['simName'] + os.sep + "simParams.conf", simParams)
    SaveTracks(simParams['simTrackFile'], theSimulation['true_tracks'], theSimulation['true_falarms'])
    SaveTracks(simParams['noisyTrackFile'], theSimulation['noisy_tracks'], theSimulation['noisy_falarms'])
    SaveCorners(simParams['inputDataFile'], simParams['corner_file'], theSimulation['noisy_volumes'])



		    
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

    SingleSimulation(simParams, simConfs['InitModels'], simConfs['MotionModels'],
                                simConfs['TrackGens'], simConfs['NoiseModels'],
                                simConfs['SimModels'])


