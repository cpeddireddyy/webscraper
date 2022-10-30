import json
import re
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import requests
import textacy.preprocessing

session = HTMLSession()

#Post processing to remove html tags
def clean(string):
    string = textacy.preprocessing.remove.html_tags(string)
    string = re.sub('<|:', '', string)
    return string

def getInformation (profileLink):
    dict = {}

    r = requests.get(profileLink)
    soup = BeautifulSoup(r.text, "lxml")

    #gets field headings
    fields = list(soup.find_all("h2"))
    # Cleans accented names to avoid unicode issues
    cleanedName = clean(textacy.preprocessing.remove.accents(str(fields[3])))
    dict['Name'] = cleanedName
    dict['ProfileURL'] = profileLink
    fields = fields[4:len(fields) - 1]

    #gets the field informaion for a given profile
    details = []
    for val in soup.find_all("h2"):
        if val.nextSibling:
            details.append(val.nextSibling)
    details = details[3:len(details)-1]
    info = []
    for detail in details:
        info.append(clean(str(detail)))

    #Makes a key-val dictionary per profile
    counter = 0
    for field in fields:
        val = clean(str(field))
        # Edge case to make a list for multiple languages rather than one string (Example on next line)
        # BulgarianTurkish --> [Bulgarian, Turkish]
        if val == "Spoken languages":
            splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', info[counter])).split()
            dict[val] = splitted
        else:
            dict[val] = info[counter]
        counter += 1
    print ('Finished scraping', cleanedName)
    return dict


def main():
    url = 'https://eumostwanted.eu'
    website = session.get(url)
    links = website.html.absolute_links
    jsonObjects = []
    dict = {}
    dict['souce_code'] = 'EU_MWL'
    dict['source_name'] = 'Europe Most Wanted List'
    dict['source_url'] = url

    #gets individual profile links from source link
    for link in links:
        profile = str(link)
        edgeCases = ['https://eumostwanted.eu/', 'https://eumostwanted.eu/legal-notice',
                     'https://eumostwanted.eu/enfast']
        if profile.startswith(url) and profile not in edgeCases:
            jsonObjects.append(getInformation(profile))

    dict['profiles'] = jsonObjects
    with open('eumostwanted.json', 'w') as file:
        json.dump(dict, file, indent=4)

main()












