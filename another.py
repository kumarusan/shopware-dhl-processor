from flask import Flask, render_template, request, send_file
import pandas as pd
import re

app = Flask(__name__)

# Function to split street and house number
def split_street_and_number(address):
    # Use regex to separate street name and house number
    match = re.match(r"(.*?)\s+(\d+)$", address)
    if match:
        street = match.group(1).strip()
        house_number = match.group(2).strip()
    else:
        street = address
        house_number = ""
    return street, house_number

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if a file was uploaded
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]

        if file.filename == "":
            return "No file selected", 400

        if file:
            try:
                # Try multiple encodings to read the CSV file
                encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
                df = None

                for encoding in encodings:
                    try:
                        file.seek(0)  # Reset file pointer
                        df = pd.read_csv(file, encoding=encoding)
                        break  # Stop if the file is successfully read
                    except UnicodeDecodeError:
                        continue  # Try the next encoding

                if df is None:
                    return "Failed to read the CSV file. Unsupported encoding.", 400

                # Extract street and house number from shipping_address_street
                df["RECV_STREET"], df["RECV_HOUSENUMBER"] = zip(*df["shipping_address_street"].apply(split_street_and_number))

                # Process the data (adjust column names as needed)
                output_df = pd.DataFrame({
                    "SEND_NAME1": "Tintenflash",
                    "SEND_NAME2": "",
                    "SEND_STREET": "Rheinstr.",
                    "SEND_HOUSENUMBER": "11",
                    "SEND_PLZ": "14513",
                    "SEND_CITY": "Teltow",
                    "SEND_COUNTRY": "DEU",
                    "SEND_EMAIL": "info@tintenflash.de",
                    "RECV_NAME1": df["customer_firstname"] + " " + df["customer_lastname"],
                    "RECV_NAME2": df["shipping_address_company"],
                    "RECV_EMAIL": df["customer_email"],
                    "RECV_STREET": df["RECV_STREET"],
                    "RECV_HOUSENUMBER": df["RECV_HOUSENUMBER"],
                    "RECV_PLZ": df["shipping_address_zipcode"],
                    "RECV_CITY": df["shipping_address_city"],
                    "RECV_COUNTRY": df["shipping_address_country_id"],
                    "PRODUCT": "PAK05.DEU",
                    "COUPON": "",
                })


                # Save the processed data to a new CSV file
                output_file_path = "./another_processed_output.csv"
                output_df.to_csv(output_file_path, index=False, encoding='utf-8')

                # Send the file to the user for download
                return send_file(output_file_path, as_attachment=True)

            except Exception as e:
                return f"An error occurred: {str(e)}", 500

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=8004)