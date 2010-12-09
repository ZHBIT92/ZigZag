#!/usr/bin/env python

from TrackUtils import *
from TrackFileUtils import *
import numpy
import Analyzers
from la import larry        # Labeled arrays
import bootstrap as btstrp
from ParamUtils import ExpandTrackRuns

def DisplaySkillScores(skillScores, skillScoreName) :
    """
    Display the skill score results in a neat manner.

    Note, this function messes around with the formatting options
    of printing numpy arrays.  It does restore the settings back to
    the numpy defaults, but if you had your own formatting specified
    before calling this function, you will need to reset it.
    """

    numpy.set_string_function(lambda x: '\n'.join(['  '.join(["% 11.8f" % val for val in row])
                                                                              for row in x]),
                              repr=True)

    # Print the last eleven characters of each trackrun name for
    # the column labels.
    print '  '.join(["%11.11s" % tracker[-11:] for tracker in skillScores.label[-1]])

    print repr(skillScores.x)

    print "-" * (11*skillScores.shape[1] + 2*(skillScores.shape[1] - 1))
    numpy.set_string_function(lambda x: '  '.join(["% 11.8f" % val for val in x]),
                              repr=True)
    bootmean = btstrp.bootstrap(25, numpy.mean, skillScores.x, axis=0)
    btmean = bootmean.mean(axis=0)
    bootci = btstrp.bootci(25, numpy.mean, skillScores.x, alpha=0.05, axis=0)
#    print repr(skillScores.mean(axis=0).x)
    print repr((bootci[0] - btmean))
    print repr(btmean)
    print repr((bootci[1] - btmean))

    # Resetting back to how it was
    numpy.set_string_function(None, repr=True)


def AnalyzeTrackings(simName, simParams, skillNames,
                     trackRuns=None, path='.') :

    if trackRuns is None :
        # If the user does not specify any trackruns
        # to analyze, then just do all of them.
        trackRuns = simParams['trackers']

    # We only want to process the trackers as specified by the user
    # This change in simParams should *not* get saved!
    simParams['trackers'] = ExpandTrackRuns(simParams['trackers'], trackRuns)

    dirName = path + os.sep + simName
    (true_tracks, true_falarms) = FilterMHTTracks(*ReadTracks(dirName + os.sep + simParams['noisyTrackFile']))
    true_AssocSegs = CreateSegments(true_tracks)
    true_FAlarmSegs = CreateSegments(true_falarms)

    # Initializing the analysis data, which will hold a table of analysis results for
    # this simulation
    analysis = numpy.empty((len(skillNames),
                            len(simParams['trackers'])))
    labels = [skillNames, simParams['trackers']]
    

    for trackerIndex, tracker in enumerate(simParams['trackers']) :
        (finalTracks, finalFAlarms) = FilterMHTTracks(*ReadTracks(dirName + os.sep + simParams['result_file'] + '_' + tracker))
        trackerAssocSegs = CreateSegments(finalTracks)
        trackerFAlarmSegs = CreateSegments(finalFAlarms)

        truthTable = CompareSegments(true_AssocSegs, true_FAlarmSegs,
                                     trackerAssocSegs, trackerFAlarmSegs)

        for skillIndex, skill in enumerate(skillNames) :
            analysis[skillIndex, trackerIndex] = Analyzers.skillcalcs[skill](tracks=finalTracks, falarms=finalFAlarms,
                                                                  truthTable=truthTable)

    return larry(analysis, labels)

def DisplayAnalysis(analysis, skillName, doFindBest=True, doFindWorst=True, compareTo=None) :
    DisplaySkillScores(analysis, skillName)

    if doFindBest or doFindWorst :
        if compareTo is None :
            compareTo = analysis.label[1][0]

        # We separate the skillscores for just the one tracker and
        # the rest of the trackers.  We use keep_label because it
        # doesn't squeeze the results down to a scalar float.
        skillscores = analysis.keep_label('==', compareTo, axis=1)
        theOthers = analysis.keep_label('!=', compareTo, axis=1)

        # Do a numpy-style subtraction (for broadcasting reasons)
        scoreDiffs = skillscores.x - theOthers.x
        # Sort score differences for each tracker 
        indices = numpy.argsort(scoreDiffs, axis=0)

        print "\n Against: ", '  '.join(["%7s" % tracker for tracker in theOthers.label[1]])
        if doFindBest :
            print "Best Run: ", '  '.join(["%7d" % index for index in indices[-1]])

        if doFindWorst :
            print "Worst Run:", '  '.join(["%7d" % index for index in indices[0]])
    

if __name__ == '__main__' :
    import argparse
    import os                   # for os.sep
    import ParamUtils


    parser = argparse.ArgumentParser(description="Analyze the tracking results of a storm-track simulation")
    parser.add_argument("simName", type=str,
                      help="Analyze tracks for SIMNAME",
                      metavar="SIMNAME", default="NewSim")
    parser.add_argument("skillNames", nargs="+",
                        help="The skill measures to use (e.g., HSS)",
                        metavar="SKILL")
    parser.add_argument("-t", "--trackruns", dest="trackRuns",
                        nargs="*", help="Trackruns to analyze.  Analyze all runs if none are given",
                        metavar="RUN", default=None)
    parser.add_argument("-d", "--dir", dest="directory",
                        help="Base directory to find SIMNAME",
                        metavar="DIRNAME", default='.')

    args = parser.parse_args()

    #skillNames = ['HSS', 'TSS', 'Dur']

    dirName = args.directory + os.sep + args.simName
    simParams = ParamUtils.ReadSimulationParams(dirName + os.sep + "simParams.conf")



    analysis = AnalyzeTrackings(args.simName, simParams, args.skillNames,
                                trackRuns=args.trackRuns, path=args.directory)
    analysis = analysis.insertaxis(axis=1, label=args.simName)
    for skill in args.skillNames :
        DisplaySkillScores(analysis.lix[[skill]], skill)
        print '\n\n'

