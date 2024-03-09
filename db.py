import psycopg2
import openpyxl

conn = psycopg2.connect(
    host="localhost",
    database="invstodb",
    user="admin",
    password="adminadmin"
)

cur = conn.cursor()

# Create a table
cur.execute("""
    CREATE TABLE IF NOT EXISTS ticker_data (
        datetime TIMESTAMP PRIMARY KEY,
        close FLOAT,
        high FLOAT,
        low FLOAT,
        open FLOAT,
        volume BIGINT,
        instrument TEXT
    )
""")

# Load the XLSX file
workbook = openpyxl.load_workbook('HINDALCO_1D.xlsx')
worksheet = workbook.active

for row in worksheet.iter_rows(min_row=2, values_only=True):
    datetime_value = row[0]
    close_value = row[1]
    high_value = row[2]
    low_value = row[3]
    open_value = row[4]
    volume_value = row[5]
    instrument_value = row[6]

    try:
        cur.execute("""
            INSERT INTO ticker_data (datetime, close, high, low, open, volume, instrument)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (datetime_value, close_value, high_value, low_value, open_value, volume_value, instrument_value))
    except psycopg2.errors.UniqueViolation:
        print(f"Data already exists for datetime: {datetime_value}")
        continue

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()