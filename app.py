from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'table-responsive'})
row = table.find_all('tr')
row_length = len(row)

temp = [] #initiating a list 

for i in range(1, row_length):
	period = row[i].select('td')[0].text
	value = row[i].select('td')[2].text
	temp.append((period,value))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns=('Date','Kurs(IDR)'))

#insert data wrangling here
df['Date'] = pd.to_datetime(df['Date'])
df['Kurs(IDR)'] = df['Kurs(IDR)'].str.replace(',','')
df['Kurs(IDR)'] = df['Kurs(IDR)'].str.replace(' IDR','')
df['Kurs(IDR)'] = df['Kurs(IDR)'].astype('float64')

#Add Saturday & Sunday date
new_daterange= pd.date_range('2022-01-12', '2022-07-11')
df = df.set_index('Date')
df = df.reindex(new_daterange)
df.index.names = ['Date']

#Fill the missing values
df = df.fillna(method='ffill').fillna(method='bfill')

#end of data wranggling 
plt.style.use('ggplot')
plt.rcParams['font.family'] = "serif"
plt.rcParams['font.size'] = 12

@app.route("/")
def index(): 
	
	card_data = f'IDR {df["Kurs(IDR)"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9))
	ax.plot(df.index.values, df['Kurs(IDR)'],color='red')
	plt.xlabel("DATE", fontweight='bold')                           
	plt.ylabel("Kurs(IDR)", fontweight='bold')
	plt.yticks(rotation=45)
	plt.legend(fontsize=12)  
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)