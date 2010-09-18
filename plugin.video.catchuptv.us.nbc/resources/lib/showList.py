from BeautifulSoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus
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
    BASE_URL = 'http://www.nbc.com/'
    INDEX_URL = 'http://www.nbc.com/video/library/full-episodes/'
    def __init__( self ):
        print 'Fetching %s' % self.INDEX_URL
        source = self._fetch_url(self.INDEX_URL)
        fodIndex = BeautifulSoup(source)
        showsListing = fodIndex.find('div',{"class":re.compile('group-full-eps')}).findAll('li')
        print 'Parsed listing and found %d shows' % len(showsListing)
        for show in showsListing:
            showLink = show.find('a')
            listitem=xbmcgui.ListItem(decode_htmlentities(showLink['title']))
            episodeCount = show.find('div',text=re.compile('^[0-9]+ Videos?$'))
            if episodeCount:
                episodeCount = int(re.search('^([0-9]+)\s*Videos?$',episodeCount.string).group(1))
                print 'Found "%s" with %d episodes' % (decode_htmlentities(showLink['title']),episodeCount)
                listitem.setInfo('video',{'episode':episodeCount})
            else: 
                print 'Found "%s" but did not find how many episodes' % decode_htmlentities(showLink['title'])
            listitem.setThumbnailImage(showLink.find('img')['src'])
            if showLink['href'][0] == '/':
                showUrl = showLink['href'][1:]
            else:
                showUrl = showLink['href'].replace(self.BASE_URL,'')
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?showUrl=%s" % ( sys.argv[ 0 ], quote_plus(showUrl)),totalItems=len(showsListing),isFolder=True)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )

    def _fetch_url(self, url):
        url = urllib2.urlopen(url)
        source = url.read()
        return source