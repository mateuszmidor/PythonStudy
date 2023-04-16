from generated import read_binance_trades_csv, trade_to_exante_row, write_exante_csv
import sys

# print welcome prompt with app usage instructions
def print_usage():
    print("Welcome to Binance to Exante CSV converter!")
    print("Usage: python main.py <input_binance_csv> <output_exante_csv>")
    print("Example: python main.py binance.csv exante.csv")


# add comments to the top of the output file
if __name__ == "__main__":

    # if less than 3 arguments are provided (scriptname, input, output), print usage instructions and exit
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    binance_trades = read_binance_trades_csv(sys.argv[1])
    exante_rows = trade_to_exante_row(binance_trades)
    for i, t in enumerate(exante_rows):
        print(i)
        print(t)
        print() 
        

    write_exante_csv(exante_rows, sys.argv[2])
    
    