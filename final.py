import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
import random

headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/85.0.4183.102 Safari/537.36', 'Accept-Language': 'en-US'#'zh-CN'
        }
def get_url_list(n):
    linklist=[]
    IDlist = []
    for pagenum in range(1,n):
        r = requests.get('https://store.steampowered.com/search/?ignore_preferences=1&category1=998&os=win&filter=globaltopsellers&page=%d'%pagenum,headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        soups= soup.find_all(href=re.compile(r"https://store.steampowered.com/app/"),class_="search_result_row ds_collapse_flag")
        for i in soups:
            i = i.attrs
            i = i['href']
            link = re.search('https://store.steampowered.com/app/(\d*?)/',i).group()
            ID = re.search('https://store.steampowered.com/app/(\d*?)/(.*?)/', i).group(1)
            linklist.append(link)
            IDlist.append(ID)
        print(str(pagenum)+' pages completed, now '+str(len(linklist)))
    #print(linklist)
    return linklist,IDlist

def getdf(n):#turn the result to df
    linklist,IDlist = get_url_list(n)
    df = pd.DataFrame(list(zip(linklist,IDlist)),
               columns =['Link', 'ID'])
    #print(df)
    return df

def gamename(soup):   #name of game
    try:
        a = soup.find(class_="apphub_AppName")
        k = str(a.string)
    except:
        a = soup.find(class_="apphub_AppName")
        k = str(a.text)
    return k

def taglist(soup):#tag list
    list1=[]
    a = soup.find_all(class_="app_tag")
    for i in a:
        k = str(i.string).replace('	', '').replace('\n', '').replace('\r', '')
        if k == '+':
            pass
        else:
            list1.append(k)
    list1 = str('\n'.join(list1)).split("\n")
    return list1

def gameprice(soup):#price
    try:
        a = soup.findAll(class_="discount_original_price")
        for i in a:
            if re.search('$|free', str(i),re.IGNORECASE):
                a = i
        k = str(a.string).replace('	', '').replace('\n', '').replace('\r', '').replace(' ', '')
    except:
        a = soup.findAll(class_="game_purchase_price price")
        for i in a:
            if re.search('$|free', str(i),re.IGNORECASE):
                a = i
        k = str(a.string).replace('	', '').replace('\n', '').replace('\r', '').replace(' ', '')
    if(re.search('free', k,re.IGNORECASE)):
        return 0
    else:
        return float(k[1:])

def gamerate(soup):#get rating
    a = soup.find(class_="user_reviews_summary_row")
    k = str((a.attrs)['data-tooltip-html'])
    return float(k.split("%")[0])/100

def open_cache(CACHE_FILENAME):
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = []
    return cache_dict
def write_cache(game_json, CACHE_FILENAME):
    dumped_json_cache = json.dumps(game_json, indent=2)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()


def main():
    game_all = {
    #"game_name1":{
    #   "taglist": ["FPG", "Shooter", etc... ],price:0,rate:0
    # }
    #"game_name2":{
    #   "taglist": ["Cartoon", "Colorful", etc... ],price:0,rate:0
    # }
    }
    tag_all = {
        #"tagname1":[game1, game2, ...]
        #"tagname2":[game3, game4, ...]
    }
    price_all = {
        "free":[],
        "0-30":[],
        "30-100":[],
        "100-200":[],
        "more expensive than 200":[]
    }
    rate_all = {
        "0\%-20\%":[],
        "20\%-40\%":[],
        "40\%-60\%":[],
        "60\%-80\%":[],
        "80\%-100\%":[]
    }
    cache = open_cache("cache.json")
    if len(cache) == 0:
        print("No cache file detected, first crawl data from steampower")
        df = getdf(300)
        for url in df['Link']:
            if(len(game_all) >= 5000):
                break
            if(len(game_all)%100 == 0):
                print(len(game_all))
            a = requests.get(url, headers=headers,timeout=10)
            soup = BeautifulSoup(a.text, 'lxml')
            try:
                n = gamename(soup)
                tags = taglist(soup)
                p = gameprice(soup)
                rate = gamerate(soup)
                game_all[n] = {
                    "taglist" : tags,
                    "price":p,
                    "rate":rate
                }
                for tag in tags:
                    if tag in tag_all:
                        tag_all[tag].append(n)
                    else:
                        tag_all[tag] = [n]
                if p == 0:
                    price_all["free"].append(n)
                elif p < 30:
                    price_all["0-30"].append(n)
                elif p < 100:
                    price_all["30-100"].append(n)
                elif p < 200:
                    price_all["100-200"].append(n)
                else:
                    price_all["more expensive than 200"].append(n)
                match int(rate*10):
                    case 0:
                        rate_all["0\%-20\%"].append(n)
                    case 1:
                        rate_all["0\%-20\%"].append(n)
                    case 2:
                        rate_all["20\%-40\%"].append(n)
                    case 3:
                        rate_all["20\%-40\%"].append(n)
                    case 4:
                        rate_all["40\%-60\%"].append(n)
                    case 5:
                        rate_all["40\%-60\%"].append(n)
                    case 6:
                        rate_all["60\%-80\%"].append(n)
                    case 7:
                        rate_all["60\%-80\%"].append(n)
                    case 8:
                        rate_all["80\%-100\%"].append(n)
                    case 9:
                        rate_all["80\%-100\%"].append(n)
                    case 10:
                        rate_all["80\%-100\%"].append(n)
            except:
                continue
        
        write_cache(game_all, "cache.json")
    else:
        game_all = cache
        for n in cache:
            tags = cache[n]["taglist"]
            for tag in tags:
                if tag in tag_all:
                    tag_all[tag].append(n)
                else:
                    tag_all[tag] = [n]
            p = cache[n]["price"]
            if p == 0:
                price_all["free"].append(n)
            elif p < 30:
                price_all["0-30"].append(n)
            elif p < 100:
                price_all["30-100"].append(n)
            elif p < 200:
                price_all["100-200"].append(n)
            else:
                price_all["more expensive than 200"].append(n)
            rate = cache[n]["rate"]
            match int(rate*10):
                case 0:
                    rate_all["0\%-20\%"].append(n)
                case 1:
                    rate_all["0\%-20\%"].append(n)
                case 2:
                    rate_all["20\%-40\%"].append(n)
                case 3:
                    rate_all["20\%-40\%"].append(n)
                case 4:
                    rate_all["40\%-60\%"].append(n)
                case 5:
                    rate_all["40\%-60\%"].append(n)
                case 6:
                    rate_all["60\%-80\%"].append(n)
                case 7:
                    rate_all["60\%-80\%"].append(n)
                case 8:
                    rate_all["80\%-100\%"].append(n)
                case 9:
                    rate_all["80\%-100\%"].append(n)
                case 10:
                    rate_all["80\%-100\%"].append(n)
    while(True):
        print("Welcome to game searching")
        
        while(True):
            try:
                p = float(input("Please give a price of the game that you intend, (0 indicate free game): "))
                break
            except:
                print("Please type a valid number")
        if p == 0:
            game_price = price_all["free"]
        elif p < 30:
            game_price = price_all["free"] + price_all["0-30"]
        elif p < 100:
            game_price = price_all["free"] + price_all["0-30"] + price_all["30-100"]
        elif p < 200:
            game_price = price_all["free"] + price_all["0-30"] + price_all["30-100"] + price_all["100-200"]
        else:
            game_price = price_all["free"] + price_all["0-30"] + price_all["30-100"] + price_all["100-200"] + price_all["more expensive than 200"]
        
        tags = []
        tag = input("Please give a tag that fits the game you want, i.e. FPS, you can also type \"recommend\" if unsure of the game type you want: ")
        if (tag == "recommend"):
            print(random.choices(list(tag_all.keys()),k=3))
        else:
            tags.append(tag)
        while(True):
            tag = input("Please give a tag that fits the game you want, or \"recommend\" for recommendation, if you are finish giving tag, type \"done\": ")
            if(tag == "done"):
                if(len(tags) == 0):
                    print("Please give at least one tag")
                else:
                    break
            elif(tag == "recommend"):
                print(random.choices(list(tag_all.keys()),[len(x[1]) for x in tag_all.items()],k=3))
            else:
                tags.append(tag)
        for tag in tags:
            try:
                game_price = list(set(tag_all[tag]) & set(game_price))
            except:
                print("We done have game type: ",tag," so we skip it for you")

        if(len(game_price) == 0):
            game_price = tag_all[tags[0]]
            print("Sorry, there is no game match for all your requirement. However, we have some recommendation for you: ")
            for i in game_price:
                print(i," :",game_all[i]["price"],"$", end=', ')
        else:
            print("The game we have for you is: ")
            rate_20 = list(set(rate_all["0\%-20\%"]) & set(game_price))
            rate_40 = list(set(rate_all["20\%-40\%"]) & set(game_price))
            rate_60 = list(set(rate_all["40\%-60\%"]) & set(game_price))
            rate_80 = list(set(rate_all["60\%-80\%"]) & set(game_price))
            rate_100 = list(set(rate_all["80\%-100\%"]) & set(game_price))
            if(len(rate_20)!=0):
                print("Game good rating between 0-20% are: ",rate_20)
            if(len(rate_40)!=0):
                print("Game good rating between 20-40% are: ",rate_40)
            if(len(rate_60)!=0):
                print("Game good rating between 40-60% are: ",rate_60)
            if(len(rate_80)!=0):
                print("Game good rating between 60-80% are: ",rate_80)
            if(len(rate_100)!=0):
                print("Game good rating between 80-100% are: ",rate_100)
        next_turn = input("Do you want another search?[Y\\N]: ")
        if(next_turn == "N"):
            break

if __name__ == "__main__":
    main()

