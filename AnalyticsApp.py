from dataclasses import dataclass
from tkinter import *
from tkinter import filedialog

import pandas as pd

import a_share_utils


@dataclass ( init = False )
class StockAnalyticsApp:
	volume_analytics_df: pd.DataFrame
	root: Tk
	menubar: Menu

	def __init__ ( self , volume_df: pd.DataFrame ):
		self.volume_analytics_df = volume_df
		self.root = Tk ()
		self.root.title ( "Stock Analytics App" )
		self.menubar = Menu ( self.root )

	def open_file ( self ):
		file_path = filedialog.askopenfilename ( filetypes = [ ("CSV files" , "*.csv") , ("All Files" , "*.*") ] )

	# TODO: Process the file and update the UI

	# Create a function to save the plot
	def save_file ( self ):
		file_path = filedialog.asksaveasfilename ( defaultextension = ".png" , filetypes = [ ("PNG files" , "*.png") , ("All Files" , "*.*") ] )

	# TODO: Save the plot to the file

	# Create a function to show the About dialog
	def show_about ( self ):
		about_window = Toplevel ( self.root )
		about_window.title ( "About Stock Analytics App" )
		about_label = Label ( about_window , text = "Stock Analytics App v1.0\n\n© 2023 - All rights reserved" )
		about_label.grid ( row = 0 , column = 0 , sticky = "nsew" )

	# Menu pop up
	def pop ( self , event ):
		self.menubar.post ( event.x_root , event.y_root )

	def start_app ( self ) -> None:
		# Create a File menu with Open, Save and Exit options
		file_menu = Menu ( self.menubar , tearoff = 0 )
		file_menu.add_command ( label = "Open" , command = self.open_file )
		file_menu.add_command ( label = "Save" , command = self.save_file )
		file_menu.add_separator ()
		file_menu.add_command ( label = "Exit" , command = self.root.quit )
		self.menubar.add_cascade ( label = "File" , menu = file_menu )

		# Create a Help menu with About option
		help_menu = Menu ( self.menubar , tearoff = 0 )
		help_menu.add_command ( label = "About" , command = self.show_about )
		self.menubar.add_cascade ( label = "Help" , menu = help_menu )

		# Set the menu bar
		self.root.config ( menu = self.menubar )

		# Create a frame for the stock ticker buttons
		ticker_frame = Frame ( self.root , padx = 10 , pady = 10 )
		ticker_frame.grid ( row = 0 , column = 0 , sticky = "nsew" )

		# Create a label for the stock ticker entry box
		ticker_label = Label ( ticker_frame , text = "Enter Stock Code:" )
		ticker_label.grid ( row = 0 , column = 0 , padx = 5 , pady = 5 , sticky = "w" )

		# Create an entry box for entering the stock ticker
		ticker_entry = Entry ( ticker_frame , width = 10 )
		ticker_entry.grid ( row = 0 , column = 1 , padx = 5 , pady = 5 , sticky = "w" )

		# Create a button to add the stock ticker
		add_button = Button ( ticker_frame , text = "Add" , command = lambda: print ( "add_button" ) )  # add_ticker ( ticker_entry.get () )
		add_button.grid ( row = 0 , column = 2 , padx = 5 , pady = 5 , sticky = "w" )

		# Create a frame for the plot area
		plot_frame = Frame ( self.root , padx = 10 , pady = 10 )
		plot_frame.grid ( row = 0 , column = 1 , sticky = "nsew" )

		# Create a label for the plot area
		plot_label = Label ( plot_frame , text = "Select a stock ticker to plot" )
		plot_label.pack ()

		valid_tickers = a_share_utils.getPeacefulStocks ( self.volume_analytics_df )
		# Create buttons for each valid stock ticker
		for ticker in valid_tickers:
			ticker_button = Button ( ticker_frame , text = ticker , command = lambda t = ticker: print ( ticker ) )  # lambda t = ticker: plot_ticker ( t )
			ticker_button.grid ( padx = 5 , pady = 5 , sticky = "w" )

		self.root.bind ( "<Button-3>" , self.pop )
		self.root.mainloop ()
