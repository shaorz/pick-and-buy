import tkinter as tk
from dataclasses import dataclass
from tkinter import *
from tkinter import filedialog
from typing import List

import pandas as pd

import a_share_utils


@dataclass ( init = False )
class StockAnalyticsApp ( tk.Tk ):
	hist_price_df: pd.DataFrame
	peace: float
	spike_multiplier: float
	volume_analytics_df: pd.DataFrame
	valid_tickers: List
	peaceScale: Scale = 0.2
	spikeEntry: Entry = 10

	def __init__ ( self , hist_price_df: pd.DataFrame , *args , **kwargs ):
		super ().__init__ ( *args , **kwargs )
		self.hist_price_df = hist_price_df
		self.title ( "Stock Analytics App" )
		self.geometry ( "800x600" )

		menubar = Menu ( self )
		# Create a File menu with Open, Save and Exit options
		file_menu = Menu ( menubar , tearoff = 0 )
		file_menu.add_command ( label = "Open" , command = self.open_file )
		file_menu.add_command ( label = "Save" , command = self.save_file )
		file_menu.add_command ( label = "Exit" , command = self.quit )
		menubar.add_cascade ( label = "File" , menu = file_menu )

		# Create a Help menu with About option
		help_menu = Menu ( menubar , tearoff = 0 )
		help_menu.add_command ( label = "About" , command = self.show_about )
		menubar.add_cascade ( label = "Help" , menu = help_menu )

		# Set the menu bar
		self.config ( menu = menubar )

		# create a frame to hold the scale and the canvas
		frame = tk.Frame ( self , padx = 10 , pady = 10 )
		frame.grid ( row = 0 , column = 0 , sticky = "nsew" )

		peace_label = tk.Label ( frame , text = "Select a value for historical peacefulness" )
		peace_label.grid ( row = 0 , column = 0 , padx = 5 , pady = 5 , sticky = "w" )
		# create a horizontal scale and pack it in the middle
		self.peaceScale = tk.Scale ( frame , orient = 'horizontal' , from_ = 0.0 , to = 1.0 , resolution = 0.01 )
		self.peaceScale.grid ( row = 0 , column = 1 , padx = 5 , pady = 5 , sticky = "e" )

		# Create a label for the stock ticker entry box
		ticker_label = Label ( frame , text = "Enter volume shock level:" )
		ticker_label.grid ( row = 1 , column = 0 , padx = 5 , pady = 5 , sticky = "w" )

		# Create an entry box for entering the stock ticker
		self.spikeEntry = Entry ( frame , width = 10 )
		self.spikeEntry.grid ( row = 1 , column = 1 , padx = 5 , pady = 5 , sticky = "e" )

		# Create a button to add the stock ticker
		add_button = Button ( frame , text = "Start monitoring" , command = self.refreshVolumeAnalyticsDF )  # add_ticker ( ticker_entry.get () )
		add_button.grid ( row = 1 , column = 2 , padx = 5 , pady = 5 , sticky = "nsew" )

		# Create a frame for the plot area
		plot_frame = Frame ( self , padx = 10 , pady = 10 )
		plot_frame.grid ( row = 2 , column = 0 , sticky = "nsew" )

		self.volume_analytics_df = a_share_utils.constructVolumeAnalyticsDF ( self.hist_price_df )
		self.valid_tickers = a_share_utils.getPeacefulStocks ( self.volume_analytics_df )
		# Create buttons for each valid stock ticker
		for ticker in self.valid_tickers:
			ticker_button = Button ( frame , text = ticker , command = lambda t = ticker: print ( ticker ) )  # lambda t = ticker: plot_ticker ( t )
			ticker_button.grid ( padx = 5 , pady = 5 , sticky = "w" )

		# Menu pop up
		def pop ( event ):
			menubar.post ( event.x_root , event.y_root )

		self.bind ( "<Button-3>" , pop )

	def open_file ( self ):
		file_path = filedialog.askopenfilename ( filetypes = [ ("CSV files" , "*.csv") , ("All Files" , "*.*") ] )

	# TODO: Process the file and update the UI

	# Create a function to save the plot
	def save_file ( self ):
		file_path = filedialog.asksaveasfilename ( defaultextension = ".png" , filetypes = [ ("PNG files" , "*.png") , ("All Files" , "*.*") ] )

	# TODO: Save the plot to the file

	# Create a function to show the About dialog
	def show_about ( self ):
		about_window = Toplevel ( self )
		about_window.title ( "About Stock Analytics App" )
		about_label = Label ( about_window , text = "Stock Analytics App v1.0\n\n© 2023 - All rights reserved" )
		about_label.grid ( row = 0 , column = 0 , sticky = "nsew" )

	def refreshVolumeAnalyticsDF ( self ):
		self.peace = self.peaceScale.get ()
		self.spike_multiplier = float ( self.spikeEntry.get () )
		print ( "Refresh volume parameter peace:" , self.peace )
		print ( "spike multiplier:" , self.spike_multiplier )
		self.volume_analytics_df = a_share_utils.constructVolumeAnalyticsDF ( self.hist_price_df , peace_level = self.peace , spike_multiplier = self.spike_multiplier )
		self.valid_tickers = a_share_utils.getPeacefulStocks ( self.volume_analytics_df )

