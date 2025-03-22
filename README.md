# Bitcoin Investment Calculator

A Flask-based web application that calculates Bitcoin investment returns using dollar-cost averaging (DCA). Users can input a start date, end date, investment amount, and period (in weeks) to see historical investment performance and current value based on real-time and historical Bitcoin prices.

## Features

- **Dynamic Interface**: Initially displays only a form; results appear after calculation without page refresh.
- **Historical Data**: Fetches Bitcoin prices from CoinMarketCap for past dates.
- **Current Price**: Retrieves real-time Bitcoin prices from CoinGecko API.
- **Investment Tracking**: Shows total invested, BTC accumulated, current value, and profit/loss percentage.
- **JSON Storage**: Saves calculation results to a JSON file in `static/json/`.
- **Responsive Design**: Works on desktop and mobile with a clean, animated UI.
- **Bulgarian Language Support**: Interface and messages in Bulgarian.

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: CoinGecko (current prices), CoinMarketCap (historical prices)
- **Libraries**: requests, lxml, tabulate, json

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/CvetelinStoimenov/Crypto_Investment_Calculator_API.git
   cd Crypto_Investment_Calculator_API
   ```

2. **Set Up a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000/`.

## Requirements

Create a `requirements.txt` file with:
```
Flask==2.3.2
requests==2.31.0
lxml==5.1.0
tabulate==0.9.0
```

## Project Structure

```
Crypto_Investment_Calculator_API/
│
├── static/
│   ├── json/               # Stores investment_results.json
│   ├── style.css          # CSS styling
│   └── script.js          # JavaScript for dynamic behavior
│
├── templates/
│   └── index.html         # Main HTML template
│
├── app.py                 # Flask application
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## Usage

1. **Input Data**:
   - **Начална дата (Start Date)**: Choose the start date for your investment.
   - **Крайна дата (End Date)**: Choose the end date.
   - **Сума за инвестиция на период (Amount)**: Enter the amount to invest per period (in USD).
   - **Периодичност (Period in Weeks)**: Enter the investment frequency in weeks.

2. **Calculate**:
   - Click the "Изчисли" button to process the data.

3. **View Results**:
   - The form disappears, and a detailed results container appears with:
     - Current Bitcoin price
     - Average purchase price
     - Total BTC accumulated
     - Total invested
     - Current value
     - Profit/loss percentage
     - Investment history table

4. **Reset**:
   - Click "Новo Изчисление" to return to the form for a new calculation.

## Example Output

After submitting:
- **Input**: Start Date: 2025-03-01, End Date: 2025-03-15, Amount: $23,436, Period: 1 week
- **Result** (sample JSON saved to `static/json/investment_results.json`):
  ```json
  {
      "average_purchase_price": 85501.83,
      "current_price": 84125,
      "current_value": 69137.47,
      "investment_history": [
          ["2025-03-01", "$86031.91", "0.27225944 BTC"],
          ["2025-03-08", "$86154.59", "0.27187176 BTC"],
          ["2025-03-15", "$84343.11", "0.27771089 BTC"]
      ],
      "investment_status": "ЗАГУБА",
      "profit_loss_percentage": -1.61,
      "total_btc": 0.82184209,
      "total_invested": 70269
  }
  ```

## Notes

- **API Reliability**: Dependent on CoinMarketCap and CoinGecko availability. Historical data XPath may need updates if CoinMarketCap changes its structure.
- **Date Limitation**: Historical data only available up to the current date (March 22, 2025, as of last update).
- **Error Handling**: Basic client-side validation and error messages included.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (create one if needed).

## Future Improvements

- Add caching for API calls
- Implement more robust error handling
- Add data visualization (e.g., charts)
- Support multiple cryptocurrencies
- Add user authentication

---

Created by Cvetelin Stoimenov on March 22, 2025.