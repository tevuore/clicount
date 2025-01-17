import pytest
import csv
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from main import show_entries, save_to_csv, parse_arguments

@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file with test data."""
    csv_file = tmp_path / "test.csv"
    headers = ["Timestamp", "Amount", "Category", "Account"]
    data = [
        ["2025-01-16 13:00:00", "50", "food", "cash"],
        ["2025-01-16 13:30:00", "100", "entertainment", "crypto wallet"]
    ]
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    return str(csv_file)

def test_argument_parsing_write_command(monkeypatch):
    """Test parsing write command with CSV file."""
    test_args = ['script.py', 'write', 'test.csv']
    monkeypatch.setattr(sys, 'argv', test_args)
    
    args = parse_arguments()
    assert args.command == 'write'
    assert args.csv_file == 'test.csv'

def test_argument_parsing_show_command(monkeypatch):
    """Test parsing show command with CSV file."""
    test_args = ['script.py', 'show', 'test.csv']
    monkeypatch.setattr(sys, 'argv', test_args)
    
    args = parse_arguments()
    assert args.command == 'show'
    assert args.csv_file == 'test.csv'

def test_argument_parsing_csv_only(monkeypatch):
    """Test parsing with just CSV file (should default to write)."""
    test_args = ['script.py', 'test.csv']
    monkeypatch.setattr(sys, 'argv', test_args)
    
    args = parse_arguments()
    assert args.command == 'write'
    assert args.csv_file == 'test.csv'

def test_argument_parsing_no_args(monkeypatch, capsys):
    """Test parsing with no arguments (should show error)."""
    test_args = ['script.py']
    monkeypatch.setattr(sys, 'argv', test_args)
    
    with pytest.raises(SystemExit):
        parse_arguments()
    
    captured = capsys.readouterr()
    assert "error: CSV file is required for write command" in captured.err

def test_argument_parsing_help_command(monkeypatch, capsys):
    """Test help command output."""
    test_args = ['script.py', 'help']
    monkeypatch.setattr(sys, 'argv', test_args)
    
    with pytest.raises(SystemExit) as e:
        parse_arguments()
    assert e.value.code == 0
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check if help output contains essential information
    assert "Available Commands" in output
    assert "write" in output
    assert "show" in output
    assert "Description" in output
    assert "Usage" in output
    assert "Example" in output
    assert "--categories" in output

def test_argument_parsing_invalid_command(monkeypatch, capsys):
    """Test parsing with invalid command."""
    test_args = ['script.py', 'invalid']
    monkeypatch.setattr(sys, 'argv', test_args)
    
    args = parse_arguments()
    assert args.command == 'write'  # Should default to write
    assert args.csv_file == 'invalid'  # Invalid command becomes the CSV file

def test_show_entries_with_data(sample_csv):
    """Test showing entries from a CSV file with data."""
    output = StringIO()
    with redirect_stdout(output):
        show_entries(sample_csv)
    
    result = output.getvalue()
    
    # Check that output contains our test data
    assert "50" in result
    assert "food" in result
    assert "cash" in result
    assert "Total entries: 2" in result

def test_show_entries_empty_file(tmp_path):
    """Test showing entries from an empty CSV file."""
    empty_csv = tmp_path / "empty.csv"
    with open(empty_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Amount", "Category", "Account"])
    
    output = StringIO()
    with redirect_stdout(output):
        show_entries(str(empty_csv))
    
    result = output.getvalue()
    assert "No entries found" in result

def test_show_entries_nonexistent_file():
    """Test showing entries from a non-existent file."""
    output = StringIO()
    with redirect_stdout(output):
        show_entries("nonexistent.csv")
    
    result = output.getvalue()
    assert "Error: File nonexistent.csv does not exist" in result

def test_show_entries_invalid_csv(tmp_path):
    """Test showing entries from an invalid CSV file."""
    invalid_csv = tmp_path / "invalid.csv"
    with open(invalid_csv, 'w') as f:
        f.write('Header1,Header2\n1,2,3,4\n')  # Inconsistent number of columns
    
    output = StringIO()
    with redirect_stdout(output):
        show_entries(str(invalid_csv))
    
    result = output.getvalue()
    assert "Error: Invalid CSV format" in result or "Error: CSV file is empty or invalid" in result

def test_write_and_show_workflow(tmp_path):
    """Test the complete workflow of writing and then showing entries."""
    csv_file = tmp_path / "workflow_test.csv"
    
    # First write some data
    headers = ["Amount", "Category", "Account"]
    data = ["100", "food", "cash"]
    save_to_csv(str(csv_file), headers, data)
    
    # Then try to show it
    output = StringIO()
    with redirect_stdout(output):
        show_entries(str(csv_file))
    
    result = output.getvalue()
    
    # Verify our data is shown
    assert "100" in result
    assert "food" in result
    assert "cash" in result
    assert "Total entries: 1" in result
