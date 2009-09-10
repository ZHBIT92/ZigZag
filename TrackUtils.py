
import copy                             # for deep copying


def CreateVolData(tracks, falarms, tLims, xLims, yLims) :
    """
    Essentially, go from lagrangian (following a particle)
    to eulerian (at fixed points on a grid).

    Note that this method will retain the 'trackID' number,
    so it is possible to reconstruct the (clipped) track data using
    this output.
    """
    volData = []
    allCells = {'frameNums': [], 'trackID': [], 'xLocs': [], 'yLocs': []}
    for (trackID, aTrack) in enumerate(tracks) :
	#print "THIS TRACK:   ", aTrack
        allCells['frameNums'].extend(aTrack['frameNums'])
        allCells['trackID'].extend([trackID] * len(aTrack['frameNums']))
        allCells['xLocs'].extend(aTrack['xLocs'])
        allCells['yLocs'].extend(aTrack['yLocs'])

    
    lastID = max(allCells['trackID'])
    lastID += 1
    for aFAlarm in falarms :
	#print "THIS FALARM: ", aFAlarm
	allCells['frameNums'].extend(aFAlarm['frameNums'])
	allCells['trackID'].extend([lastID] * len(aFAlarm['frameNums']))
	allCells['xLocs'].extend(aFAlarm['xLocs'])
	allCells['yLocs'].extend(aFAlarm['yLocs'])
	lastID += 1


    for volTime in range(min(tLims), max(tLims) + 1) :
        volData.append({'volTime': volTime,
                        'stormCells': [{'xLoc': xLoc, 'yLoc': yLoc, 'trackID': trackID}
                                       for (xLoc, yLoc, frameNum, trackID) in zip(allCells['xLocs'], allCells['yLocs'], allCells['frameNums'], allCells['trackID'])
                                        if (frameNum == volTime and xLoc >= min(xLims) and xLoc <= max(xLims) and
                                                                    yLoc >= min(yLims) and yLoc <= max(yLims))]})

    return(volData)


def ClipTracks(tracks, falarms, xLims, yLims, tLims) :
    """
    Return a copy of the tracks and falarms, clipped to within
    the given domain.

    All tracks clipped to length of one are moved to a copy of falarms.
    """
    clippedTracks = copy.deepcopy(tracks)
    clippedFAlarms = copy.deepcopy(falarms)
    for aTrack in clippedTracks :
        for (index, (xLoc, yLoc, frameNum)) in enumerate(zip(aTrack['xLocs'], aTrack['yLocs'], aTrack['frameNums'])) :
            if (xLoc < min(xLims) or xLoc > max(xLims) or
                yLoc < min(yLims) or yLoc > max(yLims) or
                frameNum < min(tLims) or frameNum > max(tLims)) :
                # Flag this track as one to get rid of.
                for aKey in aTrack : aTrack[aKey][index] = None



    (clippedTracks, clippedFAlarms) = CleanupTracks(clippedTracks, clippedFAlarms)
#    print "Length of tracks outside: ", len(clippedTracks)
    return (clippedTracks, clippedFAlarms)


def CleanupTracks(tracks, falarms) :
    """
    Rebuild the track list, effectively removing the storms flagged by a 'None'
    Also handles tracks that were shortened or effectively removed to the
    falarms list.
    """
    for trackID in range(len(tracks)) :
        for aKey in tracks[trackID] : tracks[trackID][aKey] = [someVal for someVal in tracks[trackID][aKey] if someVal is not None]
	
	if len(tracks[trackID]['frameNums']) == 1 :
	    falarms.append(tracks[trackID].copy())
	    for aKey in tracks[trackID] : tracks[trackID][aKey] = []
        
	if len(tracks[trackID]['frameNums']) == 0 :
	    # Flag for removal.
	    tracks[trackID] = None
        


    tracks = [aTrack for aTrack in tracks if aTrack is not None]
#    print "Length of tracks: ", len(tracks)
    return(tracks, falarms)




def CreateSegments(tracks, falarms) :
    """
    Breaks up a track into parallel arrays of locations in 2D space and time.
    Each element in the arrays represents the start and end point of the segment.

    Note that any track that is of length 1 will be considered a 'false alarm',
    and the falarms array will be updated accordingly.
    """

    xLocs = []
    yLocs = []
    frameNums = []
    for aTrack in tracks :
        if len(aTrack['frameNums']) > 1 :
            for index2 in range(1, len(aTrack['frameNums'])) :
                index1 = index2 - 1
                xLocs.append([aTrack['xLocs'][index1], aTrack['xLocs'][index2]])
                yLocs.append([aTrack['yLocs'][index1], aTrack['yLocs'][index2]])
                frameNums.append([aTrack['frameNums'][index1], aTrack['frameNums'][index2]])
	else :
	    falarms.append(aTrack)


    return {'xLocs': xLocs, 'yLocs': yLocs, 'frameNums': frameNums}



def CompareSegments(realSegments, realFAlarms, predSegments, predFAlarms) :
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

    unmatchedPredSegs = range(len(predSegments['xLocs']))

    for (realSegXLoc, realSegYLoc, realSegFrameNum) in zip(realSegments['xLocs'], realSegments['yLocs'], realSegments['frameNums']) :
	foundMatch = False
	for predIndex in unmatchedPredSegs :
	    if (is_eq(realSegXLoc[0], predSegments['xLocs'][predIndex][0]) and
	        is_eq(realSegXLoc[1], predSegments['xLocs'][predIndex][1]) and
	        is_eq(realSegYLoc[0], predSegments['yLocs'][predIndex][0]) and
	        is_eq(realSegYLoc[1], predSegments['yLocs'][predIndex][1]) and
	        realSegFrameNum[0] == predSegments['frameNums'][predIndex][0] and
	        realSegFrameNum[1] == predSegments['frameNums'][predIndex][1]) :


		assocs_Correct['xLocs'].append(predSegments['xLocs'][predIndex])
		assocs_Correct['yLocs'].append(predSegments['yLocs'][predIndex])
		assocs_Correct['frameNums'].append(predSegments['frameNums'][predIndex])
		# To make sure that I don't compare against that item again.
		del unmatchedPredSegs[unmatchedPredSegs.index(predIndex)]
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
    for index in unmatchedPredSegs :
        assocs_Wrong['xLocs'].append(predSegments['xLocs'][index])
        assocs_Wrong['yLocs'].append(predSegments['yLocs'][index])
        assocs_Wrong['frameNums'].append(predSegments['frameNums'][index])

    unmatchedPredFAlarms = range(len(predFAlarms))
    for realFAlarm in realFAlarms :
	foundMatch = False
	for predIndex in unmatchedPredFAlarms :
	    if (is_eq(realFAlarm['xLocs'][0], predFAlarms[predIndex]['xLocs'][0]) and
		is_eq(realFAlarm['yLocs'][0], predFAlarms[predIndex]['yLocs'][0]) and
		realFAlarm['frameNums'][0] == predFAlarms[predIndex]['frameNums'][0]) :
		
		falarms_Correct['xLocs'].append(realFAlarm['xLocs'])
		falarms_Correct['yLocs'].append(realFAlarm['yLocs'])
		falarms_Correct['frameNums'].append(realFAlarm['frameNums'])
		# To make sure that I don't compare against that item again.
		del unmatchedPredFAlarms[unmatchedPredFAlarms.index(predIndex)]
		foundMatch = True
		# Break out of this loop
		break

	# This FAlarm represents those that may have been falsely associated...
	# Not sure if there is anything I want to do about these for now...

    return {'assocs_Correct': assocs_Correct, 'assocs_Wrong': assocs_Wrong,
	    'falarms_Correct': falarms_Correct, 'falarms_Wrong': falarms_Wrong}




def FilterMHTTracks(raw_tracks, raw_falarms) :
    """
    This function is meant to deal with the special
    entries in the track file produced by the MHT algorithm.
    These track elements are for when the track is "coasting"
    for a frame.

    These track elements are removed for our purposes.
    """
    tracks = copy.deepcopy(raw_tracks['tracks'])
    falarms = copy.deepcopy(raw_falarms)
    
    for aTrack in tracks :
        for index in range(len(aTrack['types'])) :
	    if type == 'M' :
		# Flag this element of the track as one to get rid of.
                for aKey in aTrack : aTrack[aKey][index] = None
		
    (tracks, falarms) = CleanupTracks(tracks, falarms)
    return(tracks, falarms)


def DomainFromTracks(tracks) :

    minTrackX = []
    maxTrackX = []
    minTrackY = []
    maxTrackY = []
    minTrackT = []
    maxTrackT = []

    for track in tracks :
        minTrackX.append(min(track['xLocs']))
        maxTrackX.append(max(track['xLocs']))
        minTrackY.append(min(track['yLocs']))
        maxTrackY.append(max(track['yLocs']))
        minTrackT.append(min(track['frameNums']))
        maxTrackT.append(max(track['frameNums']))


    return( [min(minTrackX), max(maxTrackX)],
            [min(minTrackY), max(maxTrackY)],
            [min(minTrackT), max(maxTrackT)] )


def is_eq(val1, val2) :
    """
    Yeah, I know this isn't the smartest thing I have done, but
    most of my code only needs float type math, and it would be
    far to difficult to convert all of the models and such over
    to the "new" decimal type.
    Instead, I just worry about equality with respect to about
    3 decimal places, which is how I am dealing with it for now.

    TODO: Come up with a better way!
    """
    return int(round(val1 * 100, 0)) == int(round(val2 * 100, 0))
