# Required libraries
import requests
from bs4 import BeautifulSoup
import datetime
import time
import csv
import os
import subprocess
# Constants
URL = "http://www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDN60140.html"
SCRAPING_INTERVAL = 60  # in seconds
CSV_FILE = 'river_height_data.csv'
# Check if CSV file already exists, if not, create it with headers
if not os.path.isfile(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Station Name", "Date", "Time", "Height"])
# Keep track of the last height to avoid duplicates
last_height = None
# Update scrape_river_data function according to new requirements
def scrape_river_data(last_height):
    # Set up a user-agent to mimic a web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # Perform the web request with the user-agent
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find 'Goolmangar Ck at Nimbin' row in the table
    target_text = 'Goolmangar Ck at Nimbin'
    # Find the table containing the data. We assume the structure is <table> with <tr> and <td>
    table = soup.find_all('table')
    goolmangar_row = None
    for tbl in table:
        for row in tbl.find_all('tr'):
            cells = row.find_all('td')
            if cells and target_text in cells[0].text.strip():
                goolmangar_row = cells
                break
        if goolmangar_row:
            break
    if goolmangar_row is None:
        print(f"Could not find data for {target_text.strip()}.")
        return last_height  # Return the last height to maintain state
    # Extract the station name (first column), date (second column) and height (third column)
    station_name = goolmangar_row[0].text.strip()
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    # Adjust to Sydney timezone
    sydney_timezone = datetime.timezone(datetime.timedelta(hours=11))
    time_str = datetime.datetime.now(sydney_timezone).strftime('%H:%M')
    height_str = goolmangar_row[2].text.strip()
    # Only write to the CSV file if the height has changed from the last recorded height
    if last_height is None or last_height != height_str:
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([station_name, date_str, time_str, height_str])
        last_height = height_str  # Update the last recorded height
    return station_name, date_str, time_str, height_str, last_height
# Start the Flask app from nimbinriver.py in a separate process
subprocess.Popen(['python', 'nimbinriver.py'])
# Call the scrape_river_data function periodically
while True:
    station_name, date, scraped_time, height, last_height = scrape_river_data(last_height)
    if station_name is None or date is None or scraped_time is None or height is None:
        print("Failed to scrape data. Retrying after delay...")
    else:
        print(f"Data scraped for {station_name} on {date} at {scraped_time}: River height is {height}.")
    time.sleep(SCRAPING_INTERVAL)