import pandas as pd
import os
import sys
from pathlib import Path

def excel_to_csv(excel_file, output_csv=None, sheet_name="Sheet1"):
    """
    Convert Excel file (specific sheet) to CSV file
    
    Args:
        excel_file (str): Path to Excel file
        output_csv (str, optional): Path to output CSV file. 
                                   If None, will use same name as Excel file with .csv extension
        sheet_name (str, optional): Name of the sheet to convert. Default is "Sheet1"
    
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Check if file exists
        if not os.path.exists(excel_file):
            print(f"Error: File {excel_file} not found.")
            return None
        
        # Read Excel file from specified sheet
        print(f"Reading Excel file: {excel_file} (Sheet: {sheet_name})")
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
        except ValueError as e:
            print(f"Error: {str(e)}")
            # List available sheets
            available_sheets = pd.ExcelFile(excel_file).sheet_names
            print(f"Available sheets: {', '.join(available_sheets)}")
            return None
        
        # Check if required columns exist
        required_columns = ["Name", "NIK", "Phone Number", "Address"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Warning: Missing columns: {', '.join(missing_columns)}")
            print("Available columns:", ', '.join(df.columns))
        
        # Set output filename if not provided
        if output_csv is None:
            excel_path = Path(excel_file)
            output_csv = str(excel_path.with_suffix('.csv'))
        
        # Write to CSV
        df.to_csv(output_csv, index=False)
        print(f"Successfully converted to CSV: {output_csv}")
        
        # Display preview of the data
        print("\nData Preview:")
        print(df.head())
        
        return output_csv
        
    except Exception as e:
        print(f"Error converting Excel to CSV: {str(e)}")
        return None

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python excel_to_csv.py <excel_file> [output_csv_file] [sheet_name]")
        return
    
    excel_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    sheet_name = sys.argv[3] if len(sys.argv) > 3 else "Sheet1"
    
    excel_to_csv(excel_file, output_csv, sheet_name)

if __name__ == "__main__":
    main()