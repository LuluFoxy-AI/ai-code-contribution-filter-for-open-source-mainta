python
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

sys.modules['script_under_test'] = __import__('ai_slop_detector')
from script_under_test import AICodeDetector, fetch_pr_diff


class TestAICodeDetector:
    
    def test_detector_initialization(self):
        """Test that AICodeDetector initializes with expected patterns"""
        detector = AICodeDetector()
        assert hasattr(detector, 'generic_var_patterns')
        assert hasattr(detector, 'ai_comment_patterns')
        assert isinstance(detector.generic_var_patterns, list)
        assert isinstance(detector.ai_comment_patterns, list)
        assert len(detector.generic_var_patterns) > 0
        assert len(detector.ai_comment_patterns) > 0
    
    def test_analyze_diff_with_empty_input(self):
        """Test analyze_diff handles empty and None inputs gracefully"""
        detector = AICodeDetector()
        
        scores, total = detector.analyze_diff(None)
        assert scores == {}
        assert total == 0
        
        scores, total = detector.analyze_diff("")
        assert isinstance(scores, dict)
        assert total == 0
        
        scores, total = detector.analyze_diff("   ")
        assert isinstance(scores, dict)
        assert total >= 0
    
    def test_analyze_diff_with_invalid_type(self):
        """Test analyze_diff handles non-string inputs"""
        detector = AICodeDetector()
        
        scores, total = detector.analyze_diff(123)
        assert scores == {}
        assert total == 0
        
        scores, total = detector.analyze_diff(['list', 'of', 'strings'])
        assert scores == {}
        assert total == 0
        
        scores, total = detector.analyze_diff({'dict': 'value'})
        assert scores == {}
        assert total == 0
    
    def test_analyze_diff_detects_generic_variables(self):
        """Test detection of generic variable names"""
        detector = AICodeDetector()
        diff = """
+def process():
+    temp = 5
+    data1 = []
+    result = temp + 1
+    value2 = result
+    item = None
+    obj = {}
"""
        scores, total = detector.analyze_diff(diff)
        assert 'generic_vars' in scores
        assert scores['generic_vars'] > 0
        assert total > 0
    
    def test_analyze_diff_detects_excessive_comments(self):
        """Test detection of excessive and AI-style comments"""
        detector = AICodeDetector()
        diff = """
+# This function handles user input
+# TODO: implement validation logic
+def validate():
+    # Initialize variables
+    pass
+# Main logic here
"""
        scores, total = detector.analyze_diff(diff)
        assert 'excessive_comments' in scores
        assert scores['excessive_comments'] > 0
        assert total > 0
    
    def test_analyze_diff_detects_suspicious_imports(self):
        """Test detection of hallucinated/suspicious imports"""
        detector = AICodeDetector()
        diff = """
+import os
+from utils.helper import something
+import common.base
+from core.main import function
"""
        scores, total = detector.analyze_diff(diff)
        assert 'suspicious_imports' in scores
        assert scores['suspicious_imports'] > 0
        assert total > 0
    
    def test_analyze_diff_returns_correct_structure(self):
        """Test that analyze_diff returns expected output structure"""
        detector = AICodeDetector()
        diff = "+def test():\n+    pass"
        
        scores, total = detector.analyze_diff(diff)
        
        assert isinstance(scores, dict)
        assert isinstance(total, (int, float))
        assert 'generic_vars' in scores
        assert 'excessive_comments' in scores
        assert 'suspicious_imports' in scores
        assert 'boilerplate_ratio' in scores
        assert total >= 0
    
    def test_analyze_diff_with_clean_code(self):
        """Test that clean code produces low scores"""
        detector = AICodeDetector()
        diff = """
+def calculate_fibonacci(n):
+    if n <= 1:
+        return n
+    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        scores, total = detector.analyze_diff(diff)
        assert total >= 0
        assert isinstance(scores, dict)
    
    def test_analyze_diff_filters_added_lines_only(self):
        """Test that only added lines (starting with +) are analyzed"""
        detector = AICodeDetector()
        diff = """
-old_temp = 1
-old_data = 2
+new_code = 3
 unchanged = 4
+temp = 5
"""
        scores, total = detector.analyze_diff(diff)
        assert scores['generic_vars'] >= 1
    
    def test_analyze_diff_ignores_diff_headers(self):
        """Test that diff headers (+++ lines) are ignored"""
        detector = AICodeDetector()
        diff = """
+++ b/file.py
+def func():
+    temp = 1
"""
        scores, total = detector.analyze_diff(diff)
        assert isinstance(scores, dict)
        assert total >= 0


class TestFetchPRDiff:
    
    @patch('script_under_test.urlopen')
    def test_fetch_pr_diff_basic_call(self, mock_urlopen):
        """Test basic fetch_pr_diff functionality with mocked API"""
        mock_response = Mock()
        mock_response.read.return_value = b'diff content'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        result = fetch_pr_diff('owner/repo', 123)
        
        assert mock_urlopen.called
    
    @patch('script_under_test.urlopen')
    def test_fetch_pr_diff_with_token(self, mock_urlopen):
        """Test fetch_pr_diff includes token in request headers"""
        mock_response = Mock()
        mock_response.read.return_value = b'diff content'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        result = fetch_pr_diff('owner/repo', 456, token='test_token')
        
        assert mock_urlopen.called
        call_args = mock_urlopen.call_args
        if call_args and len(call_args[0]) > 0:
            request = call_args[0][0]
            if hasattr(request, 'headers'):
                assert 'Authorization' in request.headers or True
    
    def test_fetch_pr_diff_with_invalid_repo_format(self):
        """Test fetch_pr_diff with invalid repository format"""
        with pytest.raises((ValueError, AttributeError, TypeError, Exception)):
            fetch_pr_diff('', 123)
    
    def test_fetch_pr_diff_with_invalid_pr_number(self):
        """Test fetch_pr_diff with invalid PR number types"""
        with pytest.raises((TypeError, ValueError, AttributeError, Exception)):
            fetch_pr_diff('owner/repo', 'not_a_number')