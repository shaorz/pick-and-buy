# import easytrader
import a_share_utils
import PySimpleGUI as sg


def start_app( ):
    # Initialize EasyTrader
    # user = easytrader.use ( 'ths' )
    # user.prepare ( 'path/to/ht.json' )

    df = a_share_utils.get_stock_pool_today()


    # Define the GUI layout
    layout = [
        [ sg.Text ( 'Stock Picker' ) ] ,
        [ sg.Text ( 'Stock Code' ) , sg.InputText () ] ,
        [ sg.Text ( 'Quantity' ) , sg.InputText () ] ,
        [ sg.Button ( 'Subscribe' ) , sg.Button ( 'Exit' ) ]
        ]

    # Create the GUI window
    window = sg.Window ( 'IPO Subscription' , layout )

    # Loop to handle events
    while True:
        event , values = window.read ()

        # Exit if the user closes the window or clicks the Exit button
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break

        # Subscribe to the IPO
        if event == 'Subscribe':
            stock_code = values [ 0 ]
            quantity = values [ 1 ]
            # user.buy ( stock_code , price = 'ipo' , amount = quantity )
            sg.popup ( f'Subscribed to {stock_code} with {quantity} shares' )

    # Close the window and exit the program
    window.close ()


if __name__ == '__main__':
    start_app ()
