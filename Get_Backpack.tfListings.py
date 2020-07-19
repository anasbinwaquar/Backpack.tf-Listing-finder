from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv

def GetListings(url: str, session,fs,fb):
	source= session.get(url)
	soup = BeautifulSoup(source.content, 'html.parser')
	listing=soup.findAll("ul",{"class":"media-list"})
	if(len(listing)==1):
		if(listing[0].div.div["data-listing_intent"]=='sell'):
			all_sellers=listing[0]
		elif(listing[0].div.div["data-listing_intent"]=='buy'):
			all_buyers=listing[0]
	else:
		if(listing[0].div.div["data-listing_intent"]=='sell'):
			all_sellers=listing[0]
			all_buyers=listing[1]
		elif(listing[0].div.div["data-listing_intent"]=='buy'):
			all_buyers=listing[0]
			all_sellers=listing[1]		
	i=0
	item_name=list()
	seller_name=list()
	item_price=list()
	profile_link=list()
	headers = "item_name, seller_name, item_price, profile_link\n"
	try:
		for seller in all_sellers.select('.listing > div.listing-item'): 
			item_name.append(seller.div["title"])	#product name
			seller_name.append(seller.div["data-listing_name"])		#Seller name
			item_price.append((seller.div["data-listing_price"]).replace(",",''))
			profile_link.append("https://steamcommunity.com/profiles/{}".format(all_sellers.select(".listing> div.listing-body > span > span.user-handle> a")[i]["href"][3:]))
			i+=1
		i=0
		for a,b,c,d in zip(item_name,seller_name,item_price,profile_link):
		    fs.write(a +','+ b +','+ c + ',' +d +'\n' )
	except:
		print("no sellers")	

	item_name.clear()
	seller_name.clear()
	item_price.clear()
	profile_link.clear()
	try:
		for buyer in all_buyers.select('.listing > div.listing-item'): 
			item_name.append(buyer.div["title"])	#product name
			seller_name.append(buyer.div["data-listing_name"])		#Seller name
			item_price.append((buyer.div["data-listing_price"]).replace(",",''))
			profile_link.append("https://steamcommunity.com/profiles/{}".format(all_buyers.select(".listing> div.listing-body > span > span.user-handle> a")[i]["href"][3:]))
			i+=1

		for a,b,c,d in zip(item_name,seller_name,item_price,profile_link):
		    fb.write(a +','+ b +','+ c + ',' +d +'\n' )
	except :
		print("no buyers")
	return 


# THREADING SHIT
async def GetListings_async(urls: list,fs,fb)->list:
	res =[]
	with ThreadPoolExecutor(max_workers=2) as executor:
		with requests.Session() as session:
			loop = asyncio.get_event_loop()
			tasks=[
				loop.run_in_executor(executor,GetListings, *(url,session,fs,fb)) for url in urls
			]
			for response in await asyncio.gather(*tasks):
				res.append(response)
	return res
# Marketplace.tf Graph Parsing
# def Graph_parsing(url):
	
#  MAIN
if __name__ == "__main__":
	urls=list()
	with open('links.csv', 'r',encoding='utf8',errors='ignore') as file:
	    for line in file.readlines():
	    	urls.append(line)
	fs = open("seller" + ".csv", "w",encoding='utf-8')
	fs.truncate()

	fb = open("buyer" + ".csv", "w",encoding='utf-8')
	fs.truncate()
	loop= asyncio.get_event_loop()
	future=asyncio.ensure_future(GetListings_async(urls,fs,fb))
	res=loop.run_until_complete(future)
	print(len(res))

	fs.close()
	fb.close()