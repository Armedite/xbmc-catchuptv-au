from urllib import unquote_plus
from pyamf.remoting.client import RemotingService
import pyamf
import re
import logging
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import urllib2

class Main:
    BASE_URL = 'http://www.nbc.com/'
    SMIL_URL = 'http://video.nbcuni.com/%s'
    AMF_URL = 'http://video.nbcuni.com/amfphp/gateway.php'
    SWF_URL = 'http://www.nbc.com/assets/video/4-0/swf/NBCVideoApp.swf'
    CONFIG_ID = 17010
    def __init__( self ):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s')
        params = self._parse_argv()
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('NBC Video Player', 'Getting Episode ID')
        pDialog.update(5)
        
        #Download the page required
        pageUrl = self.BASE_URL + unquote_plus(params['episodeUrl'])
        source = self._fetch_url(pageUrl)
        pDialog.update(30)
        
        # Extact the ID numbers from the page
        vidId= re.search('var\s*assetId\s*=\s*\'?([0-9]+)\'?;',source).group(1)
        
        pDialog.create('NBC Video Player', 'Retrieving Episode URL')
        pDialog.update(40)
        
        # Connect to the AMF service
        client = RemotingService(self.AMF_URL,amf_version=1,logger=logging)
        
        # Make the request
        response = client.getService('getClipInfo.getClipAll')(vidId,'US','632','-1')
        pDialog.update(50)
        
        # Retrieve SMIL
        smil = self._fetch_url(self.SMIL_URL % response['clipurl'])
        file = re.search('<video src="(.+?)"',smil).group(1)
        
        pDialog.update(60)
        pDialog.create('NBC Video Player', 'Getting NBC Video Player Configuration')
        
        # Retrieve video config
        config = client.getService('getConfigInfo.getConfigAll')(self.CONFIG_ID)
        
        pDialog.update(75)
        pDialog.create('NBC Video Player', 'Connecting to RTMP Server')

        # Generate the RMPT(e) Url
        rtmp_url = "rtmp://%s/%s playpath=%s swfUrl=%s swfVfy=1" % (config['akamaiHostName'], config['akamaiAppName'], file.replace('.flv',''),self.SWF_URL)
        print 'rtmpdump -r "rtmp://%s/%s" -y "%s" -W "%s" -o "%s"' % (config['akamaiHostName'], config['akamaiAppName'], file.replace('.flv',''),self.SWF_URL,'video.flv')
        
        # Play the url
        listitem = xbmcgui.ListItem(response['metadata']['title'])
        listitem.setInfo("video",{'title':response['metadata']['title'],'tvshowtitle':response['metadata']['show'],'plot':response['metadata']['description'],'date':response['metadata']['publishdate'],'season':int(params['season']),'episode':int(params['episode']),'studio':'NBC'})
        listitem.setThumbnailImage(self.SMIL_URL % response['metadata']['imageurl'])
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(rtmp_url, listitem)
        
    def _parse_argv( self ):
        try:
            # parse sys.argv for params and return result
            params = dict( arg.split( "=" ) for arg in sys.argv[ 2 ][ 1 : ].split( "&" ) )
        except:
            # no params passed
            params = {}
        return params

    def _fetch_url(self, url):
        url = urllib2.urlopen(url)
        source = url.read()
        return source