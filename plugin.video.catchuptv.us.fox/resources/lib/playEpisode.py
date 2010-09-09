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
    BASE_URL = 'http://www.fox.com/'
    BASE_FOD_URL = 'http://www.fox.com/fod/'
    AMF_URL = 'http://c.brightcove.com/services/messagebroker/amf?playerId=%s'
    SWF_URL = 'http://admin.brightcove.com/viewer/us1.24.00.04/federatedVideo/BrightcovePlayer.swf'
    def __init__( self ):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s')
        params = self._parse_argv()
        #Download the page required
        pageUrl = self.BASE_URL + unquote_plus(params['episodeUrl'])
        source = self._fetch_url(pageUrl)
        
        # Extact the ID numbers from the page
        playerId= re.search('<param name="playerID" value="([0-9]+?)" />',source).group(1)
        #publisherId= re.search('<param name="publisherID" value="([0-9]+?)" />',source).group(1)
        contentId= re.search('<param name="@videoPlayer" value="([0-9]+?)" />',source).group(1)
        
        # Connect to the Brightcove AMF service
        client = RemotingService(self.AMF_URL % playerId,amf_version=3,logger=logging)
        service = client.getService('com.brightcove.experience.ExperienceRuntimeFacade')
        
        # Prepare the classes (explict type checking is used)
        pyamf.register_class(ViewerExperienceRequest,'com.brightcove.experience.ViewerExperienceRequest')
        pyamf.register_class(ContentOverride,'com.brightcove.experience.ContentOverride')
        
        # Prepare the data to send
        contentOverrides = ContentOverride({'featuredId':float(0), 'contentIds':None, 'contentType':0, 'contentId':float(contentId),'contentRefId':None,'featuredRefId':None,'target':'videoPlayer','contentRefIds':None})
        viewerExperienceRequest = ViewerExperienceRequest({'deliveryType':float(0),'contentOverrides':[contentOverrides],'URL':pageUrl,'playerKey':'','experienceId':float(playerId),'TTLToken':''})
        
        # Make the request
        response = service.getDataForExperience('d279c0ccec2bae8431eb824d32e45b4d1a24ad9f',viewerExperienceRequest)
        
        # Extract the RMPT(e) Url
        urlMatches = re.search('^rtmpe?://([^/]+?)/ondemand/.*?(mp4:[^\?]+?)(?:\.mp4)?(?:\?(.+))?$',response['programmedContent']['videoPlayer']['mediaDTO']['FLVFullLengthURL'])
        tcUrl = urlMatches.group(0)
        app = 'ondemand?%s' % urlMatches.group(3)
        playpath = urlMatches.group(2)
        host = urlMatches.group(1)
        rtmp_url = "rtmpe://%s/%s playpath=%s swfUrl=%s swfVfy=1" % (host,app,playpath,self.SWF_URL)
        print 'rtmpdump -r "rtmpe://%s/%s" -y "%s" -W "%s" -o "%s"' % (host,app,playpath,self.SWF_URL,'video.mp4')
        
        # Play the url
        listitem = xbmcgui.ListItem(response['programmedContent']['videoPlayer']['mediaDTO']['displayName'])
        listitem.setInfo("video",{'title':response['programmedContent']['videoPlayer']['mediaDTO']['displayName'],'tvshowtitle':response['programmedContent']['videoPlayer']['mediaDTO']['customFields']['series'],'genre':response['programmedContent']['videoPlayer']['mediaDTO']['customFields']['genre'],'mpaa':response['programmedContent']['videoPlayer']['mediaDTO']['customFields']['rating'],'episode':int(response['programmedContent']['videoPlayer']['mediaDTO']['customFields']['episode']),'season':int(response['programmedContent']['videoPlayer']['mediaDTO']['customFields']['season']),'aired':response['programmedContent']['videoPlayer']['mediaDTO']['customFields']['airdate'],'studio':'FOX'})
        listitem.setThumbnailImage(response['programmedContent']['videoPlayer']['mediaDTO']['thumbnailURL'])
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

# These classes are used by the AMF aliasing
class ViewerExperienceRequest(dict):
    pass

class ContentOverride(dict):
    pass