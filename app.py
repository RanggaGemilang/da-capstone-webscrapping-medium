from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import re
import numpy as np

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31&sort=boxoffice_gross_us,desc')
soup = BeautifulSoup(url_get.content,"lxml")

#find your right key here
table = soup.find('div', attrs={'class':'lister list detail sub-list'})
row = table.find_all('div', attrs={'class':'lister-item mode-advanced'})

row_length = len(row)

list_metascore = [] #to store the score
list_title = []
list_rating = []
list_vote = []
list_gross = []

for i in range(0,10):
    # 
    meta = str(soup.find_all('div', attrs={'class':'inline-block ratings-metascore'})[i])
    list_metascore.append(re.findall(r'\b\d+\b', meta)[0])

for i in range(0,10):
    products = soup.select(".lister-item.mode-advanced")
    title = products[i].select('a')[1].text
    list_title.append(title)

for i in range(0,10):
    products = soup.select(".lister-item.mode-advanced")
    rating = products[i].select('strong')[0].text
    list_rating.append(rating)

for i in range(0,10):
    products = soup.select(".sort-num_votes-visible")
    votes = products[i].select('span')[1].text
    list_vote.append(votes)

for i in range(0,10):
    products = soup.select(".sort-num_votes-visible")
    gross = products[i].select('span')[4]['data-value']
    list_gross.append(gross) 

temp = list(zip(list_title,list_rating,list_metascore,list_vote,list_gross))

#change into dataframe
df = pd.DataFrame(temp,columns=('Title','Rating','Metascore','Votes','Gross($)'))

#data cleansing
df['Title'] = df['Title'].astype('str')
df['Rating'] = df['Rating'].astype('float64')
df['Metascore'] = df['Metascore'].astype('int64')
df['Votes'] = df['Votes'].str.replace(',','')
df['Votes'] = df['Votes'].astype('int64')
df['Gross($)'] = df['Gross($)'].str.replace(',','')
df['Gross($)'] = df['Gross($)'].astype('int64')

#for rating plot
temp_r = list(zip(list_title,list_rating,list_metascore))
df2 = pd.DataFrame(temp_r,columns=('Title','Rating','Metascore'))
df2['Rating'] = df2['Rating'].str.replace('.','')
df2['Rating'] = df2['Rating'].astype('int64')
df2['Metascore'] = df2['Metascore'].astype('int64')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'${df["Gross($)"].mean().round(0):,.0f}' #be careful with the " and ' 

	# generate gross plot
	df_percent = pd.crosstab(index=df['Title'],columns='Gross($)',values=df['Gross($)'],aggfunc='sum',normalize=True).\
            sort_values(by='Gross($)',ascending=False)*100
	X = df_percent.index[::-1]
	Y = df_percent['Gross($)'][::-1]
	plt.figure(figsize=(20,9))
	plt.barh(X ,Y)
	plt.xlabel("Percentage (%)", fontweight='bold')

	
	# Rendering gross plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# generate votes plot
	df_votes = pd.crosstab(index=df['Title'],columns='Votes',values=df['Votes'],aggfunc='sum',normalize=True).\
            sort_values(by='Votes',ascending=False)*100
	X2 = df_votes.index[::-1]
	Y2 = df_votes['Votes'][::-1]
	plt.figure(figsize=(20,9))
	plt.barh(X2 ,Y2, color='orange')
	plt.xlabel("Percentage (%)", fontweight='bold')

	# Rendering votes plot
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result2 = str(figdata_png)[2:-1] 

	# generate rating plot
	df_rating = df2.groupby('Title').sum()[['Metascore','Rating']].sort_values(by='Rating',ascending=True)
	df_rating.plot.barh(figsize=(20,9))
	plt.xlabel("Rating", fontweight='bold')
	plt.ylabel('')

	# Rendering rating plot
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result3 = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		plot_result2=plot_result2,
		plot_result3=plot_result3)


if __name__ == "__main__": 
    app.run(debug=True)