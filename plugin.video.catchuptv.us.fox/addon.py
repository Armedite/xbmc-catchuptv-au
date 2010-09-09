"""
    Plugin for streaming Fox on Demand
"""

# main imports
import sys

# plugin constants (not used)
__plugin__ = "Fox on Demand"
__pluginid__ = "plugin.video.catchuptv.us.fox"
__author__ = "adammw111"
__url__ = "http://xbmc-catchuptv-au.googlecode.com/"
__svn_url__ = "http://xbmc-catchuptv-au.googlecode.com/svn/"
__useragent__ = "xbmcCatchUpTV/0.1"
__credits__ = "Team XBMC"
__version__ = "0.1.0"
__svn_revision__ = "$Revision: 1 $"
__XBMC_Revision__ = "31542"


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        import resources.lib.showList as plugin
        plugin.Main()
    elif ( sys.argv[ 2 ].startswith( "?showUrl=" ) ):
        import resources.lib.episodeList as plugin
        plugin.Main()
    elif ( sys.argv[ 2 ].startswith( "?episodeUrl=" ) ):
        import resources.lib.playEpisode as plugin
        plugin.Main()
    elif ( sys.argv[ 2 ].startswith( "?settings=" ) ):
        import os
        import xbmc
        import xbmcaddon
        # open settings
        xbmcaddon.Addon( id=os.path.basename( os.getcwd() ) ).openSettings()
        # refresh listing in case settings changed
        xbmc.executebuiltin( "Container.Refresh" )
