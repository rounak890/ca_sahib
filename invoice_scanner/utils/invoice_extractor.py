from google import genai
import json
import os

API_KEY = 'AIzaSyBm3jfoQsO3FG2lKrXzeQEzDzD25RMZb0s'
os.environ['GEMINI_API_KEY'] = API_KEY
print("the api lkey of gemini: -> ",os.environ['GEMINI_API_KEY'] )

PROMPT = """
So' you are a experienced accountant who helps CA by extracting important items from the invoices and bills, you have done it for many years,
and know which part of bill is important and which is not , like GST number is important, total amount, tax deducted and date of invoice, 
to whom it was paid etc. and other items like value of each item, quantity etc are alo equallly important extract those.

so now you are provided with a invoice or bill in text format, you have to extract the important items from it and return it in json format,
the json format should be like this:
{
    "invoice_number": "12345",
    "date": "2023-01-01",
    "total_amount": "1000.00",
    "gst_number": "22AAAAA0000A1Z5",
    "tds_deducted": "100.00",
    "vendor_name": "ABC Pvt Ltd",
    "vendor_address": "123, Main Street, City, State, ZIP",
    "items": [
        {
            "description": "Item 1",
            "quantity": "2",
            "unit_price": "500.00",
            "total_price": "1000.00"
        }
    ]
}

DON'T RETURN ANYTHING ELSE THEN THE JSON OBJECT, NO EXPLANATION, NO APOLOGY, NO GREETINGS, NOTHING ELSE


"""

from google.genai import types

client = genai.Client()


def extract_invoice_data(image_bytes):
    
    # with open(img, 'rb') as f:
    #     image_bytes = f.read()

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
            ),
            PROMPT
        ]
    )

    ind = response.text.find('```json')
    if ind != -1:
        response_text = response.text[ind+7:]
        ind2 = response_text.rfind('```')
        if ind2 != -1:
            response_text = response_text[:ind2]
        print("the json part is :- ", response_text)
        
        try:
            data = json.loads(response_text)
            print("the json data is :- ", data)
        except Exception as e:
            print("Error parsing JSON:", e)

        return data

    


