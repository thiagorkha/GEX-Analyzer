# GEX Analyzer - Testing Guide

## Test Structure

```
tests/
├── __init__.py
├── test_gex_calculator.py    # Calculator tests
├── test_patterns.py          # Pattern detection tests
└── [Additional test files]
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_gex_calculator.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_gex_calculator.py::TestGexCalculator -v
```

### Run Specific Test
```bash
pytest tests/test_gex_calculator.py::TestGexCalculator::test_calculate_gex -v
```

### Run with Coverage
```bash
pytest tests/ --cov=backend --cov-report=html
```

## Test Coverage

### GEX Calculator Tests (`test_gex_calculator.py`)

#### TestGexCalculator
- `test_calculator_initialization`: Verify calculator setup
- `test_calculate_gex`: Main GEX calculation test
- `test_gamma_exposure_calculation`: Gamma exposure correctness
- `test_empty_input`: Handle edge cases
- `test_delta_calculation`: Delta calculation accuracy
- `test_gamma_calculation`: Gamma calculation accuracy
- `test_gex_levels_analysis`: GEX level statistics

#### TestBlackScholes
- `test_bs_call_price`: Call option pricing
- `test_bs_put_price`: Put option pricing
- `test_itm_call_vs_otm`: Price comparison

### Pattern Detection Tests (`test_patterns.py`)

#### TestPatternDetector
- `test_detector_initialization`: Pattern detector setup
- `test_detect_patterns`: Pattern detection basic
- `test_pattern_attributes`: Pattern object structure
- `test_uptrend_detection`: Bullish pattern detection
- `test_downtrend_detection`: Bearish pattern detection
- `test_pattern_classification`: Pattern classification accuracy
- `test_confidence_bounds`: Confidence value validation
- `test_empty_data_handling`: Edge case handling

## Test Data

### Sample OHLC Data
```python
{
    'open': [100, 101, 102, ...],
    'high': [102, 103, 104, ...],
    'low': [99, 100, 101, ...],
    'close': [101, 102, 103, ...],
    'volume': [1000, 1100, 1200, ...]
}
```

### Sample GEX Data
```python
{
    'spot_price': 100.0,
    'strike_prices': [95, 100, 105, 110],
    'gamma_values': [0.01, 0.015, 0.012, 0.008],
    'open_interest': [1000, 5000, 4000, 1000]
}
```

## Test Fixtures

### Fixtures in test_gex_calculator.py
- `calculator`: Fresh GexCalculator instance
- `sample_data`: Pre-configured test data

### Fixtures in test_patterns.py
- `detector`: Fresh PatternDetector instance
- `sample_ohlc_data`: Pre-configured OHLC data

## Assertions & Validations

### Common Assertions
```python
# Value comparisons
assert result > 0
assert result == expected_value
assert 0 <= confidence <= 1

# Type checks
assert isinstance(result, list)
assert hasattr(object, 'attribute')

# List operations
assert len(patterns) > 0
assert 'key' in dictionary
```

## Test Configuration

### pytest.ini (if needed)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v
```

## Performance Testing

### Basic Performance Test
```python
import time

def test_gex_calculation_performance(calculator):
    start = time.time()
    # Run calculation
    calculator.calculate_gex(...)
    elapsed = time.time() - start
    
    # Assert completion time
    assert elapsed < 1.0  # Should complete in < 1 second
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: pytest tests/ --cov
```

## Mocking & Patching

### Example Mock Test
```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    with patch('backend.gex.calculator.GexCalculator') as mock:
        mock_calc = MagicMock()
        mock_calc.calculate_gex.return_value = MagicMock(gex_long=100)
        
        # Use mock in test
        result = mock_calc.calculate_gex(...)
        assert result.gex_long == 100
```

## Integration Tests

### API Integration Test
```python
def test_api_analyze_endpoint(client):
    response = client.post('/api/analyze', json={
        'ohlc_data': [...]
    })
    
    assert response.status_code == 200
    assert 'gex_analysis' in response.json
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Coverage**: Aim for >80% code coverage
4. **Speed**: Tests should run quickly
5. **Fixtures**: Use fixtures for repeated setup
6. **Assertions**: Multiple small assertions per test
7. **Documentation**: Comment complex test logic

## Debugging Tests

### Run with Print Statements
```bash
pytest tests/ -s
```

### Run with PDB Debugger
```bash
pytest tests/ --pdb
```

### Verbose Output
```bash
pytest tests/ -vv
```

## Test Metrics

### Coverage Report
```bash
pytest tests/ --cov=backend --cov-report=term-missing
```

### Test Execution Time
```bash
pytest tests/ --durations=10
```

## Adding New Tests

### Step 1: Create Test File
```python
# tests/test_my_module.py
import pytest
from backend.my_module import MyClass

class TestMyClass:
    @pytest.fixture
    def instance(self):
        return MyClass()
    
    def test_something(self, instance):
        result = instance.method()
        assert result == expected
```

### Step 2: Run Test
```bash
pytest tests/test_my_module.py -v
```

### Step 3: Check Coverage
```bash
pytest tests/test_my_module.py --cov=backend.my_module
```

## Known Issues & Workarounds

### Issue: scipy import error
**Solution**: Install with `pip install scipy`

### Issue: Test timeouts
**Solution**: Add timeout to pytest: `pytest tests/ --timeout=300`

### Issue: Flaky tests
**Solution**: Use pytest-repeat: `pytest tests/ --count=5`

## Resources

- Pytest Documentation: https://docs.pytest.org/
- Python unittest: https://docs.python.org/3/library/unittest.html
- Coverage.py: https://coverage.readthedocs.io/
- Mock Library: https://docs.python.org/3/library/unittest.mock.html

