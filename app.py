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
                # Read the uploaded CSV file
                df = pd.read_csv(file)

                # Extract street and house number from shipping_address_street
                df["RECV_STREET"], df["RECV_HOUSENUMBER"] = zip(*df["shipping_address_street"].apply(split_street_and_number))

                # Process the data (adjust column names as needed)
                output_df = pd.DataFrame({
                    "SEND_NAME1": "xyz",
                    "SEND_STREET": "dfgh",
                    "SEND_HOUSENUMBER": "gf3",
                    "SEND_PLZ": "dfghfgh",
                    "SEND_CITY": "ghfgt",
                    "SEND_COUNTRY": "234tr",
                    "RECV_NAME1": df["customer_firstname"] + " " + df["customer_lastname"],
                    "RECV_STREET": df["RECV_STREET"],
                    "RECV_HOUSENUMBER": df["RECV_HOUSENUMBER"],
                    "RECV_PLZ": df["shipping_address_zipcode"],
                    "RECV_CITY": df["shipping_address_city"],
                    "RECV_COUNTRY": df["shipping_address_country_id"],
                    "PRODUCT": "PAECK.DEU",
                    "COUPON": "",
                    "SEND_EMAIL": df["customer_email"]
                })

                # Save the processed data to a new CSV file
                output_file_path = "processed_output.csv"
                output_df.to_csv(output_file_path, index=False)

                # Send the file to the user for download
                return send_file(output_file_path, as_attachment=True)

            except Exception as e:
                return f"An error occurred: {str(e)}", 500

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)