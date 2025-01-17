import pytest
import os
import csv
from main import save_to_csv

def test_csv_line_ending_bug(tmp_path):
    # Create a test CSV file path
    test_csv = tmp_path / "test.csv"
    
    # Test headers
    headers = ["Amount", "Category", "Account"]
    
    # Test data
    test_answers1 = ["10", "food", "groceries"]
    test_answers2 = ["20", "transport", "taxi"]
    
    # First save - this creates the file with headers
    save_to_csv(str(test_csv), headers, test_answers1)
    
    # Read the file content after first save
    with open(test_csv, 'r') as f:
        content_after_first = f.read()
    
    # Verify first save has proper line endings
    assert content_after_first.count('\n') == 2, "File should have two lines (headers and data) with proper line endings"
    
    # Second save - this should properly append
    save_to_csv(str(test_csv), headers, test_answers2)
    
    # Read the file content after second save
    with open(test_csv, 'r') as f:
        content_after_second = f.read()
    
    # Verify second save has proper line endings
    assert content_after_second.count('\n') == 3, "File should have three lines with proper line endings"
    
    # Read as CSV to verify structure
    with open(test_csv, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    # Verify we have the correct number of rows
    assert len(rows) == 3, "CSV should have exactly 3 rows (headers + 2 data rows)"
    
    # Verify headers
    assert rows[0][1:] == headers, "First row should be headers"
    
    # Verify data rows (excluding timestamp)
    assert rows[1][1:] == test_answers1, "Second row should be first test data"
    assert rows[2][1:] == test_answers2, "Third row should be second test data"

def test_csv_single_line_bug(tmp_path):
    """This test specifically reproduces the bug where a CSV file with only headers
    doesn't get proper line endings when appending data."""
    
    test_csv = tmp_path / "test_single_line.csv"
    
    # Create a CSV file with just headers (no newline at the end)
    with open(test_csv, 'w', newline='') as f:
        f.write("Timestamp,Amount,Category,Account")
    
    # Headers and test data
    headers = ["Amount", "Category", "Account"]
    test_answers = ["10", "food", "groceries"]
    
    # Try to append data
    save_to_csv(str(test_csv), headers, test_answers)
    
    # Read the resulting file
    with open(test_csv, 'r') as f:
        content = f.read()
        
    # Split into lines and verify
    lines = content.split('\n')
    assert len(lines) >= 2, "File should have at least 2 lines (headers and data)"
    assert lines[0] == "Timestamp,Amount,Category,Account", "First line should be headers"
    assert "10,food,groceries" in lines[1], "Second line should contain our test data"
    
    # Verify the file ends with a newline
    assert content.endswith('\n'), "File should end with a newline"
