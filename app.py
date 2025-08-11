from flask import Flask, redirect, render_template, url_for, make_response
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

@app.route('/projects')
def projects():
    return render_template('projects.html')

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
    plt.bar(scraped_data['title'], scraped_data['price'], color='#8d9b8a')
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

@app.route('/pie')
def pie_chart():
    if scraped_data.empty:
        return redirect('/scrape')
    
    # Create availability categories for pie chart
    availability_counts = scraped_data['availability'].value_counts()
    
    plt.figure(figsize=(10, 10))
    plt.pie(availability_counts.values, labels=availability_counts.index, autopct='%1.1f%%', 
            colors=['#8d9b8a', '#d4a574', '#b08968', '#c7a882'])
    plt.title('Book Availability Distribution', fontsize=14)
    
    pie_chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pie_chart.png')
    plt.tight_layout()
    plt.savefig(pie_chart_path)
    plt.close()

    return render_template('pie_chart.html', chart_url=url_for('static', filename='pie_chart.png'))

@app.route('/export_csv')
def export_csv():
    if scraped_data.empty:
        return redirect('/scrape')
    
    # Create CSV response
    csv_data = scraped_data.to_csv(index=False)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=books_data.csv'
    
    return response

@app.route('/export_gilson_csv')
def export_gilson_csv():
    gilson_df = pd.read_csv('ws_csv_files/GilsonPipettes.csv')
    
    # Create CSV response
    csv_data = gilson_df.to_csv(index=False)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=gilson_pipettes.csv'
    
    return response


@app.route('/gilson')
def gilson():
    gilson_df = pd.read_csv('ws_csv_files/GilsonPipettes.csv')
    
    return render_template('gilson.html', tables=[gilson_df.to_html(classes='table table-striped', index=False)])

@app.route('/gaming_mouse')
def gaming_mouse():
    mouse_df = pd.read_csv('ws_csv_files/GamingMouseList.csv')

    return render_template('gaming_mouse.html', tables=[mouse_df.to_html(classes='table table-striped', index=False)])

@app.route('/gaming_laptop')
def gaming_laptop():
    laptop_df = pd.read_csv('ws_csv_files/GamingLaptopsList.csv')

    return render_template('gaming_laptop.html', tables=[laptop_df.to_html(classes='table table-striped', index=False)])

@app.route('/export_mouse_csv')
def export_mouse_csv():
    mouse_df = pd.read_csv('ws_csv_files/GamingMouseList.csv')
    
    csv_data = mouse_df.to_csv(index=False)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=gaming_mouse_list.csv'
    
    return response

@app.route('/export_laptop_csv')
def export_laptop_csv():
    laptop_df = pd.read_csv('ws_csv_files/GamingLaptopsList.csv')
    
    csv_data = laptop_df.to_csv(index=False)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=gaming_laptop_list.csv'
    
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')