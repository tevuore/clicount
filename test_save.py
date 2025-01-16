import pytest
import os
import csv
from datetime import datetime
from unittest.mock import patch
from main import save_to_csv, get_user_input, get_category_value, flatten_categories

@pytest.fixture
def test_csv(tmp_path):
    """Create a test CSV file."""
    csv_file = tmp_path / "test.csv"
    return str(csv_file)

@pytest.fixture
def test_categories():
    """Sample categories for testing."""
    return {
        'Category': [
            'food',
            'transport',
            {
                'entertainment': [
                    'movie',
                    {
                        'magazine': [
                            'Linux Format'
                        ]
                    }
                ]
            }
        ],
        'Account': [
            'savings',
            'checking',
            'cash',
            'crypto wallet'
        ]
    }

def test_save_new_file(test_csv):
    """Test saving to a new file."""
    headers = ["Amount", "Category", "Account"]
    data = ["100", "food", "cash"]
    
    save_to_csv(test_csv, headers, data)
    
    assert os.path.exists(test_csv), "CSV file should be created"
    
    with open(test_csv, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Check headers (including timestamp)
        assert rows[0] == ["Timestamp"] + headers
        
        # Check data (excluding timestamp as it's dynamic)
        assert rows[1][1:] == data

def test_save_append(test_csv):
    """Test appending multiple entries."""
    headers = ["Amount", "Category", "Account"]
    entries = [
        ["100", "food", "cash"],
        ["200", "transport", "checking"]
    ]
    
    # Save multiple entries
    for data in entries:
        save_to_csv(test_csv, headers, data)
    
    with open(test_csv, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        assert len(rows) == 3  # Headers + 2 entries
        assert rows[0] == ["Timestamp"] + headers  # Check headers
        assert rows[1][1:] == entries[0]  # Check first entry
        assert rows[2][1:] == entries[1]  # Check second entry

def test_save_newline_handling(test_csv):
    """Test handling of newlines when saving."""
    headers = ["Amount", "Category", "Account"]
    data = ["100", "food", "cash"]
    
    # First create file without newline
    with open(test_csv, 'w') as f:
        f.write("Timestamp,Amount,Category,Account")  # No newline
    
    # Now try to append
    save_to_csv(test_csv, headers, data)
    
    with open(test_csv, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        
        assert len(lines) >= 2, "Should have at least 2 lines"
        assert lines[0] == "Timestamp,Amount,Category,Account"
        assert "food" in lines[1] and "cash" in lines[1]
        assert content.endswith('\n'), "File should end with newline"

def test_get_category_value(test_categories):
    """Test getting category value from predefined options."""
    # Test simple category
    with patch('builtins.input', return_value='1'):
        result = get_category_value('Category', test_categories)
        assert result == 'food'
    
    # Test nested category (entertainment.magazine.Linux Format)
    with patch('builtins.input', return_value='4'):  # Position of entertainment.magazine.Linux Format
        result = get_category_value('Category', test_categories)
        assert result == 'entertainment.magazine.Linux Format'

def test_get_category_value_invalid_input(test_categories):
    """Test handling of invalid input when getting category value."""
    # Test invalid number then valid number
    with patch('builtins.input', side_effect=['0', '6', '1']):
        result = get_category_value('Category', test_categories)
        assert result == 'food'
    
    # Test non-numeric input then valid number
    with patch('builtins.input', side_effect=['abc', '2']):
        result = get_category_value('Account', test_categories)
        assert result == 'checking'

def test_get_user_input(test_categories):
    """Test getting user input for all fields."""
    headers = ["Name", "Category", "Account", "Amount"]
    
    # Mock inputs: 
    # - name (free form)
    # - category (entertainment.magazine.Linux Format)
    # - account (crypto wallet)
    # - amount (free form)
    with patch('builtins.input', side_effect=['John Doe', '4', '4', '50.00']):
        answers = get_user_input(headers, test_categories)
        assert answers == ['John Doe', 'entertainment.magazine.Linux Format', 'crypto wallet', '50.00']

def test_save_with_timestamp(test_csv):
    """Test that saved entries include correct timestamp."""
    headers = ["Amount", "Category", "Account"]
    data = ["100", "food", "cash"]
    
    # Get current time for comparison
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    save_to_csv(test_csv, headers, data)
    
    with open(test_csv, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Check timestamp format and approximate value
        timestamp = rows[1][0]
        assert timestamp.startswith(current_time), "Timestamp should match current time"

def test_flatten_categories(test_categories):
    """Test flattening of hierarchical categories."""
    flat_categories = flatten_categories({'Category': test_categories['Category']})
    
    expected_categories = [
        'food',
        'transport',
        'entertainment.movie',
        'entertainment.magazine.Linux Format'
    ]
    
    assert set(flat_categories) == set(expected_categories)
