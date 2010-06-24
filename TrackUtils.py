import math
import numpy
import numpy.lib.recfunctions as nprf		# for .stack_arrays(), .append_fields()

corner_dtype = [('xLocs', 'f4'), ('yLocs', 'f4')]
track_dtype = corner_dtype + [('frameNums', 'i4'), ('types', 'a1')]
volume_dtype = track_dtype + [('trackID', 'i4')]
#storm_dtype = track_dtype + [('types', 'a1'), ('frameNums', 'i4'), ('trackID', 'i4')]

def CreateVolData(tracks, falarms, tLims, xLims, yLims) :
    """
    Essentially, go from lagrangian (following a particle)
    to eulerian (at fixed points on a grid).

    Note that this method will retain the 'trackID' number,
    so it is possible to reconstruct the (clipped) track data using
    this output.
    """
    volData = []
    tmpTracks = [nprf.append_fields(aTrack, 'trackID',
                                    [trackIndex] * len(aTrack),
                                    usemask=False)
                      for trackIndex, aTrack in enumerate(tracks)]

    tmpFalarms = [nprf.append_fields(aTrack, 'trackID',
                                     [-trackIndex - 1] * len(aTrack),
                                     usemask=False)
                      for trackIndex, aTrack in enumerate(falarms)]

    allCells = numpy.hstack(tmpTracks + tmpFalarms)

    # Note, this is a mask in the opposite sense from a numpy masked array.
    #       True means that this is a value to keep.
    domainMask = numpy.logical_and(allCells['xLocs'] >= min(xLims),
                 numpy.logical_and(allCells['xLocs'] <= max(xLims),
                 numpy.logical_and(allCells['yLocs'] >= min(yLims),
                                   allCells['yLocs'] <= max(yLims))))

    for volTime in xrange(min(tLims), max(tLims) + 1) :
        # Again, this mask is opposite from numpy masked array.
        tMask = (allCells['frameNums'] == volTime)
        volData.append({'volTime': volTime,
                        'stormCells': allCells[numpy.logical_and(domainMask, tMask)]})

    return(volData)


def ClipTracks(tracks, falarms, xLims, yLims, tLims) :
    """
    Return a copy of the tracks and falarms, clipped to within
    the given domain.

    All tracks clipped to length of one are moved to a copy of falarms.
    """
    # Note, this is a mask in the opposite sense from a numpy masked array.
    #       Here, True means that this is a value to keep.
    clippedTracks = [ClipTrack(aTrack, xLims, yLims, tLims) for aTrack in tracks]
    clippedFAlarms = [ClipTrack(aTrack, xLims, yLims, tLims) for aTrack in falarms]

    CleanupTracks(clippedTracks, clippedFAlarms)
#    print "Length of tracks outside: ", len(clippedTracks)
    return clippedTracks, clippedFAlarms

def ClipTrack(track, xLims, yLims, tLims) :
    domainMask = numpy.logical_and(track['xLocs'] >= min(xLims),
                 numpy.logical_and(track['xLocs'] <= max(xLims),
                 numpy.logical_and(track['yLocs'] >= min(yLims),
                 numpy.logical_and(track['yLocs'] <= max(yLims),
                 numpy.logical_and(track['frameNums'] >= min(tLims),
                                   track['frameNums'] <= max(tLims))))))

    return track[domainMask]


def CleanupTracks(tracks, falarms) :
    """
    Moves tracks that were shortened to single length to the
    falarms list, and eliminate the empty tracks.
    """
#    cleanTracks = [aTrack.copy() for aTrack in tracks]
#    cleanFalarms = [aTrack.copy() for aTrack in falarms]
    cleanTracks = tracks
    cleanFalarms = tracks

    for trackIndex in range(len(cleanTracks))[::-1] :
        if len(cleanTracks[trackIndex]) == 1 :
            # Change the type to a False Alarm
            cleanTracks[trackIndex]['types'] = 'F'
            cleanFalarms.append(cleanTracks[trackIndex])
            cleanTracks[trackIndex] = []

        if len(cleanTracks[trackIndex]) == 0 :
            del cleanTracks[trackIndex]

    for trackIndex in range(len(cleanFalarms))[::-1] :
        if len(cleanFalarms[trackIndex]) == 0 :
            del cleanFalarms[trackIndex]

    return cleanTracks, cleanFalarms



# TODO: Still follows old data structure...
def CreateSegments(tracks) :
    """
    Breaks up a list of the tracks (or falarms) into an array of segments.
    Each element in the arrays represents the start and end point of a segment.
    """

    xLocs = []
    yLocs = []
    frameNums = []
    for aTrack in tracks :
        if len(aTrack) > 1 :
            for index2 in range(1, len(aTrack)) :
                index1 = index2 - 1
                xLocs.append([aTrack['xLocs'][index1], aTrack['xLocs'][index2]])
                yLocs.append([aTrack['yLocs'][index1], aTrack['yLocs'][index2]])
                frameNums.append([aTrack['frameNums'][index1], aTrack['frameNums'][index2]])
	else :
	    xLocs.append(aTrack['xLocs'])
	    yLocs.append(aTrack['yLocs'])
	    frameNums.append(aTrack['frameNums'])


    return {'xLocs': xLocs, 'yLocs': yLocs, 'frameNums': frameNums}


def PrintTruthTable(truthTable) :
    """
    Print out the truth table (a.k.a. - contingency table) for the line
    segments that was generated by CompareSegments().
    """
    print """
                                Reality
             |        True         |        False        ||
  Predicted  |                     |                     ||
 ============+=====================+=====================||
             | Correct Association |  Wrong Association  ||
    True     |        %5d        |        %5d        ||
             |                     |                     ||
 ------------+---------------------+---------------------+|
             |   Wrong Non-Assoc.  | Correct Non-Assoc.  ||
    False    |        %5d        |        %5d        ||
             |                     |                     ||
 ========================================================//
""" % (len(truthTable['assocs_Correct']['xLocs']), len(truthTable['assocs_Wrong']['xLocs']),
       len(truthTable['falarms_Wrong']['xLocs']), len(truthTable['falarms_Correct']['xLocs']))


def CompareSegments(realSegs, realFAlarmSegs, predSegs, predFAlarmSegs) :
    """
    This function will compare the line segments and false alarm points and
    categorize them based upon a truth table.  The truth table will determine
    if the proper point associations were made.

                                Reality
                 |      True       |      False      |
     Predicted   |                 |                 |
    -------------+-----------------+-----------------+
        True     |  assocs_Correct |  assocs_Wrong   |
    -------------+-----------------+-----------------+
       False     |  falarms_Wrong  | falarms_Correct |
    -------------+-----------------+-----------------+
    """
    assocs_Correct = {'xLocs': [], 'yLocs': [], 'frameNums': []}
    falarms_Correct = {'xLocs': [], 'yLocs': [], 'frameNums': []}
    assocs_Wrong = {'xLocs': [], 'yLocs': [], 'frameNums': []}
    falarms_Wrong = {'xLocs': [], 'yLocs': [], 'frameNums': []}


    unmatchedPredTrackSegs = range(len(predSegs['xLocs']))

    for (realSegXLoc, realSegYLoc, realSegFrameNum) in zip(realSegs['xLocs'], 
							   realSegs['yLocs'], 
							   realSegs['frameNums']) :
	foundMatch = False
	for predIndex in unmatchedPredTrackSegs :
	    if (is_eq(realSegXLoc[0], predSegs['xLocs'][predIndex][0]) and
	        is_eq(realSegXLoc[1], predSegs['xLocs'][predIndex][1]) and
	        is_eq(realSegYLoc[0], predSegs['yLocs'][predIndex][0]) and
	        is_eq(realSegYLoc[1], predSegs['yLocs'][predIndex][1]) and
	        realSegFrameNum[0] == predSegs['frameNums'][predIndex][0] and
	        realSegFrameNum[1] == predSegs['frameNums'][predIndex][1]) :


		assocs_Correct['xLocs'].append(predSegs['xLocs'][predIndex])
		assocs_Correct['yLocs'].append(predSegs['yLocs'][predIndex])
		assocs_Correct['frameNums'].append(predSegs['frameNums'][predIndex])
		# To make sure that I don't compare against that item again.
		del unmatchedPredTrackSegs[unmatchedPredTrackSegs.index(predIndex)]
		foundMatch = True
		# Break out of this loop...
		break

	# This segment represents those that were completely
        # missed by the tracking algorithm.
	if not foundMatch : 
	    falarms_Wrong['xLocs'].append(realSegXLoc)
	    falarms_Wrong['yLocs'].append(realSegYLoc)
	    falarms_Wrong['frameNums'].append(realSegFrameNum)

    # Anything left from the predicted segments must be unmatched with reality,
    # therefore, these segments belong in the "assocs_Wrong" array.
    for index in unmatchedPredTrackSegs :
        #print predSegs['xLocs'][index], predSegs['frameNums'][index]
        assocs_Wrong['xLocs'].append(predSegs['xLocs'][index])
        assocs_Wrong['yLocs'].append(predSegs['yLocs'][index])
        assocs_Wrong['frameNums'].append(predSegs['frameNums'][index])


    # Now for the falarms...
    """
    print "PredFAlarmSegs: "
    for predFAlarm in zip(predFAlarmSegs['xLocs'],
						  predFAlarmSegs['yLocs'],
						  predFAlarmSegs['frameNums']) :
	print predFAlarm
    """
    unmatchedPredFAlarms = range(len(predFAlarmSegs['xLocs']))
    for (realFAlarmXLoc, realFAlarmYLoc, realFAlarmFrameNum) in zip(realFAlarmSegs['xLocs'],
					                            realFAlarmSegs['yLocs'],
					                            realFAlarmSegs['frameNums']):
	foundMatch = False
	for predIndex in unmatchedPredFAlarms :
	    if (is_eq(realFAlarmXLoc[0], predFAlarmSegs['xLocs'][predIndex][0]) and
		is_eq(realFAlarmYLoc[0], predFAlarmSegs['yLocs'][predIndex][0]) and
		realFAlarmFrameNum[0] == predFAlarmSegs['frameNums'][predIndex][0]) :
		
		falarms_Correct['xLocs'].append(realFAlarmXLoc)
		falarms_Correct['yLocs'].append(realFAlarmYLoc)
		falarms_Correct['frameNums'].append(realFAlarmFrameNum)
		# To make sure that I don't compare against that item again.
		del unmatchedPredFAlarms[unmatchedPredFAlarms.index(predIndex)]
                #print "Deleting: ", predIndex
		foundMatch = True
		# Break out of this loop
		break

	# This FAlarm represents those that may have been falsely associated (assocs_Wrong)...
        # Well... technically, it just means that the tracking algorithm did not declare it
        #         as a false alarm.  Maybe it did not declare it as anything?
	# TODO: Not sure if there is anything I want to do about these for now...
	#       They might already have been accounted for earlier.
#        if not foundMatch :
#            print "<<<< Falsely Associated! ", realFAlarmXLoc, realFAlarmYLoc, realFAlarmFrameNum, " >>>>"

    # Anything left from the predicted non-associations are unmatched with reality.
    # therefore, these segments belong in the "falarms_Wrong" array.
    # NOTE: however, these might have already been accounted for...
#    for index in unmatchedPredFAlarms :
#	print "<<<< Falsely Non-Associated! ", index, predFAlarmSegs['xLocs'][index][0], predFAlarmSegs['yLocs'][index][0], predFAlarmSegs['frameNums'][index][0], " >>>>"
#    print "assocs_Wrong: ", assocs_Wrong
#    print "falarms_Wrong: ", falarms_Wrong
    return {'assocs_Correct': assocs_Correct, 'assocs_Wrong': assocs_Wrong,
	    'falarms_Wrong': falarms_Wrong, 'falarms_Correct': falarms_Correct}


def CalcHeidkeSkillScore(truthTable) :
    """
    Skill score formula from 
	http://www.eumetcal.org.uk/eumetcal/verification/www/english/msg/ver_categ_forec/uos3/uos3_ko1.htm

    HSS = 2(ad - bc) / [(a + c)(c + d) + (a + b)(b + d)]

    Note that a forecast is good when it is closer to 1, and
    is worse if less than zero.

                Observed
              True    False
Forecasted
    True       a        b
    False      c        d
    """

    a = float(len(truthTable['assocs_Correct']['xLocs']))
    b = float(len(truthTable['assocs_Wrong']['xLocs']))
    c = float(len(truthTable['falarms_Wrong']['xLocs']))
    d = float(len(truthTable['falarms_Correct']['xLocs']))
    if (((a + c) * (c + d)) + ((a + b) * (b + d))) < 0.1 :
       # Prevent division by zero...
       return 1.0
    else :
       return 2. * ((a * d) - (b * c)) / (((a + c) * (c + d)) + ((a + b) * (b + d)))


def CalcTrueSkillStatistic(truthTable) :
    """
    Skill score formula from 
	http://euromet.meteo.fr/resources/ukmeteocal/verification/www/english/msg/ver_categ_forec/uos3/uos3_ko2.htm

    TSS = (ad - bc) / [(a + c)(b + d)]

    Note that a forecast is good when it is closer to 1, and
    is worse if closer to -1.

                Observed
              True    False
Forecasted
    True       a        b
    False      c        d
    """

    a = float(len(truthTable['assocs_Correct']['xLocs']))
    b = float(len(truthTable['assocs_Wrong']['xLocs']))
    c = float(len(truthTable['falarms_Wrong']['xLocs']))
    d = float(len(truthTable['falarms_Correct']['xLocs']))
    if ((a + c) * (b + d)) < 0.1 :
        # Prevent division by zero...
        return 1.0
    else :
        return ((a * d) - (b * c)) / ((a + c) * (b + d))

def FilterMHTTracks(origTracks, origFalarms) :
    """
    This function will 'clean up' the track output from ReadTracks()
    such that the tracks contain only the actual detected points.
    Also, it will move any one-length tracks to falarms, and completely
    remove any zero-length tracks.
    """
    tracks = [aTrack.copy() for aTrack in origTracks]
    falarms = [aTrack.copy() for aTrack in origFalarms]

    for trackIndex, aTrack in enumerate(tracks) :
        tracks[trackIndex] = aTrack[aTrack['types'] == 'M']
		
    CleanupTracks(tracks, falarms)
    return tracks, falarms


def DomainFromTracks(tracks, falarms = []) :
    """
    Calculate the spatial and temporal domain of the tracks and false alarms.
    Note that this assumes that bad points are non-existant or has been
    masked out.
    """

    allPoints = numpy.hstack(tracks + falarms)
    
    return ((allPoints['xLocs'].min(), allPoints['xLocs'].max()),
            (allPoints['yLocs'].min(), allPoints['yLocs'].max()),
            (allPoints['frameNums'].min(), allPoints['frameNums'].max()))


def is_eq(val1, val2) :
    """
    Yeah, I know this isn't the smartest thing I have done, but
    most of my code only needs float type math, and it would be
    far to difficult to convert all of the models and such over
    to the "new" decimal type.
    Instead, I just worry about equality with respect to about
    6 decimal places, which is how I am dealing with it for now.

    TODO: Come up with a better way!
    """
#    return int(round(val1 * 1000., 1)) == int(round(val2 * 1000., 1))
    return math.fabs(val1 - val2) < 0.00000001
