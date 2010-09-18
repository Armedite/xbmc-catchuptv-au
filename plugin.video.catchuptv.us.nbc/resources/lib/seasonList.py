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
    BASE_URL = 'http://www.nbc.com/'
    def __init__( self ):
        params = self._parse_argv()
        source = self._fetch_url(self.BASE_URL + unquote_plus(params['showUrl']))
        print 'Loading ' + self.BASE_URL + unquote_plus(params['showUrl'])
        seasonIndex = BeautifulSoup(source)
        tvshowcontainer = seasonIndex.find('div',id=re.compile('scet_header|scet_top|show-header|show-header-scet|^header$'))
        if tvshowcontainer==None:
            tvshowcontainer=seasonIndex.find('div',{'class':re.compile('scet_header|scet_top|show-header|show-header-scet')})
        if tvshowcontainer!=None:
            tvshowtitle = tvshowcontainer.find('h1').string
        else:
            tvshowtitle = re.search('var siteName = "(.+?)";',source).group(1)
        print 'Parsing seasons for "%s"' % tvshowtitle
        showsListing = seasonIndex.find('div',{"class":re.compile('scet-gallery-nav')}).find('h3',text='Full Episodes').parent.findNextSibling('ul').findAll('li')
        for show in showsListing:
            showLink = show.find('a')
            print 'Found '+showLink.string
            listitem=xbmcgui.ListItem(decode_htmlentities(showLink.string))
            listitem.setInfo('video',{'tvshowtitle':tvshowtitle})
            #listitem.setThumbnailImage(showLink.find('img')['src'])
            if showLink['href'][0] == '/':
                showUrl = showLink['href'][1:]
            else:
                showUrl = showLink['href'].replace(self.BASE_URL,'')
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?seasonUrl=%s" % ( sys.argv[ 0 ], quote_plus(showUrl),),totalItems=len(showsListing),isFolder=True)
        xbmcplugin.setContent( handle=int(sys.argv[1]), content='seasons')
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