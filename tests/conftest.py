import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_data_dir(temp_dir: Path) -> Path:
    """Create a temporary directory with sample data files."""
    data_dir = temp_dir / "data"
    data_dir.mkdir()
    
    # Create sample JSONL file
    sample_jsonl = data_dir / "sample.jsonl"
    with open(sample_jsonl, 'w') as f:
        f.write('{"task_id": "test_1", "prompt": "def hello():", "completion": "print(\\"Hello\\")"}\n')
        f.write('{"task_id": "test_2", "prompt": "def add(a, b):", "completion": "return a + b"}\n')
    
    return data_dir


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample pandas DataFrame for testing."""
    return pd.DataFrame({
        'task_id': ['test_1', 'test_2', 'test_3'],
        'prompt': ['def hello():', 'def add(a, b):', 'def multiply(x, y):'],
        'completion': ['print("Hello")', 'return a + b', 'return x * y'],
        'score': [0.8, 0.9, 0.7]
    })


@pytest.fixture
def sample_numpy_array() -> np.ndarray:
    """Create a sample numpy array for testing."""
    return np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])


@pytest.fixture
def mock_model() -> Mock:
    """Create a mock ML model for testing."""
    model = Mock()
    model.predict.return_value = np.array([0.8, 0.9, 0.7])
    model.fit.return_value = model
    return model


@pytest.fixture
def mock_tokenizer() -> Mock:
    """Create a mock tokenizer for testing."""
    tokenizer = Mock()
    tokenizer.encode.return_value = [101, 7592, 102]
    tokenizer.decode.return_value = "Hello World"
    tokenizer.vocab_size = 30522
    return tokenizer


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Create a sample configuration dictionary."""
    return {
        'model_name': 'test_model',
        'batch_size': 16,
        'max_length': 512,
        'temperature': 0.7,
        'top_p': 0.9,
        'device': 'cpu',
        'seed': 42
    }


@pytest.fixture
def mock_evaluation_result() -> Dict[str, Any]:
    """Create a mock evaluation result."""
    return {
        'pass_at_1': 0.75,
        'pass_at_10': 0.85,
        'total_samples': 100,
        'passed_samples': 75,
        'timeout_samples': 5,
        'error_samples': 20
    }


@pytest.fixture
def sample_code_snippets() -> Dict[str, str]:
    """Create sample code snippets for testing."""
    return {
        'python_function': '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
        '''.strip(),
        
        'python_class': '''
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
        '''.strip(),
        
        'java_function': '''
public int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
        '''.strip(),
        
        'cpp_function': '''
#include <iostream>
int main() {
    std::cout << "Hello World!" << std::endl;
    return 0;
}
        '''.strip()
    }


@pytest.fixture
def mock_dataset() -> Mock:
    """Create a mock dataset for testing."""
    dataset = Mock()
    dataset.__len__ = Mock(return_value=100)
    dataset.__getitem__ = Mock(side_effect=lambda i: {
        'task_id': f'test_{i}',
        'prompt': f'def function_{i}():',
        'completion': f'return {i}'
    })
    return dataset


@pytest.fixture
def mock_metrics() -> Mock:
    """Create mock metrics for testing."""
    metrics = Mock()
    metrics.compute.return_value = {
        'accuracy': 0.85,
        'precision': 0.82,
        'recall': 0.88,
        'f1': 0.85
    }
    return metrics


@pytest.fixture
def sample_jsonl_content() -> str:
    """Create sample JSONL content for testing."""
    return '''{"task_id": "HumanEval/0", "prompt": "def has_close_elements(numbers, threshold):\\n", "completion": "    for i in range(len(numbers)):\\n        for j in range(i+1, len(numbers)):\\n            if abs(numbers[i] - numbers[j]) < threshold:\\n                return True\\n    return False"}
{"task_id": "HumanEval/1", "prompt": "def separate_paren_groups(paren_string):\\n", "completion": "    result = []\\n    current_string = ''\\n    current_depth = 0\\n    for c in paren_string:\\n        if c == '(':\\n            current_depth += 1\\n            current_string += c\\n        elif c == ')':\\n            current_depth -= 1\\n            current_string += c\\n            if current_depth == 0:\\n                result.append(current_string)\\n                current_string = ''\\n    return result"}'''


@pytest.fixture
def mock_file_system(temp_dir: Path) -> Dict[str, Path]:
    """Create a mock file system structure for testing."""
    structure = {}
    
    # Create directories
    dirs = ['data', 'models', 'outputs', 'configs']
    for dir_name in dirs:
        dir_path = temp_dir / dir_name
        dir_path.mkdir()
        structure[dir_name] = dir_path
    
    # Create sample files
    files = {
        'config.json': '{"model": "test", "temperature": 0.7}',
        'sample.py': 'def hello(): print("Hello World")',
        'requirements.txt': 'pytest\\nnumpy\\npandas'
    }
    
    for file_name, content in files.items():
        file_path = temp_dir / file_name
        file_path.write_text(content)
        structure[file_name] = file_path
    
    return structure


@pytest.fixture(autouse=True)
def cleanup_env():
    """Automatically cleanup environment variables after each test."""
    original_env = os.environ.copy()
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_torch_model() -> Mock:
    """Create a mock PyTorch model for testing."""
    model = Mock()
    model.eval = Mock(return_value=model)
    model.train = Mock(return_value=model)
    model.forward = Mock(return_value=Mock(logits=Mock(shape=(1, 10))))
    model.parameters = Mock(return_value=iter([Mock(shape=(10, 5))]))
    return model


@pytest.fixture
def mock_huggingface_model() -> Mock:
    """Create a mock HuggingFace model for testing."""
    model = Mock()
    model.generate.return_value = Mock(sequences=[[101, 7592, 102]])
    model.config = Mock(vocab_size=30522, max_length=512)
    return model


# Markers for different test categories
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
]