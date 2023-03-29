import pandas as pd
import matplotlib.pyplot as plt
from a_share_utils import *
from tkinter import *
from tkinter import filedialog

# Define the global variables
tickers = []    # list of stock tickers to be plotted
data = {}       # dictionary of stock data, with ticker as key and dataframe as value

def start_app(valid_tickers):
    # Initialize the Tkinter application and create a main window
    root = Tk()
    root.title("Stock Analytics App")

    # Create a menu bar
    menubar = Menu(root)

    # Create a File menu with Open, Save and Exit options
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    # Create a Help menu with About option
    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)

    # Set the menu bar
    root.config(menu=menubar)

    # Create a frame for the stock ticker buttons
    ticker_frame = Frame(root, padx=10, pady=10)
    ticker_frame.grid(row=0, column=0, sticky="nsew")

    # Create a label for the stock ticker entry box
    ticker_label = Label(ticker_frame, text="Enter Stock Code:")
    ticker_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    # Create an entry box for entering the stock ticker
    ticker_entry = Entry(ticker_frame, width=10)
    ticker_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Create a button to add the stock ticker
    add_button = Button(ticker_frame, text="Add", command=lambda: add_ticker(ticker_entry.get()))
    add_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    # Create a frame for the plot area
    plot_frame = Frame(root, padx=10, pady=10)
    plot_frame.grid(row=0, column=1, sticky="nsew")

    # Create a label for the plot area
    plot_label = Label(plot_frame, text="Select a stock ticker to plot")
    plot_label.pack()

    # Create buttons for each valid stock ticker
    for ticker in valid_tickers:
        ticker_button = Button(ticker_frame, text=ticker, command=lambda t=ticker: plot_ticker(t))
        ticker_button.grid(padx=5, pady=5, sticky="w")

    # Create a function to add a stock ticker to the list
    def add_ticker(ticker):
        # Check if the ticker is already in the list
        if ticker.upper() in tickers:
            messagebox.showwarning("Duplicate Ticker", "The stock ticker is already in the list.")
        else:
            # Add the ticker to the list and update the plot label
            tickers.append(ticker.upper())
            plot_label.config(text="Select a stock ticker to plot: " + ", ".join(tickers))

            # Load the stock data if it hasn't been loaded
            if ticker.upper() not in data:
                load_data(ticker
