#!/usr/bin/env python

from ZigZag.TrackPlot import PlotPlainTracks
from ZigZag.TrackFileUtils import ReadTracks
from ZigZag.TrackUtils import FilterMHTTracks, DomainFromTracks
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import AxesGrid

from BRadar.maputils import LatLonFrom
from mpl_toolkits.basemap import Basemap
from BRadar.maputils import PlotMapLayers, mapLayers

import numpy as np

def CoordinateTransform(tracks, cent_lon, cent_lat) :
    for track in tracks :
        # Purposely backwards to get bearing relative to 0 North
        azi = np.rad2deg(np.arctan2(track['xLocs'], track['yLocs']))
        dists = np.hypot(track['xLocs'], track['yLocs']) * 1000
        lats, lons = LatLonFrom(cent_lat, cent_lon, dists, azi)
        track['xLocs'] = lons
        track['yLocs'] = lats


def MakeTrackPlots(grid, trackData, titles, showMap,
                   endFrame=None, tail=None) :
    """
    *grid*              axes_grid object
    *trackData*         a list of the lists of tracks
    *titles*            titles for each subplot
    *showMap*           boolean indicating whether to plot a map layer
    *endFrame*          Display tracks as of *frame* number. Default: last
    *tail*              How many frames to include prior to *frame* to display
                        Default: all
    """
    stackedTracks = []
    for aTracker in trackData :
        stackedTracks += aTracker[0] + aTracker[1]

    # TODO: gotta make this get the time limits!
    (xLims, yLims, frameLims) = DomainFromTracks(stackedTracks)

    if endFrame is None :
        endFrame = frameLims[1]

    if tail is None :
        tail = frameLims[1] - frameLims[0]

    startFrame = endFrame - tail

    if showMap :
        bmap = Basemap(projection='cyl', resolution='i',
                       suppress_ticks=False,
                       llcrnrlat=yLims[0], llcrnrlon=xLims[0],
                       urcrnrlat=yLims[1], urcrnrlon=xLims[1])


    for ax, aTracker, title in zip(grid, trackData, titles) :
        if showMap :        
            PlotMapLayers(bmap, mapLayers, ax)
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
        else :
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

        PlotPlainTracks(aTracker[0], aTracker[1],
                        startFrame, endFrame, axis=ax)

        ax.set_title(title)


def main(args) :
    if len(args.trackFiles) == 0 : print "WARNING: No trackFiles given!"

    if args.trackTitles is None :
        args.trackTitles = args.trackFiles
    else :
        if len(args.trackTitles) != len(args.trackFiles) :
            raise ValueError("The number of TITLEs do not match the"
                             " number of TRACKFILEs.")

    if args.layout is None :
        args.layout = (1, len(args.trackFiles))

    if args.figsize is None :
        args.figsize = plt.figaspect(float(args.layout[0]) / args.layout[1])

    trackerData = [FilterMHTTracks(*ReadTracks(trackFile)) for
                   trackFile in args.trackFiles]

    if args.statLonLat is not None :
        for aTracker in trackerData :
            CoordinateTransform(aTracker[0] + aTracker[1],
                                args.statLonLat[0],
                                args.statLonLat[1])

    theFig = plt.figure(figsize=args.figsize)
    grid = AxesGrid(theFig, 111, nrows_ncols=args.layout, aspect=False,
                            share_all=True, axes_pad=0.45)
    
    showMap = (args.statLonLat is not None and args.displayMap)

    MakeTrackPlots(grid, trackerData, args.trackTitles, showMap,
                   endFrame=args.endFrame, tail=args.tail)

    if args.saveImgFile is not None :
        theFig.savefig(args.saveImgFile)

    if args.doShow :
        plt.show()


if __name__ == '__main__' :

    import argparse				# Command-line parsing

    from ZigZag.zigargs import AddCommandParser

    parser = argparse.ArgumentParser(description="Produce a plain display of"
                                                 " the tracks")
    AddCommandParser('ShowTracks2', parser)
    args = parser.parse_args()

    main(args)


