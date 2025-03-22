from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import requests
from lxml import html
from tabulate import tabulate

app = Flask(__name__)

def get_bitcoin_price_on_date(date_input):
    """Fetch Bitcoin price for the given date using CryptoCompare API."""
    url = f'https://min-api.cryptocompare.com/data/pricehistorical'
    params = {
        'fsym': 'BTC',
        'tsyms': 'USD',
        'ts': int(datetime.strptime(date_input, '%Y-%m-%d').timestamp())
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['BTC']['USD']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {date_input}: {e}")
        return None

def get_current_bitcoin_price():
    """Fetch the current Bitcoin price using CoinGecko API."""
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['bitcoin']['usd']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current Bitcoin price: {e}")
        return None

def get_dates_in_range(start_date, end_date, period_weeks):
    """Generate a list of dates between the start and end dates based on the investment period."""
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(weeks=period_weeks)
    return dates

def calculate_investment(start_date_input, end_date_input, amount, period_weeks):
    """Calculates the investment details."""
    start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
    dates = get_dates_in_range(start_date, end_date, period_weeks)

    investment_history = []
    total_invested = 0
    total_btc = 0

    for date in dates:
        price = get_bitcoin_price_on_date(date)
        if price:
            purchased_btc = amount / price
            total_btc += purchased_btc
            total_invested += amount
            investment_history.append([date, f"${price:.2f}", f"{purchased_btc:.8f} BTC"])

    total_btc = round(total_btc, 8)

    average_purchase_price = round(total_invested / total_btc, 2) if total_btc != 0 else 0

    current_price = get_current_bitcoin_price()

    if current_price is None:
        return None

    current_value = round(total_btc * current_price, 2)
    profit_loss = current_value - total_invested
    profit_loss_percentage = round((profit_loss / total_invested) * 100,2) if total_invested != 0 else 0
    investment_status = "ПЕЧАЛБА" if profit_loss > 0 else "ЗАГУБА"

    return investment_history, total_invested, total_btc, current_price, current_value, profit_loss_percentage, investment_status, average_purchase_price

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start_date_input = request.form["start_date"]
        end_date_input = request.form["end_date"]
        amount = float(request.form["amount"])
        period_weeks = int(request.form["period_weeks"])

        result = calculate_investment(start_date_input, end_date_input, amount, period_weeks)

        if result:
            investment_history, total_invested, total_btc, current_price, current_value, profit_loss_percentage, investment_status, average_purchase_price = result
            # Ако се използва за JSON отговор
            if request.is_json:
                return jsonify({
                    "investment_history": investment_history,
                    "total_invested": total_invested,
                    "total_btc": total_btc,
                    "current_price": current_price,
                    "current_value": current_value,
                    "profit_loss_percentage": profit_loss_percentage,
                    "investment_status": investment_status
                })
            else:
                # ако заявката е за HTML, връщаме стандартния HTML отговор
                return render_template(
                    "index.html", 
                    investment_history=investment_history, 
                    total_invested=total_invested, 
                    total_btc=total_btc, 
                    current_price=current_price, 
                    current_value=current_value, 
                    profit_loss_percentage=profit_loss_percentage, 
                    investment_status=investment_status,
                    average_purchase_price=average_purchase_price)
        else:
            error_message = "❌ Грешка: Не можа да се извлече текущата цена на биткойн."
            return render_template("index.html", error_message=error_message)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
