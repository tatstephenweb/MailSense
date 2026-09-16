import base64

#Function to decode body of the mail from base64 to plain understandable text

def decode_email_body(payload):

    #if the body is in the payload directly this condition will execute
    if payload.get('body', {}).get('data'):
        data = payload['body']['data']
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    #if the email body is divided into parts, this condition will be executed
    if 'parts' in payload:

        # the loop if the body is stored as plain text
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        # the loop if the body is stored as html
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    return "" 

multipart_payload = {
    "mimeType": "multipart/alternative",
    "parts": [
        {
            "mimeType": "text/plain",
            "body": {
                "data": "VGhpcyBpcyB0aGUgcGxhaW4gdGV4dCB2ZXJzaW9uIG9mIHRoZSBlbWFpbC4gVXJnZW50OiBwbGVhc2UgcmVzcG9uZCBieSA1cG0u"
            }
        },
        {
            "mimeType": "text/html",
            "body": {
                "data": "PGh0bWw+PGJvZHk+PHA+VGhpcyBpcyB0aGUgSFRNTCB2ZXJzaW9uPC9wPjwvYm9keT48L2h0bWw+"
            }
        }
    ]
}

simple_payload = {
    "mimeType": "text/plain",
    "body": {
        "data": "SGVsbG8gVGF0LCB0aGlzIGlzIGEgc2ltcGxlIHBsYWluIHRleHQgZW1haWwgd2l0aCBubyBIVE1MIHZlcnNpb24u"
    }
}

print("Simple:", decode_email_body(simple_payload))
print("Multipart:", decode_email_body(multipart_payload))