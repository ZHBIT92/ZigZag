
_zigargs = {}

def AddCommandParser(command, parser) :
    if command not in _zigargs :
        raise ValueError("The command '%s' is not registered." % command)

    for args, kwargs in _zigargs[command] :
        parser.add_argument(*args, **kwargs)


_zigargs['TrackSim'] = [
    (("simName",), 
     dict(help="Generate Tracks for SIMNAME",
          metavar="SIMNAME", default="NewSim")),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to place SIMNAME",
          metavar="DIRNAME", default='.')),
    (("-c", "--conf"), 
     dict(dest="simConfFiles",
          nargs='+',
          help="Configuration files for the simulation.",
          metavar="CONFFILE", default=None))
    ]

_zigargs['MultiSim'] = [
    (("multiSim",), 
     dict(type=str,
          help="Generate Tracks for MULTISIM",
          metavar="MULTISIM", default="NewMulti")),
    (("simCnt",), 
     dict(type=int,
          help="Repeat Simulation N times.",
          metavar="N", default=1)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to place MULTISIM",
          metavar="DIRNAME", default='.')),
    (("-c", "--conf"), 
     dict(dest="simConfFiles",
          nargs='+',
          help="Configuration files for the simulation.",
          metavar="CONFFILE", default=None))
    ]

_zigargs['DownsampleSim'] = [
    (("simName",), 
     dict(help="Downsample the tracks of SIMNAME",
          metavar="SIMNAME")),
    (("newName",), 
     dict(help="Name of the new simulation",
          metavar="NEWNAME")),
    (("skipCnt",), 
     dict(type=int,
          help="Skip CNT frames for downsampling",
          metavar="CNT")),
    (("--volume",),
     dict(dest="doTracks",
          action="store_false",
          help="Downsample only the corner files, not tracks",
          default=True)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find SIMNAME and NEWNAME",
          metavar="DIRNAME", default='.'))
    ]

_zigargs['MultiDownsample'] = [
    (("multiSim",), 
     dict(help="Downsample the simulations of MULTISIM",
          metavar="MULTISIM")),
    (("newName",), 
     dict(help="Name of the downsampled multi-sim",
          metavar="NEWMULTI")),
    (("skipCnt",), 
     dict(type=int,
          help="Skip CNT frames for downsampling",
          metavar="CNT")),
#    (("--volume",),
#     dict(dest="doTracks",
#          action="store_false",
#          help="Downsample only the corner files, not tracks",
#          default=True)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find MULTISIM and NEWMULTI",
          metavar="DIRNAME", default='.'))
    ]


_zigargs['DoTracking'] = [
    (("simName",), 
     dict(help="Generate Tracks for SIMNAME",
          metavar="SIMNAME")),
    (("trackconfs",), 
     dict(nargs='+',
          help="Config files for the parameters for the trackers",
          metavar="CONF")),
    (("-t", "--trackruns"),
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to perform.  Perform all runs in CONF if none are given.",
          metavar="RUN", default=None)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find SIMNAME",
          metavar="DIRNAME", default='.'))
    ]


_zigargs['MultiTracking'] = [
    (("multiSim",), 
     dict(help="Generate Tracks for MULTISIM",
          metavar="MULTISIM")),
    (("trackconfs",), 
     dict(nargs='+',
          help="Config files for the parameters for the trackers",
          metavar="CONF")),
    (("-t", "--trackruns"), 
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to perform.  Perform all runs in CONF if none are given.",
          metavar="RUN", default=None)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find MULTISIM",
          metavar="DIRNAME", default='.'))
    ]

_zigargs['AnalyzeTracking'] = [
    (("simName",),
     dict(type=str,
          help="Analyze tracks for SIMNAME",
          metavar="SIMNAME", default="NewSim")),
    (("skillNames",), 
     dict(nargs="+",
          help="The skill measures to use (e.g., HSS)",
          metavar="SKILL")),
    (("-t", "--trackruns"), 
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to analyze.  Analyze all runs if none are given",
          metavar="RUN", default=None)),
    (("--cache",), 
     dict(dest="cacheOnly",
          help="Only bother with processing for the purpose of caching results.",
          action="store_true", default=False)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find SIMNAME",
          metavar="DIRNAME", default='.'))
    ]

_zigargs['MultiAnalysis'] = [
    (("multiSim",), 
     dict(help="Analyze tracks for MULTISIM",
          metavar="MULTISIM", default="NewMulti")),
    (("skillNames",), 
     dict(nargs="+",
          help="The skill measures to use",
          metavar="SKILL")),
    (("-t", "--trackruns"), 
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to analyze.  Analyze all runs if none are given",
          metavar="RUN", default=None)),

    (("--titles",),
     dict(dest="titles",
          nargs="+", help="Titles for the plots.  Default is to use the skill score name",
          metavar="TITLE", default=None)),
    (("--labels",),
     dict(dest="labels",
          nargs="+", help="Tick labels.  Default is to use the run names.",
          metavar="LABEL", default=None)),


    (("--cache",),
     dict(dest="cacheOnly",
          help="Only bother with processing for the purpose of caching results.",
          action="store_true", default=False)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find MULTISIM",
          metavar="DIRNAME", default='.')),

    (("--compare",), 
     dict(dest="compareTo", type=str,
          help="Compare other trackers to TRACKER",
          metavar="TRACKER", default="MHT")),
    (("--find_best",), 
     dict(dest="doFindBest", action="store_true",
          help="Find the best comparisons.", default=False)),
    (("--find_worst",), 
     dict(dest="doFindWorst", action = "store_true",
          help="Find the Worst comparisons.", default=False)),

    (("--save",), 
     dict(dest="saveImgFile", type=str,
          help="Save the resulting image using FILESTEM as the prefix. (e.g., saved file will be 'foo/bar_PC.png' for the PC skill scores and suffix of 'foo/bar').  Use --type to control which image format.",
          metavar="FILESTEM", default=None)),
    (("--type",), 
     dict(dest="imageType", type=str,
          help="Image format to use for saving the figures. Default: %(default)s",
          metavar="TYPE", default='png')),
    (("-f", "--figsize"), 
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: %(default)s",
          metavar="SIZE", default=(11.0, 5.0))),
    (("--noshow",), 
     dict(dest="doShow", action = 'store_false',
          help="To display or not to display...",
          default=True))
    ]

_zigargs['MultiScenarioAnalysis'] = [
    (("multiSims",),  
     dict(help="Analyze tracks for MULTISIM",
          nargs='+',
          metavar="MULTISIM", type=str)),
    (("-s", "--skills"), 
     dict(dest="skillNames",
          help="The skill measures to use",
          nargs='+', metavar="SKILL")),
    (("-t", "--trackruns"), 
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to analyze.  Analyze all common runs if none are given",
          metavar="RUN", default=None)),
    (("--titles",),
     dict(dest="titles",
          nargs="+", help="Titles for the plots.  Default is to use the skill score name",
          metavar="TITLE", default=None)),
    (("--labels",),
     dict(dest="labels",
          nargs="+", help="Tick labels.  Default is to use the sim names",
          metavar="LABEL", default=None)),

    (("--cache",), 
     dict(dest="cacheOnly",
          help="Only bother with processing for the purpose of caching results.",
          action="store_true", default=False)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find MULTISIM",
          metavar="DIRNAME", default='.')),

    (("--save",), 
     dict(dest="saveImgFile", type=str,
          help="Save the resulting image using FILESTEM as the prefix. (e.g., saved file will be 'foo/bar_PC.png' for the PC skill scores and suffix of 'foo/bar').  Use --type to control which image format.",
          metavar="FILESTEM", default=None)),
    (("--type",), 
     dict(dest="imageType", type=str,
          help="Image format to use for saving the figures. Default: %(default)s",
          metavar="TYPE", default='png')),
    (("-f", "--figsize"), 
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: %(default)s",
          metavar="SIZE", default=(11.0, 5.0))),
    (("--noshow",), 
     dict(dest="doShow", action = 'store_false',
          help="To display or not to display...",
          default=True))
    ]

_zigargs['ListRuns'] = [
    (("simNames",), 
     dict(nargs='+',
          help="List track runs done for SIMNAME. If more than one, then list all common track runs.",
          metavar="SIMNAME")),
    (("-f", "--files"),
     dict(action='store_true', dest='listfiles',
          help="Do we list the track runs, or the track result files? (Default is to list the runs)",
          default=False)),
    (("-t", "--trackruns"), 
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to list.  List all runs if none are given.",
          metavar="RUN", default=None)),
    (("-m", "--multi"), 
     dict(dest='isMulti',
          help="Indicate that SIMNAME(s) is actually a Multi-Sim so that we can process correctly.",
          default=False, action='store_true')),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to find SIMNAME",
          metavar="DIRNAME", default='.'))
    ]

_zigargs['ParamSearch'] = [
    (("paramFile",), 
     dict(help="The configuration file", metavar="FILE")),
    (("tracker",), 
     dict(help="The tracker algorithm to use", metavar="TRACKER")),
    (("-p", "--param"), 
     dict(dest="parameters", type=str,
          help="Name of parameter", action="append",
          metavar="NAME", default=[])),
    (("--silent",), 
     dict(dest="silentParams", type=str,
          help="Parameters not to include in the name of the track runs",
          metavar="NAME", nargs='+', default=[])),
    (("-i", "--int"), 
     dict(dest="paramSpecs", type=int,
          help="Scalar integer parameter value", action="append",
          metavar="VAL")),
    (("-f", "--float"), 
     dict(dest="paramSpecs", type=float,
          help="Scalar float parameter value", action="append",
          metavar="VAL")),
    (("-s", "--str"), 
     dict(dest="paramSpecs", type=str,
          help="Scalar str parameter value", action="append",
          metavar="VAL")),
    (("-b", "--bool"), 
     dict(dest="paramSpecs", type=bool,
          help="Scalar bool parameter value", action="append",
          metavar="VAL")),
    (("--lint",), 
     dict(dest="paramSpecs", nargs='+', type=int,
          help="Integer list parameter value", action="append",
          metavar="VAL")),
    (("--lfloat",), 
     dict(dest="paramSpecs", nargs='+', type=float,
          help="Float list parameter value", action="append",
          metavar="VAL")),
    (("--lstr",), 
     dict(dest="paramSpecs", nargs='+', type=str,
          help="String list parameter value", action="append",
          metavar="VAL")),
    (("--lbool",), 
     dict(dest="paramSpecs", nargs='+', type=bool,
          help="String list parameter value", action="append",
          metavar="VAL")),

    (("--range",), 
     dict(dest="paramSpecs", nargs='+', type=int,
          help="Integer list created by range()", action='AppendRange',
          metavar="VAL")),
    (("--arange",), 
     dict(dest="paramSpecs", nargs='+', type=float,
          help="Float list created by numpy.arange()", action='AppendARange',
          metavar="VAL")),
    (("--linspace",), 
     dict(dest="paramSpecs", nargs='+', type=float,
          help="Float list created by numpy.linspace()", action='AppendLinspace',
          metavar="VAL")),
    (("--logspace",), 
     dict(dest="paramSpecs", nargs='+', type=float,
          help="Float list created by numpy.logspace()", action='AppendLogspace',
          metavar="VAL"))
    ]



_zigargs['ShowTracks2'] = [
    (("trackFiles",),
     dict(nargs='+',
          help="TRACKFILEs to use for display",
          metavar="TRACKFILE")),
    (("--titles",),
     dict(dest='trackTitles', type=str,
          nargs='*', help="Titles to use for the figure subplots. Default is to use the filenames.",
          metavar="TITLE", default=None)),

    (("--save",),
     dict(dest="saveImgFile",
          help="Save the resulting image as FILENAME.",
          metavar="FILENAME", default=None)),
    (("--noshow",),
     dict(dest="doShow", action = 'store_false',
          help="To display or not to display...",
          default=True)),

    (("-l", "--layout"),
     dict(dest="layout", type=int,
          nargs=2, help="Layout of the subplots (rows x columns). All plots on one row by default.",
          metavar="NUM", default=None)),
    (("-f", "--figsize"),
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: auto",
          metavar="SIZE", default=None))

    ]


_zigargs['ShowCompare2'] = [
    (("trackFiles",),
     dict(nargs='+',
          help="TRACKFILEs to use for display",
          metavar="TRACKFILE")),
    (("-t", "--truth"),
     dict(dest="truthTrackFile", nargs='+',
          help="Use TRUTHFILE for true track data",
          metavar="TRUTHFILE")),
    (("--titles",),
     dict(dest='trackTitles', type=str,
          nargs='*', help="Titles to use for the figure subplots. Default is to use the filenames or the track run names.",
          metavar="TITLE", default=None)),

    (("--save",),
     dict(dest="saveImgFile",
          help="Save the resulting image as FILENAME.",
          metavar="FILENAME", default=None)),
    (("--noshow",),
     dict(dest="doShow", action = 'store_false',
          help="To display or not to display...",
          default=True)),

    (("-l", "--layout"),
     dict(dest="layout", type=int,
          nargs=2, help="Layout of the subplots (rows x columns). All plots on one row by default.",
          metavar="NUM", default=None)),
    (("-f", "--figsize"),
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: auto",
          metavar="SIZE", default=None))

    ]

_zigargs['ShowCorners2'] = [
    (("inputDataFiles",),
     dict(nargs='+',
          help="Use INDATAFILE for finding corner data files",
          metavar="INDATAFILE")),
    (("--titles",),
     dict(dest='trackTitles', type=str,
          nargs='*', help="Titles to use for the figure subplots. Default is to use the filenames or the track run names.",
          metavar="TITLE", default=None)),

    (("--save",),
     dict(dest="saveImgFile",
          help="Save the resulting image as FILENAME.",
          metavar="FILENAME", default=None)),
    (("--noshow",),
     dict(dest="doShow", action = 'store_false',
          help="To display or not to display...",
          default=True)),

    (("-l", "--layout"),
     dict(dest="layout", type=int,
          nargs=2, help="Layout of the subplots (rows x columns). All plots on one row by default.",
          metavar="NUM", default=None)),
    (("-f", "--figsize"),
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: auto",
          metavar="SIZE", default=None))

    ]








_zigargs['ShowTracks'] = [
    (("trackFiles",), 
     dict(nargs='*',
          help="TRACKFILEs to use for display",
          metavar="TRACKFILE", default=[])),
    (("-t", "--truth"), 
     dict(dest="truthTrackFile",
          help="Use TRUTHFILE for true track data",
          metavar="TRUTHFILE", default=None)),
    (("-r", "--trackruns"), 
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to analyze.  Analyze all runs if none are given",
          metavar="RUN", default=None)),

    (("-s", "--simName"), 
     dict(dest="simName",
          help="Use data from the simulation SIMNAME",
          metavar="SIMNAME", default=None)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to work from when using --simName",
          metavar="DIRNAME", default=".")),

    (("--save",), 
     dict(dest="saveImgFile",
          help="Save the resulting image as FILENAME.",
          metavar="FILENAME", default=None)),
    (("--noshow",), 
     dict(dest="doShow", action = 'store_false',
          help="To display or not to display...",
          default=True)),

    (("-l", "--layout"), 
     dict(dest="layout", type=int,
          nargs=2, help="Layout of the subplots (rows x columns). All plots on one row by default.",
          metavar="NUM", default=None)),
    (("-f", "--figsize"), 
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: auto",
          metavar="SIZE", default=None)),
    (("--titles",), 
     dict(dest='trackTitles', type=str,
          nargs='*', help="Titles to use for the figure subplots. Default is to use the filenames or the track run names.",
          metavar="TITLE", default=None))
    ]


_zigargs['ShowAnims'] = [
    (("trackFiles",),
     dict(nargs='*',
          help="TRACKFILEs to use for display",
          metavar="TRACKFILE", default=[])),
    (("-t", "--truth"), 
     dict(dest="truthTrackFile",
          help="Use TRUTHFILE for true track data",
          metavar="TRUTHFILE", default=None)),
    (("-r", "--trackruns"), 
     dict(dest="trackRuns",
          nargs="+", help="Trackruns to analyze.  Analyze all runs if none are given",
          metavar="RUN", default=None)),

    (("-s", "--simName"), 
     dict(dest="simName",
          help="Use data from the simulation SIMNAME",
          metavar="SIMNAME", default=None)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to work from when using --simName",
          metavar="DIRNAME", default=".")),

    (("-l", "--layout"), 
     dict(dest="layout", type=int,
          nargs=2, help="Layout of the subplots (rows x columns). All plots on one row by default.",
          metavar="NUM", default=None)),
    (("-f", "--figsize"), 
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: auto",
          metavar="SIZE", default=None)),
#    (("--titles",),
#     dict(dest='trackTitles', type=str,
#          nargs='*', help="Titles to use for the figure subplots. Default is to use the filenames or the track run names.",
#          metavar="TITLE", default=None))

    ]

_zigargs['ShowCorners'] = [
    (("inputDataFiles",), 
     dict(nargs='*',
          help="Use INDATAFILE for finding corner data files",
          metavar="INDATAFILE")),
    (("-t", "--track"), 
     dict(dest="trackFile",
          help="Use TRACKFILE for determining domain limits.",
          metavar="TRACKFILE", default=None)),

    (("-s", "--simName"), 
     dict(dest="simName",
          help="Use data from the simulation SIMNAME.",
          metavar="SIMNAME", default=None)),
    (("-d", "--dir"), 
     dict(dest="directory",
          help="Base directory to work from when using --simName",
          metavar="DIRNAME", default=".")),

    (("-l", "--layout"), 
     dict(dest="layout", type=int,
          nargs=2, help="Layout of the subplots (rows x columns). All plots on one row by default.",
          metavar="NUM", default=None)),
    (("-f", "--figsize"), 
     dict(dest="figsize", type=float,
          nargs=2, help="Size of the figure in inches (width x height). Default: auto",
          metavar="SIZE", default=None)),
#    (("--titles",),
#     dict(dest='trackTitles', type=str,
#          nargs='*', help="Titles to use for the figure subplots. Default is to use the filenames or the track run names.",
#          metavar="TITLE", default=None))

    ]


_zigargs['TrackReports'] = [
    (("trackfiles",),
     dict(nargs='+', type=str,
          help='Analyze the tracks in FILE.',
          metavar='FILE')),
    ]

