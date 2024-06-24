import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime
import io
import base64
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Initialize the database
def init_db():
    conn = sqlite3.connect('price_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            price REAL NOT NULL,
            target_price REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call the init_db function to create the database table
init_db()

# Database connection
def get_db_connection():
    conn = sqlite3.connect('price_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_data(url):
    conn = get_db_connection()
    query = "SELECT date, price FROM prices WHERE url=?"
    df = pd.read_sql_query(query, conn, params=(url,))
    df['date'] = pd.to_datetime(df['date'])
    conn.close()
    return df

def calculate_average_price(df):
    return df['price'].mean()

def best_time_to_buy(df):
    min_price_date = df.loc[df['price'].idxmin()]['date']
    return min_price_date

def predict_future_prices(df, days_ahead=30):
    if df.shape[0] <= 1:
        print("Not enough data for prediction.")  # Debug print
        future_dates = pd.date_range(start=df.index.max(), periods=days_ahead + 1)[1:]
        future_prices = [df['price'].iloc[0]] * days_ahead
        future_df = pd.DataFrame({'date': future_dates, 'predicted_price': future_prices})
        return future_df

    df = df.set_index('date')
    df['days'] = (df.index - df.index.min()).days
    X = df[['days']].values
    y = df['price'].values

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.arange(df['days'].max() + 1, df['days'].max() + days_ahead + 1).reshape(-1, 1)
    future_prices = model.predict(future_days)

    future_dates = pd.date_range(start=df.index.max(), periods=days_ahead + 1)[1:]
    future_df = pd.DataFrame({'date': future_dates, 'predicted_price': future_prices})
    return future_df

def fetch_current_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Try multiple selectors to find the price
    selectors = [
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#corePriceDisplay_desktop_feature_div .a-price-whole"
    ]

    price = None
    for selector in selectors:
        price_tag = soup.select_one(selector)
        if price_tag:
            price = price_tag.get_text().strip()
            # Remove currency symbols and commas
            price = price.replace('₹', '').replace(',', '').strip()
            try:
                price = float(price)
                break
            except ValueError:
                price = None

    if price is not None:
        return price

    print("Price tag not found.")  # Debug print
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    url = request.form['url']
    target_price = request.form['target_price']

    if not url or not target_price:
        flash('All fields are required.')
        print("All fields are required.")
        return redirect(url_for('index'))

    try:
        target_price = float(target_price)
    except ValueError:
        flash('Invalid target price format.')
        print("Invalid target price format.")
        return redirect(url_for('index'))

    current_price = fetch_current_price(url)
    print(f"Fetched current price: {current_price}")  # Debug print
    if current_price is None:
        flash('Failed to fetch the current price. Please try again.')
        print("Failed to fetch the current price.")
        return redirect(url_for('index'))

    conn = get_db_connection()
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute('INSERT INTO prices (url, price, target_price, date) VALUES (?, ?, ?, ?)',
                 (url, current_price, target_price, date))
    conn.commit()
    conn.close()

    flash(f'Tracking price for {url} at target price ₹{target_price}')
    print(f"Redirecting to analyze page with URL: {url}")  # Debug print
    return redirect(url_for('analyze', url=url))

@app.route('/analyze')
def analyze():
    url = request.args.get('url')
    df = fetch_data(url)
    if df.empty:
        flash('No data found for the provided URL.')
        print("No data found for the provided URL.")  # Debug print
        return redirect(url_for('index'))

    avg_price = calculate_average_price(df)
    best_time = best_time_to_buy(df)
    future_df = predict_future_prices(df)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], marker='o', linestyle='-', label='Actual Prices')
    plt.plot(future_df['date'], future_df['predicted_price'], marker='x', linestyle='--', color='red', label='Predicted Prices')
    plt.title('Price Trend')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    stats_text = f"Average Price: ₹{avg_price:.2f}<br>Best Time to Buy: {best_time.strftime('%Y-%m-%d')}"

    return render_template('analysis.html', img_data=img_data, stats_text=stats_text)

if __name__ == '__main__':
    app.run(debug=True)
