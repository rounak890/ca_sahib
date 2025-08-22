import numpy as np


def find_duplicates_df(data):
    duplicates = data[data.duplicated()]
    return duplicates

def find_anomalies_df(data):
    amt_zscore = (data['amount'] - data['amount'].mean()) / data['amount'].std()
    unusual_amt = data[np.abs(amt_zscore) > 3]  # 3 is a threshold, you can tune it
    return unusual_amt

def bounced_df(data):
    bounce_keywords = ['bounce', 'bounced', 'reversal', 'failed', 'chargeback', 'declined', 'return', 'refund']
    mask = data['name'].str.lower().str.contains('|'.join(bounce_keywords), na=False)

    bounced_entries = data[mask]
    return bounced_entries