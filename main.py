# import easytrader

from tkinter import *
from tkinter import filedialog

import a_share_utils


def start_app ( valid_tickers ):
	# Initialize the Tkinter application and create a main window
	root = Tk ()
	root.title ( "Stock Analytics App" )

	# Create a menu bar
	menubar = Menu ( root )

	# Create a File menu with Open, Save and Exit options
	file_menu = Menu ( menubar , tearoff = 0 )
	file_menu.add_command ( label = "Open" , command = open_file )
	file_menu.add_command ( label = "Save" , command = save_file )
	file_menu.add_separator ()
	file_menu.add_command ( label = "Exit" , command = root.quit )
	menubar.add_cascade ( label = "File" , menu = file_menu )

	# Create a Help menu with About option
	help_menu = Menu ( menubar , tearoff = 0 )
	help_menu.add_command ( label = "About" , command = show_about )
	menubar.add_cascade ( label = "Help" , menu = help_menu )

	# Set the menu bar
	root.config ( menu = menubar )

	# Create a frame for the stock ticker buttons
	ticker_frame = Frame ( root , padx = 10 , pady = 10 )
	ticker_frame.grid ( row = 0 , column = 0 , sticky = "nsew" )

	# Create a label for the stock ticker entry box
	ticker_label = Label ( ticker_frame , text = "Enter Stock Code:" )
	ticker_label.grid ( row = 0 , column = 0 , padx = 5 , pady = 5 , sticky = "w" )

	# Create an entry box for entering the stock ticker
	ticker_entry = Entry ( ticker_frame , width = 10 )
	ticker_entry.grid ( row = 0 , column = 1 , padx = 5 , pady = 5 , sticky = "w" )

	# Create a button to add the stock ticker
	add_button = Button ( ticker_frame , text = "Add" , command = lambda: add_ticker ( ticker_entry.get () ) )
	add_button.grid ( row = 0 , column = 2 , padx = 5 , pady = 5 , sticky = "w" )

	# Create a frame for the plot area
	plot_frame = Frame ( root , padx = 10 , pady = 10 )
	plot_frame.grid ( row = 0 , column = 1 , sticky = "nsew" )

	# Create a label for the plot area
	plot_label = Label ( plot_frame , text = "Select a stock ticker to plot" )
	plot_label.pack ()

	# Create buttons for each valid stock ticker
	for ticker in valid_tickers:
		ticker_button = Button ( ticker_frame , text = ticker , command = lambda t = ticker: plot_ticker ( t ) )
		ticker_button.grid ( padx = 5 , pady = 5 , sticky = "w" )

	# Create a function to open a file dialog
	def open_file ():
		file_path = filedialog.askopenfilename ( filetypes = [ ("CSV files" , "*.csv") , ("All Files" , "*.*") ] )

	# TODO: Process the file and update the UI

	# Create a function to save the plot
	def save_file ():
		file_path = filedialog.asksaveasfilename ( defaultextension = ".png" , filetypes = [ ("PNG files" , "*.png") , ("All Files" , "*.*") ] )

	# TODO: Save the plot to the file

	# Create a function to show the About dialog
	def show_about ():
		about_window = Toplevel ( root )
		about_window.title ( "About Stock Analytics App" )
		about_label = Label ( about_window , text = "Stock Analytics App v1.0\n\n© 2023 - All rights reserved" )


if __name__ == '__main__':
	preceding_days: int = 30
	peace_level: float = 0.2
	a_share_data , volume_benchmark_df = a_share_utils.get_a_share_hist_data ( preceding_days = preceding_days , peace_level = peace_level )
	peaceTickers = a_share_utils.getPeacefulStocks ( volume_benchmark_df )
	start_app ( peaceTickers )
