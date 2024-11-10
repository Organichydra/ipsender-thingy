import requests
import smtplib
import os
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(filename='ip_change.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get the public IP
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        return None

# Function to send an email notification
def send_email(new_ip):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "@gmail.com"       # Replace with your sender email
    receiver_email = "@gmail.com" # Replace with the receiver's email
    password = "passeord"        # Get the email password from an environment variable

    if not password:
        logging.error("No email password provided. Set the EMAIL_PASSWORD environment variable.")
        return

    subject = "Public IP Address Changed"
    body = f"Your public IP address has changed to: {new_ip}"
    email_message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, email_message)
        logging.info("Email sent successfully.")
    except smtplib.SMTPException as e:
        logging.error(f"Error sending email: {e}")

# Function to check internet connectivity
def check_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Main function
def main():
    # Path to save the last known IP
    ip_file_path = os.path.join(os.path.dirname(__file__), "last_ip.txt")
    last_ip = None

    # Check if the file exists and read the last IP
    if os.path.exists(ip_file_path):
        try:
            with open(ip_file_path, "r") as file:
                last_ip = file.read().strip()
        except IOError as e:
            logging.error(f"Error reading the IP file: {e}")

    while True:
        if check_internet():
            current_ip = get_public_ip()
            if current_ip:
                if current_ip != last_ip:
                    logging.info(f"IP address changed from {last_ip} to {current_ip}.")
                    send_email(current_ip)
                    last_ip = current_ip
                    # Update the saved IP
                    try:
                        with open(ip_file_path, "w") as file:
                            file.write(current_ip)
                        logging.info("Updated the last known IP address.")
                    except IOError as e:
                        logging.error(f"Error writing to the IP file: {e}")
                else:
                    logging.info("No change in IP address.")
            else:
                logging.error("Failed to retrieve the current public IP address.")
            # Sleep for 30 minutes
            time.sleep(1800)
        else:
            logging.warning("No internet connection. Retrying in 1 minute.")
            # Keep checking every minute until internet is restored
            while not check_internet():
                time.sleep(60)
            logging.info("Internet connection restored. Checking IP address.")

if __name__ == "__main__":
    main()
