import os
import requests
import pandas as pd
import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get the API key from the environment variables
API_KEY = os.getenv('DANELFIN_API_KEY')
BASE_URL = 'https://apirest.danelfin.com/ranking'

# Validate API Key
if not API_KEY:
    raise ValueError("API key not found. Please set the DANELFIN_API_KEY environment variable.")

def get_all_stock_data(market='USA', limit=100, date=None, ticker=None, scores=None):
    """
    Fetches stock data from the Danelfin API.

    Args:
        market (str): The market to fetch data for ('USA' or 'europe').
        limit (int): The number of records to retrieve.
        date (str): The date in 'YYYY-MM-DD' format.
        ticker (str): The stock ticker to fetch data for.
        scores (dict): A dictionary of score filters (e.g., {'aiscore': 10}).

    Returns:
        dict: JSON response from the API, or None if an error occurs.
    """
    if not date and not ticker:
        raise ValueError("At least one of 'date' or 'ticker' must be specified.")

    valid_markets = ['USA', 'europe']
    if market not in valid_markets:
        raise ValueError(f"Invalid market: {market}. Valid options are: {valid_markets}")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError(f"Limit must be a positive integer. Received: {limit}")

    headers = {'x-api-key': API_KEY}
    params = {'market': market, 'limit': limit, 'date': date, 'ticker': ticker}

    if scores:
        for key, value in scores.items():
            if key not in ['aiscore', 'fundamental', 'technical', 'sentiment']:
                raise ValueError(f"Invalid score type: {key}.")
            if not (1 <= value <= 10):
                raise ValueError(f"Score value must be between 1 and 10 for {key}.")
            params[key] = value

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        if response.headers.get('Content-Type') == 'application/json':
            logger.info("Data fetched successfully.")
            return response.json()
        else:
            logger.error("Unexpected response format.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

def save_to_excel(data, filename="stocks_data.xlsx"):
    """
    Saves the provided data to an Excel file.

    Args:
        data (list or dict): The data to save.
        filename (str): The name of the Excel file.

    Returns:
        None
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        final_filename = filename.replace(".xlsx", f"_{timestamp}.xlsx")
        df = pd.DataFrame(data)
        df.to_excel(final_filename, index=False)
        logger.info(f"Data saved to {final_filename}")
    except Exception as e:
        logger.error(f"Error saving data to Excel: {e}")

def main():
    """
    Main function to fetch stock data and save it to an Excel file.
    """
    logger.info("Starting data retrieval process...")
    stock_data = get_all_stock_data(market='USA', limit=100, date='2024-01-02', scores={'aiscore': 10})
    if stock_data:
        save_to_excel(stock_data)
    else:
        logger.error("No data to save.")

if __name__ == "__main__":
    main()
