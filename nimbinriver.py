from flask import Flask, render_template
import csv
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    # Read the CSV file and get the most recent, second most recent, and highest in the last 24 hours
    with open('river_height_data.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header
        rows = list(csv_reader)
    if len(rows) >= 2:
        most_recent = rows[-1]
        second_most_recent = rows[-2]
    elif len(rows) == 1:
        most_recent = rows[0]
        second_most_recent = None
    else:
        most_recent = second_most_recent = None
    # Calculate the highest in the last 24 hours
    highest_last_24h = None
    twenty_four_hours_ago = datetime.now() - timedelta(days=1)
    for row in rows:
        row_date = datetime.strptime(row[1] + ' ' + row[2], '%Y-%m-%d %H:%M')
        if row_date > twenty_four_hours_ago:
            if highest_last_24h is None or float(row[3]) > float(highest_last_24h[3]):
                highest_last_24h = row
    # Get the date and time of the last update
    last_update = datetime.strptime(most_recent[1] + ' ' + most_recent[2], '%Y-%m-%d %H:%M') if most_recent else 'N/A'
    # Render the data using a template and return it
    return render_template('template.html', most_recent=most_recent, second_most_recent=second_most_recent, highest_last_24h=highest_last_24h, last_update=last_update)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')