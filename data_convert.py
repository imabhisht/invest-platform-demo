import openpyxl
import csv

# Load the XLSX file
workbook = openpyxl.load_workbook('HINDALCO_1D.xlsx')

# Select the active sheet
worksheet = workbook.active

# Create a CSV file
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    header = ['datetime', 'close', 'high', 'low', 'open', 'volume', 'instrument']
    writer.writerow(header)

    # Write the data rows
    for row in worksheet.iter_rows(min_row=2, values_only=True):
        writer.writerow(row)