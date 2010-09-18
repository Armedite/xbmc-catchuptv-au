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
        source = self._fetch_url(self.BASE_URL + unquote_plus(params['seasonUrl']))
        showIndex = BeautifulSoup(source)
        tvshowcontainer = showIndex.find('div',id=re.compile('scet_header|scet_top|show-header|show-header-scet|^header$'))
        if tvshowcontainer==None:
            tvshowcontainer=showIndex.find('div',{'class':re.compile('scet_header|scet_top|show-header|show-header-scet')})
        if tvshowcontainer!=None:
            tvshowtitle = tvshowcontainer.find('h1').string
        else:
            tvshowtitle = re.search('var siteName = "(.+?)";',source).group(1)
        pages = 1
        if showIndex.find('div',{'class':re.compile('nbcu_pager')}):
            pageLinks = showIndex.find('div',{'class':re.compile('nbcu_pager')}).findAll('a',{'class':re.compile('nbcu_pager_page')})
            pages = len(pageLinks)
        for i in range(0,pages):
            if i>0:
                source = self._fetch_url(self.BASE_URL + pageLinks[i]['href'])
                showIndex = BeautifulSoup(source)
            episodesListing = showIndex.find('ul',{'class':re.compile('scet_th_full')}).findAll('li')
            for episode in episodesListing:
                vidInfo = {'tvshowtitle': tvshowtitle, 'studio': 'NBC'}
                title = decode_htmlentities(episode.find('p',{'class':re.compile('list_full_det_title')}).find('a').string)
                listitem = xbmcgui.ListItem(title)
                listitem.setThumbnailImage(episode.find('img')['src'])
                episodeLink = episode.find('a')
                if episodeLink['href'][0] == '/':
                    episodeUrl = episodeLink['href'][1:]
                else:
                    episodeUrl = episodeLink['href'].replace(self.BASE_URL,'')
                if episode.find('p',{'class':re.compile('list_full_des')}):
                    vidInfo['plot'] = decode_htmlentities(episode.find('p',{'class':re.compile('list_full_des')}).find('em').string)
                epNum = re.search('^Ep(?:\.\s*)?([0-9]{1,2})([0-9][0-9])(?:\s*:\s*)?(.+)$',title)
                if epNum != None:
                    vidInfo['season'] = int(epNum.group(1))
                    vidInfo['episode'] = int(epNum.group(2))
                vidInfo['title'] = epNum.group(3)
                #airedDateAndPlot = re.search('Aired\s+([01]?[0-9])/([0-3]?[0-9])/([0-9]{2,4})\s*(?:<br\s*/?>)?\s*(.+?)\s*</div>$',str(episode.find('div',{'class':'episodeInfo'})))
                #seasonNum = re.search('Season\s+([0-9]+?)[\s:]',str(episode.find('p',{'class':'seasonNum'})))
                #episodeNumAndDuration = re.search('Episode\s+([0-9]+?)\s+?\(((?:[0-9]*?:)?[0-9]*?:[0-9]+?)\)',str(episode.find('p',{'class':'episodeNumLine'})))
                #vidInfo['aired'] = '%s-%s-%s' % (airedDateAndPlot.group(3),airedDateAndPlot.group(1),airedDateAndPlot.group(2))
                #vidInfo['season'] = int(seasonNum.group(1))
                #vidInfo['episode'] = int(episodeNumAndDuration.group(1))
                #vidInfo['duration'] = episodeNumAndDuration.group(2)
                #vidInfo['title'] = episode.find('h3').find('a').string
                #vidInfo['plot'] = decode_htmlentities(airedDateAndPlot.group(4))
                #print vidInfo
                listitem.setInfo("video",vidInfo)
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?episodeUrl=%s&episode=%s&season=%s" % ( sys.argv[ 0 ], quote_plus(episodeUrl),vidInfo['episode'],vidInfo['season']))
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_EPISODE )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DURATION )
        xbmcplugin.setContent( handle=int(sys.argv[1]), content='episodes')
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