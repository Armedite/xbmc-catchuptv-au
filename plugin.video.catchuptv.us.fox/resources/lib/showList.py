from BeautifulSoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus
import sys
import os
import xbmcgui
import xbmcplugin
import urllib2

class Main:
    BASE_URL = 'http://www.fox.com/'
    BASE_FOD_URL = 'http://www.fox.com/fod/'
    def __init__( self ):
        source = self._fetch_url(self.BASE_FOD_URL)
        fodIndex = BeautifulSoup(source)
        showsListing = fodIndex.find('div',id='episodes-listing').findAll('li')
        for show in showsListing:
            showLink = show.find('a')
            if showLink['href'][0] == '/':
                showUrl = showLink['href'][1:]
            else:
                showUrl = showLink['href'].replace(self.BASE_URL,'')
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(showLink.string),url="%s?showUrl=%s" % ( sys.argv[ 0 ], quote_plus(showUrl)),totalItems=len(showsListing),isFolder=True)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )

    def _fetch_url(self, url):
        url = urllib2.urlopen(url)
        source = url.read()
        return source