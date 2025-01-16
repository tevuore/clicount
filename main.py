import csv
from datetime import datetime
import os
import sys
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Interactive questionnaire that saves responses to a CSV file.')
    parser.add_argument('csv_file', nargs='?', default='responses.csv',
                       help='Name of the CSV file to store responses (default: responses.csv)')
    return parser.parse_args()

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

def get_user_input(headers):
    answers = []
    for header in headers:
        # Convert header to question format
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

def edit_answers(headers, answers):
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
                new_value = input(f"Enter new value for {headers[choice-1]}: ")
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

def main():
    args = parse_arguments()
    headers = get_headers(args.csv_file)
    
    while True:
        print(f"\nWelcome to the questionnaire! (saving to {args.csv_file})")
        print("Please answer the following questions:\n")
        
        answers = get_user_input(headers)
        print_summary(headers, answers)
        
        while True:
            print("\nWhat would you like to do?")
            print("1. Edit values")
            print("2. Save and enter next entry")
            print("3. Save and quit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                answers = edit_answers(headers, answers)
            elif choice == "2":
                save_to_csv(args.csv_file, headers, answers)
                break
            elif choice == "3":
                save_to_csv(args.csv_file, headers, answers)
                return
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
