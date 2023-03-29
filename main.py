# import easytrader
from tkinter import *

import a_share_utils


def start_app ():
	# Initialize EasyTrader
	# user = easytrader.use ( 'ths' )
	# user.prepare ( 'path/to/ht.json' )
	preceding_days: int = 30
	peace_level: float = 0.2

	a_share_data , volume_benchmark_df = a_share_utils.get_a_share_hist_data ( preceding_days = preceding_days , peace_level = peace_level )
	mask = (volume_benchmark_df [ 'peace' ])

	t = Tk ()
	t.geometry ( "600x600" )
	t.title ( "Stock Picker" )
	fileOptions = [ "New" , "open" , "Save" , "Save as" ]
	fileOptionsAfterseparator = [ "Import" , "Export" , "Exit" ]
	viewOptions = [ "Transform" , "Edit" , "Create" ]
	menuBar = Menu ( t )
	file = Menu ( menuBar , tearoff = 0 )

	for i in fileOptions:
		file.add_command ( label = i , command = None )
	file.add_separator ()

	for i in fileOptionsAfterseparator:
		file.add_command ( label = i , command = None )
	menuBar.add_cascade ( label = "File" , menu = file )

	View = Menu ( menuBar , tearoff = 0 )
	for i in viewOptions:
		View.add_command ( label = i , command = None )
	menuBar.add_cascade ( label = "View" , menu = View )
	t.config ( menu = menuBar )

	t.mainloop ()


if __name__ == '__main__':
	start_app ()
