# Import required libraries
from flask import Flask, render_template, request, jsonify  # Flask web framework components
from datetime import datetime, timedelta  # For date manipulation
import requests  # For making HTTP requests to APIs
from lxml import html  # For parsing HTML from CoinMarketCap
import json  # For handling JSON data
import os  # For file system operations
import sqlite3  # For SQLite database operations

# Initialize Flask application
app = Flask(__name__)

# Define the database path (local for now, will need adjustment for PythonAnywhere deployment)
DB_PATH = os.path.join(os.getcwd(), "bitcoin_prices.db")

# Function to initialize the SQLite database
def init_db():
    # Establish connection to the database file
    conn = sqlite3.connect(DB_PATH)
    # Create a cursor object to execute SQL commands
    c = conn.cursor()
    # Create 'prices' table if it doesn't exist with 'date' as primary key and 'price' as real number
    c.execute('''CREATE TABLE IF NOT EXISTS prices
                 (date TEXT PRIMARY KEY, price REAL)''')
    # Commit the transaction to save changes
    conn.commit()
    # Close the database connection
    conn.close()
    # Log initialization for debugging
    print("Database initialized with prices table")

# Function to save a Bitcoin price to the database
def save_price_to_db(date, price):
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Insert or replace price for the given date (replaces if date already exists due to primary key)
        c.execute("INSERT OR REPLACE INTO prices (date, price) VALUES (?, ?)", (date, price))
        # Commit the change
        conn.commit()
        # Log the save operation
        print(f"Saved price {price} for {date} to database")
    except Exception as e:
        # Log any errors that occur during database operation
        print(f"Error saving to database: {e}")
    finally:
        # Ensure the connection is closed even if an error occurs
        conn.close()

# Function to retrieve a Bitcoin price from the database
def get_price_from_db(date):
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Query the price for the specified date
        c.execute("SELECT price FROM prices WHERE date = ?", (date,))
        # Fetch the result (single row)
        result = c.fetchone()
        # If a result is found, log and return it
        if result:
            print(f"Found price {result[0]} for {date} in database")
            return result[0]
        # Return None if no price is found
        return None
    except Exception as e:
        # Log any errors during query
        print(f"Error querying database: {e}")
        return None
    finally:
        # Ensure the connection is closed
        conn.close()

# Function to fetch Bitcoin price for a specific date
def get_bitcoin_price_on_date(date_input):
    """Fetch Bitcoin price for the given date, check database first, then CoinMarketCap."""
    # First, try to get the price from the database
    price = get_price_from_db(date_input)
    # If price is found in DB, return it without hitting the API
    if price is not None:
        return price

    # Parse the input date string into a datetime object
    date_obj = datetime.strptime(date_input, "%Y-%m-%d")
    # If the date is in the future, use the current price instead
    if date_obj > datetime.now():
        return get_current_bitcoin_price()  # Avoid fetching historical data for future dates

    # Format date for CoinMarketCap URL (YYYYMMDD)
    formatted_date = date_obj.strftime("%Y%m%d")
    # Construct the URL for CoinMarketCap historical data
    url = f'https://coinmarketcap.com/historical/{formatted_date}/'
    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        # Make HTTP GET request to CoinMarketCap
        response = requests.get(url, headers=headers)
        # Raise an exception if the request fails (e.g., 404, 500)
        response.raise_for_status()
        # Parse the HTML response
        tree = html.fromstring(response.content)
        # Define XPath to extract Bitcoin price from the page
        price_xpath = '//*[@id="__next"]/div[2]/div[2]/div/div[1]/div[3]/div[1]/div[3]/div/table/tbody/tr[1]/td[5]/div'
        # Extract price element
        price = tree.xpath(price_xpath)
        # If price is found, process and save it
        if price:
            # Convert price text to float, removing commas and dollar signs
            price_value = float(price[0].text.strip().replace(',', '').replace('$', ''))
            # Save the fetched price to the database
            save_price_to_db(date_input, price_value)
            return price_value
        else:
            # Log if no price is found on the page
            print(f"No price found for {date_input} on CoinMarketCap")
            return None
    except requests.exceptions.RequestException as e:
        # Log any request-related errors (e.g., network issues)
        print(f"Error fetching data for {date_input}: {e}")
        return None

# Function to fetch the current Bitcoin price
def get_current_bitcoin_price():
    """Fetch the current Bitcoin price, check database first, then CoinGecko."""
    # Use today's date as the key
    today = datetime.now().strftime("%Y-%m-%d")
    # Check if today's price is already in the database
    price = get_price_from_db(today)
    # If found, return the cached price
    if price is not None:
        return price

    # Define CoinGecko API URL for current Bitcoin price
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    try:
        # Make HTTP GET request to CoinGecko
        response = requests.get(url)
        # Raise exception if request fails
        response.raise_for_status()
        # Parse JSON response
        data = response.json()
        # Extract Bitcoin price in USD
        price = data['bitcoin']['usd']
        # Save the current price to the database
        save_price_to_db(today, price)
        return price
    except requests.exceptions.RequestException as e:
        # Log any errors fetching current price
        print(f"Error fetching current Bitcoin price: {e}")
        return None

# Function to generate a list of investment dates
def get_dates_in_range(start_date, end_date, period_weeks):
    """Generate a list of dates between the start and end dates based on the investment period."""
    dates = []
    current_date = start_date
    # Iterate from start_date to end_date, incrementing by period_weeks
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(weeks=period_weeks)
    return dates

# Function to calculate investment details
def calculate_investment(start_date_input, end_date_input, amount, period_weeks):
    """Calculates the investment details based on periodic Bitcoin purchases."""
    # Parse input dates, validate format
    try:
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    # Ensure start date is before end date
    if start_date > end_date:
        raise ValueError("Start date must be before end date.")

    # Generate list of investment dates
    dates = get_dates_in_range(start_date, end_date, period_weeks)
    investment_history = []  # Store each purchase details
    total_invested = 0  # Total USD invested
    total_btc = 0  # Total BTC purchased

    # Process each investment date
    for date in dates:
        price = get_bitcoin_price_on_date(date)
        # Skip if price couldn’t be fetched
        if price is None:
            print(f"Skipping date {date} due to missing price")
            continue
        # Calculate BTC purchased with the given amount
        purchased_btc = amount / price
        total_btc += purchased_btc
        total_invested += amount
        # Add purchase details to history
        investment_history.append([date, f"${price:.2f}", f"{purchased_btc:.8f} BTC"])

    # If no valid purchases were made, return None
    if not investment_history:
        return None

    # Round total BTC to 8 decimal places (BTC precision)
    total_btc = round(total_btc, 8)
    # Calculate average purchase price
    average_purchase_price = round(total_invested / total_btc, 2) if total_btc != 0 else 0
    # Get current Bitcoin price
    current_price = get_current_bitcoin_price()

    # If current price couldn’t be fetched, return None
    if current_price is None:
        return None

    # Calculate current value of total BTC
    current_value = round(total_btc * current_price, 2)
    # Calculate profit or loss
    profit_loss = current_value - total_invested
    # Calculate profit/loss percentage
    profit_loss_percentage = round((profit_loss / total_invested) * 100, 2) if total_invested != 0 else 0
    # Determine investment status (profit or loss)
    investment_status = "ПЕЧАЛБА" if profit_loss > 0 else "ЗАГУБА"

    # Return all calculated values as a tuple
    return (investment_history, total_invested, total_btc, current_price, current_value, 
            profit_loss_percentage, investment_status, average_purchase_price)

# Function to save calculation results to a JSON file
def save_results_to_json(data, filename="investment_results.json"):
    """Save the investment results to a JSON file in the static/json directory."""
    try:
        # Define the directory path for JSON storage
        dir_path = os.path.join(os.getcwd(), "static", "json")
        # Create directory if it doesn’t exist, ignore if it does
        os.makedirs(dir_path, exist_ok=True)
        # Construct full file path
        file_path = os.path.join(dir_path, filename)
        # Write data to JSON file with indentation for readability
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        # Log successful save
        print(f"Резултатите бяха записани в {file_path}")
    except Exception as e:
        # Log any errors during file operation
        print(f"Грешка при записване на JSON файл: {e}")

# Define the main route for the Flask app
@app.route("/", methods=["GET", "POST"])
def index():
    # Handle POST requests (form submission)
    if request.method == "POST":
        try:
            # Extract form data
            start_date_input = request.form["start_date"]
            end_date_input = request.form["end_date"]
            amount = float(request.form["amount"])
            period_weeks = int(request.form["period_weeks"])
            # Log received form data for debugging
            print(f"Received form data: start={start_date_input}, end={end_date_input}, amount={amount}, period={period_weeks}")
            
            # Calculate investment details
            result = calculate_investment(start_date_input, end_date_input, amount, period_weeks)
            # If calculation succeeded, prepare and return response
            if result:
                # Unpack result tuple
                investment_history, total_invested, total_btc, current_price, current_value, profit_loss_percentage, investment_status, average_purchase_price = result
                # Create JSON response data, ensuring numeric values are float for serialization
                response_data = {
                    "investment_history": investment_history,
                    "total_invested": float(total_invested),
                    "total_btc": float(total_btc),
                    "current_price": float(current_price),
                    "current_value": float(current_value),
                    "profit_loss_percentage": float(profit_loss_percentage),
                    "investment_status": str(investment_status),
                    "average_purchase_price": float(average_purchase_price)
                }
                # Save results to JSON file
                save_results_to_json(response_data)
                # Log the response data
                print(f"Returning response: {response_data}")
                # Return JSON response to the client
                return jsonify(response_data)
            else:
                # Return error if calculation failed (e.g., no prices fetched)
                return jsonify({"error": "Не можа да се извлече текущата цена на биткойн или исторически данни"}), 500
        except ValueError as e:
            # Handle invalid input (e.g., date format, non-numeric amount)
            print(f"ValueError in form data: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            # Handle unexpected errors
            print(f"Unexpected POST error: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Handle GET requests by rendering the index.html template
    return render_template("index.html")

# Run the app if executed directly
if __name__ == "__main__":
    # Initialize the database before starting the server
    init_db()
    # Start Flask development server with debug mode enabled
    app.run(debug=True)