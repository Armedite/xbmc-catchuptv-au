"""
    Plugin for watching ABC News 24 Stream
"""
import xbmc, xbmcgui, xbmcplugin, os

if ( __name__ == "__main__" ):
    # This is simply a static URL
    # In the future, this plugin should check http://tviview.abc.net.au/iview/api2/?series=2932730 for the url
    # And also use an auth parameter specifed by http://tviview.abc.net.au/iview/auth/?v2
    
    stream="news24-hi@28773" #change this to news24-med@28772 or news24-lo@28771 for lower quality
    rtmp_url="rtmp://cp81899.live.edgefcs.net//"+stream+" app=live/"+stream+" swfurl=http://www.abc.net.au/iview/images/iview.jpg swfvfy=true live=true"
    item = xbmcgui.ListItem("ABC News 24")
    item.setInfo('video', {"genre": "news"})
    item.setThumbnailImage(os.path.join(os.getcwd(),'icon.png'))
    # Future versions of this plugin could fetch the ABC News 24 TV Guide to get which show is "Now Playing"
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(rtmp_url, item)