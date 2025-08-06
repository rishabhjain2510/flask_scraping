from flask import Flask, redirect, render_template, url_for
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

scraped_data = pd.DataFrame()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/scrape')
def scrape_books():
    global scraped_data
    url = 'http://books.toscrape.com/index.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    books=[]
    items = soup.find_all('article', class_='product_pod')

    for item in items:
        title_element = item.find("h3").find("a")
        price_element = item.find('p', class_='price_color')
        availability_element = item.find('p', class_='instock availability')

        title = title_element.get('title') if title_element else 'No title'
        price = price_element.get_text(strip=True) if price_element else 'No price'
        availability = availability_element.get_text(strip=True) if availability_element else 'No availability'
        books.append({
            'title': title,
            'price': price,
            'availability': availability
        })

    scraped_data = pd.DataFrame(books, columns=['title', 'price', 'availability'])

    scraped_data['price'] = scraped_data['price'].str.replace(r'[^\d.]', '', regex=True).astype(float)

    return render_template('index.html', books=scraped_data.to_html(classes='table table-striped', index=False))

@app.route('/bar')
def bar_chart():
    if scraped_data.empty:
        return redirect('/scrape')
    
    plt.figure(figsize=(20, 16))
    plt.bar(scraped_data['title'], scraped_data['price'], color='#14b8a6')
    plt.xlabel('Books', fontsize=14)
    plt.ylabel('Price (£)', fontsize=14)
    plt.title('Book Prices')
    plt.xticks(rotation=90, fontsize=12)
    plt.yticks(fontsize=12)
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'bar_chart.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return render_template('bar_chart.html', chart_url=url_for('static', filename='bar_chart.png'))

@app.route('/gilson')
def gilson():
    gilson_df = pd.read_csv('ws_csv_files/GilsonPipettes.csv')
    
    return render_template('gilson.html', tables=[gilson_df.to_html(classes='table table-striped', index=False)])

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')