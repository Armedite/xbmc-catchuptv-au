import sys
import re
import xbmcgui
import xbmcplugin
import urllib
import xml.etree.ElementTree
import time
class Main:
    BASE_CURRENT_URL = "http://player.sbs.com.au/video/playlist/index/standalone/%s"
    def __init__( self ):
        params = self._parse_argv()
        if params["playlistId"] == "default":
            playlistUrl = self.BASE_CURRENT_URL % ("94")
        else:
            playlistUrl = self.BASE_CURRENT_URL % (params["playlistId"])
        playlist = xml.etree.ElementTree.parse(playlistUrl)
        videos = playlist.findall("video")
        for video in videos: 
            listItm = xbmcgui.ListItem(video.findtext("title"))
            for img in video.findall("media/image"):
                if (img.get("type") == "thumbnail" and len(img.get("src"))>0):
                    listItm.setThumbnailImage(img.get("src"))
            if int(video.findtext("date")) > 0:
                date = int(video.findtext("date")) / 1000
            else:
                date = 0
            hours, remainder = divmod(int(video.findtext("duration"))/1000, 3600)
            minutes, seconds = divmod(remainder, 60)
            try:
                listItm.setInfo("video",{'date': time.strftime("%d.%m.%Y",time.gmtime(date)),'year':int(time.strftime("%Y",time.gmtime(date))),'plot':video.findtext("description"),'duration':"%s:%s:%s" % (hours, minutes, seconds)})
            except: pass
            #TODO: Do some intelegent auto-parsing such as spliting at '-'s and loking for "ep 54", etc.
            #TODO: I couldn't work out how to do it, but reusing the existing list item would be better (perhaps?) rather than passing all the data
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),
                listitem=listItm,
                url='%s?downloadId=%s&title=%s&description=%s&duration=%s&date=%s&year=%s' % (
                    sys.argv[ 0 ],
                    video.get("src").rsplit("/",1)[1],
                    urllib.quote_plus(video.findtext("title")),
                    urllib.quote_plus(video.findtext("description")),
                    urllib.quote_plus("%s:%s:%s" % (hours, minutes, seconds)),
                    urllib.quote_plus(time.strftime("%d.%m.%Y",time.gmtime(date))),
                    urllib.quote_plus(time.strftime("%Y",time.gmtime(date))) 
                ),
                totalItems=len(videos))
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
            params = { "menuId": "default"}#"category": None }
        # return params
        return params
        
    def _fetch_url( self, url ):
        sock = urllib.urlopen(url)
        data = sock.read()
        sock.close()
        return data