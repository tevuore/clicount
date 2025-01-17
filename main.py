import csv
from datetime import datetime
import os
import sys
import argparse
import yaml
from tabulate import tabulate

COMMANDS = {
    'write': {
        'description': '[Default] Add new entries to a CSV file with interactive prompts',
        'usage': 'write <csv_file>',
        'example': 'write expenses.csv'
    },
    'show': {
        'description': 'Display entries from a CSV file in a formatted table',
        'usage': 'show <csv_file>',
        'example': 'show expenses.csv'
    },
    'help': {
        'description': 'Show this help message with detailed command information',
        'usage': 'help',
        'example': 'help'
    }
}

def show_help():
    """Display detailed help information about available commands."""
    print("\nAvailable Commands:")
    print("-" * 80)
    
    rows = []
    for cmd, info in COMMANDS.items():
        rows.append([
            cmd,
            info['description'],
            info['usage'],
            info['example']
        ])
    
    print(tabulate(rows, 
                  headers=['Command', 'Description', 'Usage', 'Example'],
                  tablefmt='grid'))
    
    print("\nOptions:")
    print("  --categories FILE  Specify a YAML file containing category definitions")
    print("                    (default: categories.yaml)")
    print("\nNotes:")
    print("- If no command is specified, 'write' is assumed")
    print("- Categories in the YAML file will be used for matching column names")
    print("- CSV file is required for all commands except 'help'\n")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='CSV-based questionnaire with category support.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s write expenses.csv          # Add new entries to expenses.csv
  %(prog)s show expenses.csv           # Display entries from expenses.csv
  %(prog)s expenses.csv                # Same as 'write expenses.csv'
  %(prog)s help                        # Show detailed command information
        """)
    
    parser.add_argument('command', nargs='?', default='write',
                       help='Command to execute: write, show, or help. If omitted, defaults to write')
    parser.add_argument('csv_file', nargs='?',
                       help='CSV file to read from or write to (required except for help command)')
    parser.add_argument('--categories', default='categories.yaml',
                       help='YAML file containing category definitions (default: categories.yaml)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle help command
    if args.command == 'help':
        show_help()
        sys.exit(0)
    
    # If first argument is not a valid command, treat it as the CSV file
    if args.command not in COMMANDS:
        args.csv_file = args.command
        args.command = 'write'
    
    # Validate CSV file is provided for non-help commands
    if not args.csv_file:
        parser.error("CSV file is required for {} command".format(args.command))
    
    return args

def process_yaml_dict(data, prefix=''):
    """Process a YAML dictionary and its nested structure into dot-notation paths."""
    result = []
    
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # Process nested dictionary
                for key, value in item.items():
                    key_path = f"{prefix}.{key}" if prefix else key
                    result.append(key_path)
                    result.extend(process_yaml_dict(value, key_path))
            else:
                # Simple list item
                result.append(f"{prefix}.{item}" if prefix else item)
    elif isinstance(data, dict):
        for key, value in data.items():
            key_path = f"{prefix}.{key}" if prefix else key
            result.append(key_path)
            result.extend(process_yaml_dict(value, key_path))
    
    return result

def load_categories(categories_file='categories.yaml'):
    """Load categories from YAML file."""
    if not os.path.exists(categories_file):
        return {}
    
    try:
        with open(categories_file, 'r') as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return {}
            
            result = {}
            for category, items in data.items():
                if not isinstance(items, list):
                    continue
                
                processed = []
                for item in items:
                    if isinstance(item, str):
                        processed.append(item)
                    elif isinstance(item, dict):
                        # Item is a dictionary with nested structure
                        for key, value in item.items():
                            processed.append(key)
                            processed.extend(process_yaml_dict(value, key))
                
                if processed:
                    result[category] = sorted(list(set(processed)))
            
            return result
    except yaml.YAMLError:
        return {}

def flatten_categories(category_dict, prefix='', result=None):
    """Convert nested category dictionary into a flat list with full paths."""
    if result is None:
        result = []
    
    if not category_dict:
        return result
    
    for key, values in category_dict.items():
        if not isinstance(values, list):
            continue
        
        for item in values:
            if isinstance(item, str):
                if '.' in item:
                    # Already flattened path
                    result.append(item)
                else:
                    # Simple category
                    path = f"{prefix}.{item}" if prefix else item
                    result.append(path)
            elif isinstance(item, list):
                # This is a list of subcategories for the previous item
                if result:
                    parent = result[-1]
                    result.extend([f"{parent}.{child}" for child in item])
    
    return sorted(list(set(result)))  # Remove duplicates and sort

def get_headers(filename):
    """Get headers from CSV file or return default headers."""
    default_headers = ["Amount", "Category", "Account"]
    
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)[1:]  # Skip timestamp column
            return headers if headers else default_headers
    except (FileNotFoundError, StopIteration):
        return default_headers

def get_user_input(headers, categories):
    """Get user input for all fields."""
    answers = []
    
    for header in headers:
        if header in categories:
            print(f"\nSelect {header}:")
            value = get_category_value(header, categories)
            answers.append(value)
        else:
            question = f"What is your {header.lower()}?"
            answer = input(f"{question} ")
            answers.append(answer)
    
    return answers

def print_summary(headers, answers):
    print("\nSummary of your responses:")
    print("-" * 30)
    for header, answer in zip(headers, answers):
        print(f"{header}: {answer}")
    print("-" * 30)

def edit_answers(headers, answers, categories):
    while True:
        print("\nWhich field would you like to edit?")
        for i, header in enumerate(headers, 1):
            print(f"{i}. {header}")
        print("0. Done editing")
        
        try:
            choice = int(input("\nEnter the number of the field to edit (0 to finish): "))
            if choice == 0:
                break
            if 1 <= choice <= len(headers):
                header = headers[choice-1]
                # Check if this header has predefined categories
                category_value = get_category_value(header, categories)
                if category_value is not None:
                    answers[choice-1] = category_value
                else:
                    new_value = input(f"Enter new value for {header}: ")
                    answers[choice-1] = new_value
                print_summary(headers, answers)
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    return answers

def save_to_csv(filename, headers, answers):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_headers = ["Timestamp"] + headers
    row = [timestamp] + answers
    
    file_exists = os.path.exists(filename)
    
    if file_exists:
        # Check if file ends with newline
        with open(filename, 'r') as f:
            f.seek(0, 2)  # Seek to end of file
            if f.tell() > 0:  # If file is not empty
                f.seek(f.tell() - 1)  # Go to last character
                last_char = f.read(1)
                if last_char != '\n':
                    # If file doesn't end with newline, add it
                    with open(filename, 'a') as f2:
                        f2.write('\n')
    
    # Now append the new data
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(full_headers)
        writer.writerow(row)
    
    print(f"\nResponses have been saved to {filename}")

def show_entries(filename):
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist")
        return
        
    try:
        with open(filename, 'r', newline='') as csvfile:
            # First validate CSV format by reading all lines
            content = csvfile.read()
            if not content.strip():
                print("Error: CSV file is empty")
                return
                
            # Try parsing as CSV
            try:
                reader = csv.reader(content.splitlines())
                headers = next(reader)
                if not headers:
                    print("Error: Invalid CSV format - no headers found")
                    return
                    
                # Read and validate data
                data = []
                header_count = len(headers)
                for row in reader:
                    if len(row) != header_count:
                        print("Error: Invalid CSV format - inconsistent number of columns")
                        return
                    data.append(row)
                    
            except (csv.Error, StopIteration) as e:
                print(f"Error: Invalid CSV format - {str(e)}")
                return
            
            if not data:
                print("No entries found in the file.")
                return
                
            print(f"\nEntries from {filename}:")
            print(tabulate(data, headers=headers, tablefmt='grid'))
            print(f"\nTotal entries: {len(data)}")
            
    except Exception as e:
        print(f"Error reading file: {str(e)}")

def get_category_value(header, categories):
    """Get category value with proper path handling."""
    if header not in categories:
        return None
    
    # Get flattened list of categories
    flat_categories = flatten_categories({header: categories[header]})
    while True:
        print(f"\nAvailable options for {header}:")
        for i, value in enumerate(flat_categories, 1):
            print(f"{i}. {value}")
        
        try:
            choice = int(input(f"\nSelect {header} (1-{len(flat_categories)}): "))
            if 1 <= choice <= len(flat_categories):
                return flat_categories[choice - 1]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    args = parse_arguments()
    
    if args.command == 'show':
        show_entries(args.csv_file)
        return
        
    # Default 'write' command
    headers = get_headers(args.csv_file)
    categories = load_categories(args.categories)
    print("\nCategories loaded:", categories)
    
    while True:
        print(f"\nWelcome to the questionnaire! (saving to {args.csv_file})")
        print("Please answer the following questions:\n")
        
        answers = get_user_input(headers, categories)
        print_summary(headers, answers)
        
        while True:
            print("\nWhat would you like to do?")
            print("1. Edit values")
            print("2. Save and enter next entry")
            print("3. Save and quit")
            print("4. Cancel this entry")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":
                answers = edit_answers(headers, answers, categories)
            elif choice == "2":
                save_to_csv(args.csv_file, headers, answers)
                break
            elif choice == "3":
                save_to_csv(args.csv_file, headers, answers)
                return
            elif choice == "4":
                print("\nEntry cancelled. No data was saved.")
                if input("\nWould you like to enter a new entry? (y/n): ").lower() != 'y':
                    return
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
