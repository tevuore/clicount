import csv
from datetime import datetime
import os
import sys
import argparse
import yaml
from tabulate import tabulate

def parse_arguments():
    parser = argparse.ArgumentParser(description='Interactive questionnaire that saves responses to a CSV file.')
    parser.add_argument('command', nargs='?', default='write',
                       choices=['write', 'show'],
                       help='Command to execute: write (default) or show')
    parser.add_argument('csv_file', nargs='?', default='responses.csv',
                       help='Name of the CSV file to store responses (default: responses.csv)')
    parser.add_argument('--categories', default='categories.yaml',
                       help='YAML file containing category definitions (default: categories.yaml)')
    return parser.parse_args()

def load_categories(filename):
    if not os.path.exists(filename):
        return {}
    
    try:
        with open(filename, 'r') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        print(f"Warning: Error parsing {filename}, using empty categories")
        return {}

def get_headers(filename):
    default_headers = ["Name", "Age", "Email", "Occupation"]
    
    if not os.path.exists(filename):
        return default_headers
        
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        try:
            headers = next(reader)
            # Remove timestamp column if it exists
            if headers[0].lower() == "timestamp":
                headers = headers[1:]
            return headers if headers else default_headers
        except StopIteration:
            return default_headers

def get_category_value(header, categories):
    if header not in categories:
        return None
        
    values = categories[header]
    while True:
        print(f"\nAvailable options for {header}:")
        for i, value in enumerate(values, 1):
            print(f"{i}. {value}")
            
        try:
            choice = int(input(f"\nSelect {header} (1-{len(values)}): "))
            if 1 <= choice <= len(values):
                return values[choice - 1]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_user_input(headers, categories):
    answers = []
    for header in headers:
        # Check if this header has predefined categories
        category_value = get_category_value(header, categories)
        if category_value is not None:
            answers.append(category_value)
        else:
            # If no category defined, ask for free-form input
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

def main():
    args = parse_arguments()
    
    if args.command == 'show':
        show_entries(args.csv_file)
        return
        
    # Default 'write' command
    headers = get_headers(args.csv_file)
    categories = load_categories(args.categories)
    
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
