import csv
from datetime import datetime
import os

def get_headers():
    filename = "responses.csv"
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

def save_to_csv(headers, answers):
    filename = "responses.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_headers = ["Timestamp"] + headers
    row = [timestamp] + answers
    
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(full_headers)
        writer.writerow(row)
    
    print(f"\nResponses have been saved to {filename}")

def main():
    headers = get_headers()
    
    while True:
        print("\nWelcome to the questionnaire!")
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
                save_to_csv(headers, answers)
                break
            elif choice == "3":
                save_to_csv(headers, answers)
                return
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
