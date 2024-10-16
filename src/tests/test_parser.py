import os
import sys
sys.path.append(os.getcwd())
import pandas as pd


from src.export_parser.GlookoParser import GlookoParser
from src.export_parser.DexcomParser import DexcomParser



def main():
    
    dexcom = DexcomParser('src/tests/test_files/Clarity_Export_Jankových_Samuel_2024-10-14_170219.csv')
    print(dexcom.insulin)
    
    glooko_insulin_file = 'src/tests/test_files/export_Samuel Jankovych copy/Insulin data/insulin_data.csv'
    glooko = GlookoParser(glooko_insulin_file)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(glooko.insulin)
    
    
    
    
    
    
    
if __name__ == '__main__':
    main()