import sys
import re
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import xml.etree.ElementTree

class Main:
    Addon = xbmcaddon.Addon( id=os.path.basename( os.getcwd() ) )
    BASE_CURRENT_URL = "http://player.sbs.com.au/video/smil/index/standalone/%s"
    def __init__( self ):
        if self.Addon.getSetting("prompt_user") == 'true':
            self.Addon.openSettings()
        params = self._parse_argv()
        if params["downloadId"] == "default":
            downloadId = self.BASE_CURRENT_URL % ("94")
        else:
            downloadId = self.BASE_CURRENT_URL % (params["downloadId"])
        smil = xml.etree.ElementTree.parse(downloadId)
        url = None
        for video in smil.findall("body/switch/video"):
            if self.Addon.getSetting( "vid_quality" ) == "2" and video.get("system-bitrate") == "1000000.00": #1000kbps 
                url = video.get("src")
            elif self.Addon.getSetting( "vid_quality" ) == "1" and video.get("system-bitrate") == "300000.000": #300kbps
                url = video.get("src")
            elif self.Addon.getSetting( "vid_quality" ) == "0" and video.get("system-bitrate") == "128000.000": #128kbps
                url = video.get("src")
        if (url == None):
            url = smil.find("body/switch/video").get("src")
            print "defaulted..."
            print self.Addon.getSetting( "vid_quality" )
        
        base = smil.find("head/meta").get("base")
        if (base[0:4] == 'rtmp'):
            url = base + " playpath=" + url.rsplit(".",1)[0]
        else:
            url = base + url
        item = xbmcgui.ListItem(params["title"])
        item.setInfo("video",{'date': params["date"],'year':int(params["year"]),'plot':params["description"],'duration':params["duration"]})
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, item)
        #xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(menu.findtext("title")),url=sys.argv[ 0 ])
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        
    def _parse_argv( self ):
        try:
            # parse sys.argv for params and return result
            params = dict( urllib.unquote_plus( arg ).split( "=" ) for arg in sys.argv[ 2 ][ 1 : ].split( "&" ) )
            # we need to do this as quote_plus and unicode do not work well together
            #params[ "category" ] = eval( params[ "category" ] )
        except:
            # no params passed
            params = { "downloadId": "default"}#"category": None }
        # return params
        return params
        
    def _fetch_url( self, url ):
        sock = urllib.urlopen(url)
        data = sock.read()
        sock.close()
        return data