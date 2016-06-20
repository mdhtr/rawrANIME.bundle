######################################################################################
#
#	rawrANIME (BY TEHCRUCIBLE) - v0.05
#
######################################################################################

TITLE = "rawrANIME"
PREFIX = "/video/rawranime"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://rawranime.tv"

######################################################################################
# Set global variables

def Start():

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(ICON_COVER)
    DirectoryObject.art = R(ART)
    PopupDirectoryObject.thumb = R(ICON_COVER)
    PopupDirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON_COVER)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
    HTTP.Headers['Referer'] = 'http://rawranime.tv/'

######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(LatestCategory, title="Latest Episodes"), title = "Latest Episodes", thumb = R(ICON_LIST)))
    oc.add(DirectoryObject(key = Callback(ShowCategory, title="Most Popular", category = "/list/popular"), title = "Most Popular", thumb = R(ICON_LIST)))
    oc.add(DirectoryObject(key = Callback(ShowCategory, title="Top Rated", category = "/list/toprated"), title = "Top Rated", thumb = R(ICON_LIST)))
    oc.add(DirectoryObject(key = Callback(ShowCategory, title="Ongoing Anime", category = "/list/popularongoing"), title = "Ongoing Anime", thumb = R(ICON_LIST)))
    oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Bookmarks"), title = "My Bookmarks", thumb = R(ICON_QUEUE)))
    oc.add(InputDirectoryObject(key=Callback(Search), title = "Search", prompt = "Search for anime?", thumb = R(ICON_SEARCH)))

    return oc

######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")
def Bookmarks(title):

    oc = ObjectContainer(title1 = title)

    for each in Dict:
        show_url = Dict[each]
        page_data = HTML.ElementFromURL(show_url)
        show_title = each
        show_thumb = BASE_URL + page_data.xpath("//div[@class='anime_info']//img/@data-original")[0]
        show_summary = page_data.xpath("//div[@class='anime_info_synopsis']/text()")[0]

        oc.add(DirectoryObject(
            key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
            title = show_title,
            thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
            summary = show_summary
            )
        )

    #add a way to clear bookmarks list
    oc.add(DirectoryObject(
        key = Callback(ClearBookmarks),
        title = "Clear Bookmarks",
        thumb = R(ICON_QUEUE),
        summary = "CAUTION! This will clear your entire bookmark list!"
        )
    )

    return oc

######################################################################################
# Takes query and sets up a http request to return and create objects from results

def wrap_in_html(content):
    return "<html><head></head><body>" + content + "</body></html>"


def clean_response_markup(request):
    request = "" + request[1:-1]
    req_array = request.split("\\n")
    a = ""
    for item in req_array:
        item = item.strip().replace("\"", "'").replace("\\", "")
        a += item
    return a

@route(PREFIX + "/search")
def Search(query):

    oc = ObjectContainer(title1 = query)

    #setup the search request url
    request_url = BASE_URL + "/index.php?ajax=anime&do=search&s=" + query
    #do http request for search data
    response_content = HTTP.Request(request_url, values={}, headers={'referer': "http://rawranime.tv"}).content
    page_data = HTML.ElementFromString(wrap_in_html(clean_response_markup(response_content)))

    for each in page_data.xpath("//a"):
        show_url = BASE_URL + each.xpath(".//@href")[0]
        show_number = show_url.split("/anime/")[1].split("-")[0]
        show_title = each.xpath(".//div[@class='quicksearch-title']/text()")[0].strip()
        try:
            show_subtitle = each.xpath(".//div[@class='quicksearch-subtitle']/text()")[0].strip()
        except:
            show_subtitle = ""
        show_thumb = "http://static5.rawranime.tv/images/anime/" + show_number + "/image-small.jpg"
        try:
            show_summary = each.xpath(".//div[@class='quicksearch-synopsis']/text()")[0]
        except:
            show_summary = ""

        oc.add(DirectoryObject(
            key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
            title = show_title,
            tagline = show_subtitle,
            thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
            summary = show_summary
            )
        )

    #check for zero results and display error
    if len(oc) < 1:
        Log ("No shows found! Check search query.")
        return ObjectContainer(header="Error", message="Nothing found! Try something less specific.")

    return oc

######################################################################################
# Creates latest episode objects from the front page

@route(PREFIX + "/latestcategory") # this is the recent uploads. TODO pagination -- this is only the first page.
def LatestCategory(title):
    Log("Entered Latest Category")
    oc = ObjectContainer(title1 = title)
    page_data = HTML.ElementFromURL(BASE_URL + "/recent")

    for each in page_data.xpath("//div[@class='ep ']"):
        Log(each.xpath(".//a[@class='ep-title']/text()"))
        ep_title = ""
        for item in each.xpath(".//a[@class='ep-title']/text()"):
            if not(item == "\n" or item == ""):
                ep_title += item
        if ep_title == "":
            ep_title += "Episode"
        ep_title += " - " + each.xpath(".//div[@class='ep-number']/text()")[0].strip()
        Log(ep_title)
        ep_url = BASE_URL + each.xpath(".//a[@class='ep-bg']/@href")[0].strip()
        Log(ep_url)
        Log(each.xpath(".//a[@class='ep-bg']/@style"))
        ep_thumb = "http:" + each.xpath(".//a[@class='ep-bg']/@style")[0].split('"').split("&quot;")[1]
        Log(ep_thumb)
        ep_release_date = each.xpath(".//div[@class='ep-airtimes']/span/text()")[0]
        Log(ep_release_date)

        oc.add(PopupDirectoryObject(
            key = Callback(GetMirrors, ep_url = ep_url),
            title = ep_title,
            thumb = R(ICON_COVER)
            )
        )

    #check for results and display an error if none
    if len(oc) < 1:
        Log ("No shows found! Check xpath queries.")
        return ObjectContainer(header="Error", message="Error! Please let TehCrucible know, at the Plex forums.")

    return oc


######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")
def ShowCategory(title, category):

    oc = ObjectContainer(title1 = title)
    page_data = HTML.ElementFromURL(BASE_URL + category)

    for each in page_data.xpath("//tr[contains(@class, 'list ')]"):

        show_url = each.xpath("./td[@class='animetitle']/a/@href")[0]
        show_title = each.xpath("./td[@class='animetitle']/a/text()")[0].strip()
        show_thumb = BASE_URL + each.xpath("./td//img/@data-original")[0]

        oc.add(DirectoryObject(
            key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
            title = show_title,
            thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
            summary = "Watch " + show_title + " in HD now from rawrANIME.tv!"
            )
        )

    #check for results and display an error if none
    if len(oc) < 1:
        Log ("No shows found! Check xpath queries.")
        return ObjectContainer(header="Error", message="Error! Please let TehCrucible know, at the Plex forums.")

    return oc

######################################################################################
# Creates an object for every 30 episodes (or part thereof) from a show url

@route(PREFIX + "/pageepisodes")
def PageEpisodes(show_title, show_url):

    oc = ObjectContainer(title1 = show_title)
    page_data = HTML.ElementFromURL(show_url)
    show_thumb = "http:" + page_data.xpath("//div[@id='anime-info-listimage']/@style")[0].split('"').split("&quot;")[1]
    show_ep_count = len(page_data.xpath("//div[@class='ep ']"))
    show_summary = ""
    for line in page_data.xpath("//div[@id='anime-info-synopsis']//text()"):
        if len(line.strip()) > 0 :
            show_summary += line.strip() + "\n"
    eps_list = page_data.xpath("//div[@class='ep ']")

    #set a start point and determine how many objects we will need
    offset = 0
    rotation = (show_ep_count - (show_ep_count % 30)) / 30

    #add a directory object for every 30 episodes
    while rotation > 0:

        start_ep  = offset
        end_ep = offset + 30
        start_ep_title = extract_episode_title(eps_list[start_ep])
        end_ep_title = extract_episode_title(eps_list[end_ep - 1])

        oc.add(DirectoryObject(
            key = Callback(ListEpisodes, show_title = show_title, show_url = show_url, start_ep = start_ep, end_ep = end_ep),
            title = "Episodes " + start_ep_title + " - " + end_ep_title,
            thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
            summary = show_summary
            )
        )

        offset += 30
        rotation = rotation - 1

    #if total eps is divisible by 30, add bookmark link and return
    if (show_ep_count % 30) == 0:

        #provide a way to add or remove from favourites list
        oc.add(DirectoryObject(
            key = Callback(AddBookmark, show_title = show_title, show_url = show_url),
            title = "Add Bookmark",
            summary = "You can add " + show_title + " to your Bookmarks list, to make it easier to find later.",
            thumb = R(ICON_QUEUE)
            )
        )
        return oc

    #else create directory object for remaining eps
    else:

        start_ep = offset
        end_ep = (offset + (show_ep_count % 30))
        start_ep_title = extract_episode_title(eps_list[start_ep])
        end_ep_title = extract_episode_title(eps_list[end_ep - 1])

        oc.add(DirectoryObject(
            key = Callback(ListEpisodes, show_title = show_title, show_url = show_url, start_ep = offset, end_ep = offset + (show_ep_count % 30)),
            title = "Episodes " + start_ep_title + " - " + end_ep_title,
            thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
            summary = show_summary
            )
        )

        #provide a way to add or remove from favourites list
        oc.add(DirectoryObject(
            key = Callback(AddBookmark, show_title = show_title, show_url = show_url),
            title = "Add Bookmark",
            summary = "You can add " + show_title + " to your Bookmarks list, to make it easier to find later.",
            thumb = R(ICON_QUEUE)
            )
        )
        return oc


def extract_episode_title(html_element):
    return html_element.xpath(".//div[@class='ep-number']/text()")[0].strip() + " - " + \
    html_element.xpath(".//a[@class='ep-title']/text()")[0].strip()



######################################################################################
# Returns a list of VideoClipObjects for the episodes with a specified range

@route(PREFIX + "/listepisodes")
def ListEpisodes(show_title, show_url, start_ep, end_ep):

    oc = ObjectContainer(title1 = show_title)
    page_data = HTML.ElementFromURL(show_url)
    eps_list = page_data.xpath("//div[@class='ep ']")

    for each in eps_list[int(start_ep):int(end_ep)]:
        ep_url = each.xpath(".//a[@class='ep-bg']/@href")[0].strip()
        ep_title = "Episode " + extract_episode_title(each)

        oc.add(PopupDirectoryObject(
            key = Callback(GetMirrors, ep_url = ep_url),
            title = ep_title,
            thumb = R(ICON_COVER)
            )
        )

    return oc

######################################################################################
# Returns a list of VideoClipObjects for each mirror, with video_id tagged to ep_url

@route(PREFIX + "/getmirrors")
def GetMirrors(ep_url):

    oc = ObjectContainer()
    page_data = HTML.ElementFromURL(ep_url)

    for each in page_data.xpath("//if/div[contains(@class, 'mirror')]"):
        video_type = each.xpath("./div/div/@class")[0].split("_trait")[0].upper()
        video_quality = each.xpath("./div/div/@class")[1].split("_trait")[0].upper().replace("_"," ")
        video_id = each.xpath("./@rn")[0]
        video_url = 'http:' + String.Quote(ep_url.split(':',1)[1], usePlus=False) + "??" + video_id
        video_thumb = BASE_URL + each.xpath("./img/@src")[0]
        video_host = each.xpath("./text()")[2].strip().upper()
        video_title = video_type + " " + video_quality + " " + video_host

        oc.add(VideoClipObject(
            url = video_url,
            title = video_title,
            thumb = Callback(GetThumb, ep_url = ep_url)
            )
        )

    return oc


######################################################################################
# Get episode thumbnails from the ep_url

@route(PREFIX + "/getthumb")
def GetThumb(ep_url):

    ep_data = HTML.ElementFromURL(ep_url)
    find_thumb = BASE_URL + ep_data.xpath("//div[contains(@class, 'selected')]/img/@src")[0]

    try:
        data = HTTP.Request(find_thumb, cacheTime=CACHE_1MONTH).content
        return DataObject(data, 'image/png')
    except:
        return Redirect(R(ICON_COVER))

######################################################################################
# Adds a show to the bookmarks list using the title as a key for the url

@route(PREFIX + "/addbookmark")
def AddBookmark(show_title, show_url):

    Dict[show_title] = show_url
    Dict.Save()
    return ObjectContainer(header=show_title, message='This show has been added to your bookmarks.')

######################################################################################
# Clears the Dict that stores the bookmarks list

@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

    Dict.Reset()
    return ObjectContainer(header="My Bookmarks", message='Your bookmark list has been cleared.')
