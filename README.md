
# Amazon Price Tracker

This project is a web application built with Flask that tracks the prices of products on Amazon. Users can input the URL of an Amazon product and a target price, and the application will track the price over time. The application uses web scraping to fetch the current price, stores the data in a SQLite database, and provides analysis including average price, the best time to buy, and future price predictions using linear regression.


## Features

- Track Amazon product prices by entering the product URL and target price.
- Fetch the current price using web scraping.
- Store price data in a SQLite database.
- Display a graphical analysis of the price trend.
- Predict future prices using linear regression.


## Technologies Used
- Flask
- SQLite
- Pandas
- Matplotlib
- Scikit-learn
- BeautifulSoup
- Requests
- Bootstrap
- dotenv
## Prerequisites
- Python 3.x
- pip (Python package installer)
##  Installation
## Installation

1. Clone the repository:

```bash
  git clone https://github.com/yourusername/amazon-price-tracker.git
  cd amazon-price-tracker

```
2. Create a virtual environment and activate it:

```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
   pip install -r requirements.txt

```

4. Set up environment variables:
Create a .env file in the project root directory and add your Flask secret key:

```bash
   FLASK_SECRET_KEY=your_secret_key

```
5. Initialize the database:

```bash
  python -c "from app import init_db; init_db()"

```
## Running the Application
1. Start the Flask development server:

```bash
  flask run

```
2. Open your browser and navigate to:

```bash
  http://127.0.0.1:5000/

```
## Usage

- Enter the Amazon product URL and your desired target price.
- Submit the form to start tracking the price.
- The application will fetch the current price and  store it in the database.
- You will be redirected to the analysis page where you can see the price trend and predictions.


## Future Improvements
- Implement user authentication to allow users to manage their tracked products.
- Add email notifications when the product price drops below the target price.
- Improve the web scraping logic to handle more Amazon page variations.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
## Acknowledgements

 - Flask: https://flask.palletsprojects.com/
 - Bootstrap: https://getbootstrap.com/
 - BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
