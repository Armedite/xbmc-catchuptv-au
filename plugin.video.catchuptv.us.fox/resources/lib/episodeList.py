from BeautifulSoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus,unquote_plus
import re
import sys
import os
import xbmcgui
import xbmcplugin
import urllib2

from htmlentitydefs import name2codepoint as n2cp
def substitute_entity(match):
    ent = match.group(2)
    if match.group(1) == "#":
        return unichr(int(ent))
    else:
        cp = n2cp.get(ent)

        if cp:
            return unichr(cp)
        else:
            return match.group()

def decode_htmlentities(string):
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(substitute_entity, string)[0]

class Main:
    BASE_URL = 'http://www.fox.com/'
    BASE_FOD_URL = 'http://www.fox.com/fod/'
    def __init__( self ):
        params = self._parse_argv()
        source = self._fetch_url(self.BASE_URL + unquote_plus(params['showUrl']))
        showIndex = BeautifulSoup(source)
        vidInfo = {'tvshowtitle': showIndex.find('div',id='showDashboard').find('span',{'class':'blueText'}).string, 'studio': 'FOX'}
        seasonsListing = showIndex.findAll('div',{'class':re.compile('dashPageHolder'),'id':re.compile('^fullEp')})
        print len(seasonsListing)
        for season in seasonsListing:
            episodesListing = season.findAll('div',{'class':'episodeListing'})
            for episode in episodesListing:
                listitem = xbmcgui.ListItem(episode.find('h3').find('a').string)
                listitem.setThumbnailImage(episode.find('img',id=re.compile('^epThumb'))['src'])
                episodeLink = episode.find('a',{'class':'thumbnailLink'})
                if episodeLink['href'][0] == '/':
                    episodeUrl = episodeLink['href'][1:]
                else:
                    episodeUrl = episodeLink['href'].replace(self.BASE_URL,'')
                airedDateAndPlot = re.search('Aired\s+([01]?[0-9])/([0-3]?[0-9])/([0-9]{2,4})\s*(?:<br\s*/?>)?\s*(.+?)\s*</div>$',str(episode.find('div',{'class':'episodeInfo'})))
                seasonNum = re.search('Season\s+([0-9]+?)[\s:]',str(episode.find('p',{'class':'seasonNum'})))
                episodeNumAndDuration = re.search('Episode\s+([0-9]+?)\s+?\(((?:[0-9]*?:)?[0-9]*?:[0-9]+?)\)',str(episode.find('p',{'class':'episodeNumLine'})))
                vidInfo['aired'] = '%s-%s-%s' % (airedDateAndPlot.group(3),airedDateAndPlot.group(1),airedDateAndPlot.group(2))
                vidInfo['season'] = int(seasonNum.group(1))
                vidInfo['episode'] = int(episodeNumAndDuration.group(1))
                vidInfo['duration'] = episodeNumAndDuration.group(2)
                vidInfo['title'] = episode.find('h3').find('a').string
                vidInfo['plot'] = decode_htmlentities(airedDateAndPlot.group(4))
                print vidInfo
                listitem.setInfo("video",vidInfo)
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?episodeUrl=%s" % ( sys.argv[ 0 ], quote_plus(episodeUrl)))
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        
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