# -*- coding: utf-8 -*-
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import copy

my_str = input("Search: ")

new = my_str.replace(' ', '%20')

my_url = 'https://www.imdb.com/find?q=' + new + '&s=tt&ttype=ft&ref_=fn_ft'

# create a connection and download web-page
uClient = uReq(my_url)
# store html
page_html = uClient.read()
uClient.close()
#html parsing
page_soup = soup(page_html, "html.parser")

#grabs each movie url
movies = page_soup.findAll("td", {"class":"result_text"})

# remove movies that don't contain the string 
for movie in movies:
    if my_str.lower() not in movie.text.lower():
        movies.remove(movie)

# remove movies in development
for movie in movies:
    temp = copy.copy(movie)
    temp.a.decompose()
    if "in development" in temp.text or temp.text.strip() == "":
        movies.remove(movie)

# stores only movie pages urls from results page html
movie_urls = []

for movie in movies:
    movie_urls.append("https://www.imdb.com" + movie.a["href"])

# store data in text file
filename = my_str.lower().title().replace(" ", "") + ".txt"
f = open(filename, "w", encoding='utf-8')

print("\nWriting " + filename + " file.....\nPlease wait until finished (may take a few minutes)\n")

# loop over found URLs
for url in movie_urls:
    
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    # relevant data
    data = page_soup.find("div", {"id":"title-overview-widget"})

    # movie title
    title_container = data.find("h1")
    if title_container.span is not None:
        title_container.span.decompose()
        title = title_container.text.strip()
    else:
        title = ''
        
    # extract movie header subtext
    subtext = data.find("div", {"class":"subtext"})
    
    genres = []
    duration = ''
    
    if subtext is not None:
        # extract genres
        links = subtext.select("a[href*=genres]")
        for link in links:
            genres.append(link.text)
        genres = ", ".join(genres)

        # extract movie duration
        if subtext.time is not None:
            duration = duration + subtext.time.text.strip()
    
    summary = data.find("div", {"class":"plot_summary"})
    
    # credits
    credits_container = summary.findAll("div", {"class":"credit_summary_item"})
    
    # remove non Stars or Directors
    matches = ["Director", "Directors", "Star", "Stars"]
    for credit in credits_container:
        if any(x in credit.text for x in matches) == False:
            credits_container.remove(credit)
    
    # director/s
    if(credits_container):
        directors_container = credits_container[0].select("a[href*=name]")
        directors = []
        for director in directors_container:
            directors.append(director.text)
        directors = ", ".join(directors)
    
    # star/s
    if len(credits_container) > 1:
        stars_container = credits_container[1].select("a[href*=name]")
        stars = []
        for star in stars_container:
            stars.append(star.text)
        stars = ", ".join(stars)
    else: stars = ''
    
    # write data in file
    f.write(title + " | " + genres + " | " + duration + " | " + directors + " | " + stars + "\n")


# close file 
f.close()

# using input for keeping window open
k = input(filename + " file has completed successfully")