import pytest
import os
import yaml
from main import load_categories, get_headers, save_to_csv

@pytest.fixture
def category_file(tmp_path):
    """Create a temporary category file for testing."""
    categories = {
        'Category': ['food', 'transport', 'entertainment'],
        'Account': ['savings', 'checking', 'cash']
    }
    
    category_file = tmp_path / "test_categories.yaml"
    with open(category_file, 'w') as f:
        yaml.dump(categories, f)
    
    return str(category_file)

@pytest.fixture
def csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test.csv"
    with open(csv_file, 'w', newline='') as f:
        f.write("Timestamp,Amount,Category,Account\n")
    return str(csv_file)

def test_load_categories(category_file):
    """Test loading categories from YAML file."""
    categories = load_categories(category_file)
    
    assert 'Category' in categories
    assert 'Account' in categories
    assert len(categories['Category']) == 3
    assert len(categories['Account']) == 3
    assert 'food' in categories['Category']
    assert 'savings' in categories['Account']

def test_load_categories_missing_file():
    """Test loading categories with missing file."""
    categories = load_categories("nonexistent.yaml")
    assert categories == {}

def test_headers_match_categories(csv_file, category_file):
    """Test that CSV headers match category names."""
    headers = get_headers(csv_file)
    categories = load_categories(category_file)
    
    # Check if category columns in CSV have matching categories
    category_columns = set(categories.keys())
    header_set = set(headers)
    
    matching_categories = category_columns.intersection(header_set)
    assert len(matching_categories) > 0, "No matching categories found in headers"
    
    # Verify specific matches
    assert 'Category' in matching_categories
    assert 'Account' in matching_categories

def test_save_with_categories(tmp_path, category_file):
    """Test saving data with category values."""
    # Create test CSV
    csv_file = tmp_path / "test_save.csv"
    headers = ["Category", "Account", "Amount"]
    test_data = ["food", "savings", "100"]
    
    # Save the data
    save_to_csv(str(csv_file), headers, test_data)
    
    # Read back and verify
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 2  # Headers + one data row
    assert "Category,Account,Amount" in lines[0]
    assert "food,savings,100" in lines[1]

def test_invalid_category_file():
    """Test handling of invalid YAML file."""
    # Create invalid YAML file
    invalid_yaml = "invalid: - yaml: content:"
    with open("invalid.yaml", "w") as f:
        f.write(invalid_yaml)
    
    try:
        categories = load_categories("invalid.yaml")
        assert categories == {}, "Should return empty dict for invalid YAML"
    finally:
        # Cleanup
        os.remove("invalid.yaml")
