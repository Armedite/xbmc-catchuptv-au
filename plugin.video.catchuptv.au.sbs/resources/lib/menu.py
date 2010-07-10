import sys
import re
import xbmcgui
import xbmcplugin
import urllib
import xml.etree.ElementTree

class Main:
    BASE_CURRENT_URL = "http://player.sbs.com.au/video/menu/index/standalone/%s"
    def __init__( self ):
        params = self._parse_argv()
        if params["menuId"] == "default":
            m = re.search('name="menuURL"\s+value="(.+?)"',self._fetch_url("http://player.sbs.com.au/playerassets/programs/standalone_settings.xml"))
            if len(m.group(1)) == 0: raise
            if m.group(1).startswith('/'):
                menuUrl = "http://player.sbs.com.au%s" % m.group(1)
            else:
                menuUrl = m.group(1)
        else:
            menuUrl = self.BASE_CURRENT_URL % (params["menuId"])
        menu = xml.etree.ElementTree.parse(menuUrl)
        menus = menu.findall("menu/menu")
        for item in menus: #find all submenus, as we assume that everything is two levels deep
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(item.findtext("title")),url="%s?playlistId=%s" % ( sys.argv[ 0 ], item.find("playlist").get("xmlSrc").rsplit("/",1)[1], ),isFolder=True, totalItems=len(menus))   
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        
    def _parse_argv( self ):
        try:
            # parse sys.argv for params and return result
            params = dict( urllib.unquote_plus( arg ).split( "=" ) for arg in sys.argv[ 2 ][ 1 : ].split( "&" ) )
            # we need to do this as quote_plus and unicode do not work well together
            #params[ "category" ] = eval( params[ "category" ] )
        except:
            # no params passed
            params = { "menuId": "default"}#"category": None }
        # return params
        return params
        
    def _fetch_url( self, url ):
        sock = urllib.urlopen(url)
        data = sock.read()
        sock.close()
        return data