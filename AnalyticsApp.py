import tkinter as tk
from dataclasses import dataclass
from functools import partial
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
	plot_frame: Frame
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
		file_menu.add_command ( label = "Open" , command = self.openFile )
		file_menu.add_command ( label = "Save" , command = self.saveFile )
		file_menu.add_command ( label = "Exit" , command = self.quit )
		menubar.add_cascade ( label = "File" , menu = file_menu )

		# Create a Help menu with About option
		help_menu = Menu ( menubar , tearoff = 0 )
		help_menu.add_command ( label = "About" , command = self.showAbout )
		menubar.add_cascade ( label = "Help" , menu = help_menu )

		# Set the menu bar
		self.config ( menu = menubar )

		# Menu pop up
		def pop ( event ):
			menubar.post ( event.x_root , event.y_root )

		self.bind ( "<Button-3>" , pop )

		# create a frame to hold the scale and the canvas
		self.frame = tk.Frame ( self , padx = 10 , pady = 10 )
		self.frame.grid ( row = 0 , column = 0 , sticky = "nsew" )

		peace_label = tk.Label ( self.frame , text = "Select a value for historical peacefulness" , bg = '#4C5C74' )
		peace_label.grid ( row = 0 , column = 0 , padx = 5 , pady = 5 , sticky = "w" )
		# create a horizontal scale and pack it in the middle
		self.peaceScale = tk.Scale ( self.frame , orient = 'horizontal' , from_ = 0.0 , to = 1.0 , resolution = 0.01 )
		self.peaceScale.grid ( row = 0 , column = 1 , padx = 5 , pady = 5 , sticky = "e" )

		# Create a label for the stock ticker entry box
		ticker_label = Label ( self.frame , text = "Enter volume shock level:" , bg = '#4C5C74' )
		ticker_label.grid ( row = 1 , column = 0 , padx = 5 , pady = 5 , sticky = "w" )

		# Create an entry box for entering the stock ticker
		self.spikeEntry = Entry ( self.frame , width = 10 )
		self.spikeEntry.grid ( row = 1 , column = 1 , padx = 5 , pady = 5 , sticky = "e" )

		# Create a button to add the stock ticker
		add_button = Button ( self.frame , text = "Start monitoring" , command = self.refreshVolumeAnalyticsDF , bg = '#4C5C74' )
		add_button.grid ( row = 1 , column = 2 , padx = 5 , pady = 5 , sticky = "nsew" )

		# Create a frame for the plot area
		self.plot_frame = Frame ( self , padx = 10 , pady = 10 )
		self.plot_frame.grid ( row = 1 , column = 0 , sticky = "nsew" )
		self.refreshVolumeAnalyticsDF ()

	def openFile ( self ):
		file_path = filedialog.askopenfilename ( filetypes = [ ("CSV files" , "*.csv") , ("All Files" , "*.*") ] )

	# TODO: Process the file and update the UI

	# Create a function to save the plot
	def saveFile ( self ):
		file_path = filedialog.asksaveasfilename ( defaultextension = ".png" , filetypes = [ ("PNG files" , "*.png") , ("All Files" , "*.*") ] )

	# TODO: Save the plot to the file

	# Create a function to show the About dialog
	def showAbout ( self ):
		about_window = Toplevel ( self )
		about_window.title ( "About Stock Analytics App" )
		about_window.geometry ( "350x150" )
		about_label = Label ( about_window , text = "Stock Analytics App v1.0" )
		about_label.grid ( row = 0 , column = 0 , sticky = "nsew" )
		content_label = Label ( about_window , text = "Desktop application to facilitate volume-chasing trades.\n\n" )
		content_label.grid ( row = 1 , column = 0 , sticky = "w" )
		author_label = Label ( about_window , text = "Designed by RogerSF\n\n© 2023 - All rights reserved" )
		author_label.grid ( row = 2 , column = 0 , sticky = "e" )

	def showTickerBenchmark ( self , ticker: str ):
		ticker_window = Toplevel ( self )
		ticker_window.title ( ticker + " Volume Analsis" )
		ticker_window.geometry ( "400x150" )
		ticker_row = self.volume_analytics_df.loc [ self.volume_analytics_df [ 'code' ] == ticker ]
		about_label = Label ( ticker_window , text = str ( ticker_row ) )
		about_label.grid ( row = 0 , column = 0 , sticky = "nsew" )

	def refreshVolumeAnalyticsDF ( self ):
		self.peace = self.peaceScale.get ()

		try:
			self.spike_multiplier = float ( self.spikeEntry.get () )
		except Exception:
			self.spike_multiplier = 10

		print ( "Refresh volume parameter peace:" , self.peace )
		print ( "spike multiplier:" , self.spike_multiplier )
		self.volume_analytics_df = a_share_utils.constructVolumeAnalyticsDF ( self.hist_price_df , peace_level = self.peace , spike_multiplier = self.spike_multiplier )
		self.valid_tickers = a_share_utils.getPeacefulStocks ( self.volume_analytics_df )
		print ( "updated valid stock list" , self.valid_tickers )

		# Create buttons for each valid stock ticker
		for widget in self.plot_frame.winfo_children ():
			widget.destroy ()

		for i , ticker in enumerate ( self.valid_tickers ):
			r: int = int ( i / 10 )
			col: int = int ( i % 10 )
			ticker_button: Button = Button ( self.plot_frame , text = ticker , command = partial ( self.showTickerBenchmark , ticker ) , bg = '#4C5C74' )
			ticker_button.grid ( row = r , column = col , padx = 5 , pady = 5 , sticky = "w" )
