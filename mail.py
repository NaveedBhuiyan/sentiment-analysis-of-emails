import imaplib
import email
from email.header import decode_header
from transformers import pipeline
from pync import Notifier
import time


#Hugging Face sentiment analysis pipeline
sentiment_analysis = pipeline("sentiment-analysis")


imap_server = "mail.rwth-aachen.de"
email_address = ""
#xu287400
#naveed.bhuiyan
password = ""

#port 993
imap = imaplib.IMAP4_SSL(imap_server)

imap.login(email_address, password)

def check_for_new_emails(imap):
    imap.select("inbox")
    # Search for all unread emails
    result, data = imap.search(None, 'UNSEEN')
    email_ids = data[0].split()

    for email_id in email_ids:
        # Fetch the email by ID
        res, msg_data = imap.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                # Extract email body
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                # Perform sentiment analysis on the email body
                sentiment_result = sentiment_analysis(body[:512])[0]  # Limit the text size for performance
                sentiment = sentiment_result['label']
                confidence = sentiment_result['score']

                # Show a popup notification with the sentiment
                show_notification(subject, sentiment, confidence)

def show_notification(subject, sentiment, confidence):
    # Use pync to send macOS notification
    Notifier.notify(
        f"Sentiment: {sentiment} ({confidence:.2f})",
        title=f"New Email: {subject}"
    )


if __name__ == "__main__":
    # Connect to the email server

    try:
        while True:
            # Check for new emails every 60 seconds
            check_for_new_emails(imap)
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping the email notifier.")
        imap.logout()

"""
imap.select("Inbox")

_, msgnums = imap.search(None, "ALL")

for msgnum in msgnums[0].split():
    _, data = imap.fetch(msgnum,"(RFC822)")
    message = email.message_from_bytes(data[0][1])

    for part in message.walk():
        if part.get_content_type() == "text/plain":
            print(part.as_string())

imap.close()
"""
