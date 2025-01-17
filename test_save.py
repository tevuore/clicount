import pytest
import os
import csv
from datetime import datetime
from unittest.mock import patch
from main import save_to_csv, get_user_input, get_category_value, flatten_categories, load_categories

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
            ['public', 'taxi', 'train'],
            'entertainment',
            ['movie', 'concert', 'sports'],
            'utilities',
            'other'
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
    with patch('builtins.input', return_value='5'):  # 'food'
        result = get_category_value('Category', test_categories)
        assert result == 'food'
    
    # Test parent category
    with patch('builtins.input', return_value='7'):  # 'transport'
        result = get_category_value('Category', test_categories)
        assert result == 'transport'
    
    # Test subcategory
    with patch('builtins.input', return_value='9'):  # 'transport.taxi'
        result = get_category_value('Category', test_categories)
        assert result == 'transport.taxi'
    
    # Test entertainment subcategory
    with patch('builtins.input', return_value='3'):  # 'entertainment.movie'
        result = get_category_value('Category', test_categories)
        assert result == 'entertainment.movie'

def test_get_category_value_invalid_input(test_categories):
    """Test handling of invalid input when getting category value."""
    # Test invalid number then valid number
    with patch('builtins.input', side_effect=['0', '13', '1']):  # 'entertainment'
        result = get_category_value('Category', test_categories)
        assert result == 'entertainment'
    
    # Test non-numeric input then valid number
    with patch('builtins.input', side_effect=['abc', '2']):
        result = get_category_value('Account', test_categories)
        assert result == 'checking'

def test_get_user_input(test_categories):
    """Test getting user input for all fields."""
    headers = ["Name", "Category", "Account", "Amount"]
    
    # Mock inputs:
    # - name (free form)
    # - category (transport.taxi)
    # - account (crypto wallet)
    # - amount (free form)
    with patch('builtins.input', side_effect=['John Doe', '9', '3', '50.00']):  # 'transport.taxi' is at index 9
        answers = get_user_input(headers, test_categories)
        assert answers == ['John Doe', 'transport.taxi', 'crypto wallet', '50.00']

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
        'entertainment',
        'entertainment.concert',
        'entertainment.movie',
        'entertainment.sports',
        'food',
        'other',
        'transport',
        'transport.public',
        'transport.taxi',
        'transport.train',
        'utilities'
    ]
    
    assert flat_categories == expected_categories  # Order matters since we sort

def test_flatten_categories_simple():
    """Test flattening of simple categories without nesting."""
    categories = {
        'Category': [
            'food',
            'utilities',
            'other'
        ]
    }
    
    result = flatten_categories(categories)
    expected = ['food', 'other', 'utilities']
    assert result == expected

def test_flatten_categories_with_subcategories():
    """Test flattening of categories with one level of subcategories."""
    categories = {
        'Category': [
            'food',
            'transport',
            ['public', 'taxi', 'train'],
            'utilities'
        ]
    }
    
    result = flatten_categories(categories)
    expected = [
        'food',
        'transport',
        'transport.public',
        'transport.taxi',
        'transport.train',
        'utilities'
    ]
    assert result == expected

def test_flatten_categories_multiple_parents():
    """Test flattening of multiple parent categories with subcategories."""
    categories = {
        'Category': [
            'food',
            'transport',
            ['public', 'taxi', 'train'],
            'entertainment',
            ['movie', 'concert', 'sports'],
            'utilities'
        ]
    }
    
    result = flatten_categories(categories)
    expected = [
        'entertainment',
        'entertainment.concert',
        'entertainment.movie',
        'entertainment.sports',
        'food',
        'transport',
        'transport.public',
        'transport.taxi',
        'transport.train',
        'utilities'
    ]
    assert result == expected

def test_flatten_categories_empty():
    """Test flattening of empty categories."""
    categories = {
        'Category': []
    }
    
    result = flatten_categories(categories)
    assert result == []

def test_flatten_categories_invalid_input():
    """Test flattening with invalid input types."""
    # Test with None
    assert flatten_categories(None) == []
    
    # Test with empty dict
    assert flatten_categories({}) == []
    
    # Test with invalid category structure
    categories = {
        'Category': 'not a list'
    }
    assert flatten_categories(categories) == []

def test_get_category_value_shows_all_options(monkeypatch, capsys):
    """Test that get_category_value shows all available options and handles selection."""
    categories = {'Category': ['food', 'transport', 'transport.public', 'transport.taxi']}
    
    # Mock user input to select option 2 (transport)
    inputs = iter(['2'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
    result = get_category_value('Category', categories)
    
    # Check the output shows all options
    captured = capsys.readouterr()
    assert 'food' in captured.out
    assert 'transport' in captured.out
    assert 'transport.public' in captured.out
    assert 'transport.taxi' in captured.out
    
    # Check the selected value is returned
    assert result == 'transport'

def test_load_categories_simple(tmp_path):
    """Test loading of simple categories without nesting."""
    # Create a test YAML file
    categories_file = tmp_path / "test_categories.yaml"
    categories_content = """
Category:
  - food
  - utilities
  - other
Account:
  - savings
  - checking
  - cash
"""
    categories_file.write_text(categories_content)
    
    # Load and verify
    result = load_categories(str(categories_file))
    expected = {
        'Category': sorted(['food', 'utilities', 'other']),
        'Account': sorted(['savings', 'checking', 'cash'])
    }
    assert result == expected

def test_load_categories_with_subcategories(tmp_path):
    """Test loading of categories with one level of subcategories."""
    categories_file = tmp_path / "test_categories.yaml"
    categories_content = """
Category:
  - food
  - transport:
      - public
      - taxi
      - train
  - utilities

Account:
  - savings
  - checking
"""
    categories_file.write_text(categories_content)
    
    result = load_categories(str(categories_file))
    expected = {
        'Category': sorted(['food', 'transport', 'transport.public', 'transport.taxi', 'transport.train', 'utilities']),
        'Account': sorted(['savings', 'checking'])
    }
    assert result == expected

def test_load_categories_deep_nesting(tmp_path):
    """Test loading of deeply nested categories."""
    categories_file = tmp_path / "test_categories.yaml"
    categories_content = """
Category:
  - food
  - transport:
      - public
      - taxi
      - train
  - entertainment:
      - magazine:
          - Linux Format
          - PC World
      - movie
      - concert
  - utilities
"""
    categories_file.write_text(categories_content)
    
    result = load_categories(str(categories_file))
    expected = {
        'Category': sorted([
            'food',
            'transport',
            'transport.public',
            'transport.taxi',
            'transport.train',
            'entertainment',
            'entertainment.magazine',
            'entertainment.magazine.Linux Format',
            'entertainment.magazine.PC World',
            'entertainment.movie',
            'entertainment.concert',
            'utilities'
        ])
    }
    assert result == expected

def test_load_categories_file_not_found():
    """Test loading categories when file doesn't exist."""
    result = load_categories('nonexistent.yaml')
    assert result == {}

def test_load_categories_invalid_yaml(tmp_path):
    """Test loading categories with invalid YAML content."""
    categories_file = tmp_path / "test_categories.yaml"
    categories_content = """
Category:
  - food
  - transport:
    - public
    - invalid:
      - yaml
    structure
"""
    categories_file.write_text(categories_content)
    
    result = load_categories(str(categories_file))
    assert result == {}

def test_load_categories_empty_file(tmp_path):
    """Test loading categories from an empty file."""
    categories_file = tmp_path / "test_categories.yaml"
    categories_file.write_text("")
    
    result = load_categories(str(categories_file))
    assert result == {}

def test_load_categories_matches_flatten_format(tmp_path):
    """Test that loaded categories match the format expected by flatten_categories."""
    categories_file = tmp_path / "test_categories.yaml"
    categories_content = """
Category:
  - food
  - transport
  - public
  - taxi
  - entertainment
  - movie
  - concert
  - utilities
"""
    categories_file.write_text(categories_content)
    
    # First load the categories
    categories = load_categories(str(categories_file))
    
    # Then try to flatten them
    flat_categories = flatten_categories({'Category': categories['Category']})
    
    # Verify we get the expected flattened structure
    expected_flat = [
        'concert',
        'entertainment',
        'food',
        'movie',
        'public',
        'taxi',
        'transport',
        'utilities'
    ]
    assert flat_categories == expected_flat
