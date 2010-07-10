import sys
import os
import xbmcgui
import xbmcplugin

class Main:
    def __init__( self ):
        buttons = ( 
                ( "Default Playlist", "%s?menuId=%s" % ( sys.argv[ 0 ], "default", ),    ),
                ( "World News Australia", "%s?menuId=%s" % ( sys.argv[ 0 ], "1", ),    ),
                ( "FIFA World Cup 2010", "%s?menuId=%s" % ( sys.argv[ 0 ], "642", ),    ),
                ( "The World Game", "%s?menuId=%s" % ( sys.argv[ 0 ], "117", ),    ),
                ( "The Ashes", "%s?menuId=%s" % ( sys.argv[ 0 ], "321", ),    ),
                ( "Speedweek", "%s?menuId=%s" % ( sys.argv[ 0 ], "236", ),    ),
                ( "Le Tour de France", "%s?menuId=%s" % ( sys.argv[ 0 ], "99", ),    ),
                ( "Cycling Central", "%s?menuId=%s" % ( sys.argv[ 0 ], "160", ),    ),
                ( "Dakar Rally", "%s?menuId=%s" % ( sys.argv[ 0 ], "180", ),    ),
            )
        for button in buttons:
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(button[0]),url=button[1],totalItems=len( buttons ),isFolder=True)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )