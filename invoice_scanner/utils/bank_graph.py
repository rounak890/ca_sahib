import pandas as pd
from io import BytesIO
import base64
import matplotlib.pyplot as plt

def plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return f'data:image/png;base64,{image_base64}'


def plot_distribution_graph(data):
    debit = data[data.DrCr == 'Db']
    credit = data[data.DrCr == 'Cr']

    # 1. Get the figure and axes objects
    fig, ax = plt.subplots(figsize=(15, 7))

    # 2. Plot your bars on the specific axes `ax`
    ax.bar(debit['date'], debit['amount'], color='green', label='Debit', width=0.8)
    ax.bar(credit['date'], credit['amount'], color='red', label='Credit', width=0.8)

    # 4. Add legend and title
    ax.legend()
    ax.set_title("Debit vs Credit Transactions")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount")
    x_labels = ax.get_xticklabels()

    # Set all labels invisible first
    plt.setp(x_labels, visible=False)

    # Make every 10th label visible
    for i in range(0, len(x_labels), 20): # Change '10' to show every Nth label
        x_labels[i].set_visible(True)
        x_labels[i].set_rotation(45) # Optionally rotate them if still dense
        x_labels[i].set_ha('right')   # Horizontal alignment

    plt.tight_layout()
    return plot_to_base64(fig)
    
def plot_pie_chart(data):
    value_counts = data['DrCr'].value_counts()

    fig, ax = plt.subplots(figsize=(5, 5))
    value_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax)
    ax.set_ylabel('')  # Removes the y-label
    ax.set_title('Debit vs Credit Distribution')
    plt.tight_layout()

    return plot_to_base64(fig)

def plot_bar_graph(data):
    d = dict(data['name'].value_counts())
    final = {}

    for i in d:
        j = d[i]
        if j.item() > 1:
            final[i] = int(j)

    # print(final)

    fig, ax = plt.subplots(figsize=(5, 5))
    plt.title('10 Most happened transactions')
    plt.bar(list(final.keys())[:10], list(final.values())[:10])

    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    return plot_to_base64(fig)
