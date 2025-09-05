from google import genai


tds_sections = {
    "192A": "Payment of taxable accumulated balance of provident fund",
    "193": "Interest on securities to a resident",
    "194": "Dividend/Deemed dividend to resident",
    "194.": "Deemed dividend on buy back of shares referred to section 2(22)(f)",
    "194A": "Interest other than interest on securities to a resident",
    "194B": "Winning from lottery or crossword puzzle etc",
    "194BA": "Winning from Online gaming",
    "194BA(alt)": "TDS on benefit/perquisite paid to Business/Profession",  # duplicate section, renamed key
    "194BB": "Winning from Horse races to a resident",
    "194C": "Payment to a resident contractor/sub-contractor",
    "194D": "Insurance commission to a resident",
    "194DA": "Payment in respect of life insurance policy",
    "194EE": "Payment in respect of deposits under National Savings Scheme, 1987 to a resident",
    "194F": "Payment on account of repurchase of units of MF or UTI to a resident",
    "194G": "Commission on sale of lottery tickets to a resident",
    "194H": "Commission or brokerage to a resident",
    "194I(a)": "Rent to a resident (Plant and Machinery)",
    "194I(b)": "Rent to a resident (Others)",
    "194IA": "Payment/credit of consideration to a resident transferor for transfer of any immovable property",
    "194IB": "Payment/credit of rent by Individual/HUF to a resident",
    "194IC": "Payment under joint development agreement to resident Individual/HUF",
    "194J": "Fees for professional or technical services to a resident",
    "194K": "Payment of Income to specified unit-holders",
    "194LA": "Payment of compensation to a resident on acquisition of certain immovable property",
    "194LBA(1)": "Income from units of a business trust",
    "194LBB": "Payment in respect of units of investment fund specified in section 115UB",
    "194LBC": "Income from Investment in specified securitization trust u/s 115TCA",
    "194M": "TDS on account of contractual work, brokerage and professional fees etc.",
    "194N": "TDS on Cash Withdrawals",
    "194N(alt)": "Interest on securities to a resident",  # duplicate section, renamed key
    "194O": "Payment by e-commerce operators to e-commerce participants",
    "194O(alt)": "Purchase of goods (Value exceeding 50 lakhs or more)",  # looks like meant 194Q but given as 1940
    "194Q": "Purchase of goods (Value exceeding 50 lakhs or more)",
    "194R": "TDS on benefit/perquisite paid to Business/Profession",
    "194S": "TDS from payment on transfer of Virtual Digital Asset"
}

import os

API_KEY = 'AIzaSyBm3jfoQsO3FG2lKrXzeQEzDzD25RMZb0s'
os.environ['GEMINI_API_KEY'] = API_KEY
print("the api lkey of gemini: -> ",os.environ['GEMINI_API_KEY'] )


client = genai.Client()
print("client connnectede")

def get_tds_section_details(description):
    if not description or description.strip() == "":
        return None, "No description provided."
    
    response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                *tds_sections,
                "given the tds sections and description of the user transaction, you have to accurately choose the section applicable and return the key of the section and return only one section , don't output anything else , wisely choose the section you can not afford a mistake , following is the decsription of transaction ->" + str(description)
            ],
        )
    
    ai_response = response.text
    print("AI Response:", ai_response)

    for section in list(tds_sections.keys())[::-1]:
        if section in ai_response:
            return section, tds_sections[section]