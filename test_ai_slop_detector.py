python
#!/usr/bin/env python3
"""
Test suite for ai_slop_detector.py (AI Code Contribution Filter)
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
from script_under_test import AICodeDetector


class TestAICodeDetector:
    """Test suite for AICodeDetector class"""
    
    @pytest.fixture
    def detector(self):
        """Fixture to create a fresh AICodeDetector instance for each test"""
        return AICodeDetector()
    
    def test_detector_initialization(self, detector):
        """Test that AICodeDetector initializes with expected attributes"""
        assert hasattr(detector, 'generic_var_patterns')
        assert hasattr(detector, 'comment_markers')
        assert hasattr(detector, 'ai_phrases')
        assert isinstance(detector.generic_var_patterns, list)
        assert isinstance(detector.comment_markers, list)
        assert isinstance(detector.ai_phrases, list)
        assert len(detector.generic_var_patterns) > 0
        assert len(detector.ai_phrases) > 0
    
    def test_analyze_diff_with_empty_string(self, detector):
        """Test analyze_diff with empty diff content"""
        result = detector.analyze_diff("")
        assert isinstance(result, dict)
        assert 'lines_analyzed' in result.get('details', {})
        assert result['details']['lines_analyzed'] == 0
    
    def test_analyze_diff_with_no_added_lines(self, detector):
        """Test analyze_diff with diff containing no added lines"""
        diff_content = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
-old line
 unchanged line"""
        result = detector.analyze_diff(diff_content)
        assert isinstance(result, dict)
        assert result['details']['lines_analyzed'] == 0
    
    def test_analyze_diff_with_clean_code(self, detector):
        """Test analyze_diff with clean, non-AI-looking code"""
        diff_content = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,5 @@
+def calculate_total(prices):
+    return sum(prices)
+"""
        result = detector.analyze_diff(diff_content)
        assert isinstance(result, dict)
        assert 'score' in result or 'total_score' in result or 'generic_variable_score' in result.get('details', {})
        assert 'details' in result
        assert result['details']['lines_analyzed'] == 2
    
    def test_analyze_diff_with_ai_patterns(self, detector):
        """Test analyze_diff with code containing AI-like patterns"""
        diff_content = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,8 @@
+# Initialize the data structure
+def helper_function(data1, temp, result):
+    # This function processes the data
+    value = data1
+    # TODO: implement error handling
+    return result
+"""
        result = detector.analyze_diff(diff_content)
        assert isinstance(result, dict)
        assert 'details' in result
        assert result['details']['lines_analyzed'] == 6
        assert 'generic_variable_score' in result['details']
        assert 'comment_ratio' in result['details']
        assert 'ai_phrase_score' in result['details']
    
    def test_analyze_diff_output_structure(self, detector):
        """Test that analyze_diff returns properly structured output"""
        diff_content = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
+x = 1
+"""
        result = detector.analyze_diff(diff_content)
        assert isinstance(result, dict)
        assert 'details' in result
        details = result['details']
        assert isinstance(details, dict)
        assert 'lines_analyzed' in details
        assert isinstance(details['lines_analyzed'], int)
    
    def test_check_generic_variables_with_generic_names(self, detector):
        """Test _check_generic_variables with lines containing generic variable names"""
        lines = [
            "temp = 5",
            "data1 = []",
            "result = calculate()",
            "value = get_value()",
            "item = items[0]"
        ]
        score = detector._check_generic_variables(lines)
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_check_generic_variables_with_specific_names(self, detector):
        """Test _check_generic_variables with lines containing specific variable names"""
        lines = [
            "user_name = 'John'",
            "total_price = 100",
            "customer_id = 42"
        ]
        score = detector._check_generic_variables(lines)
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_check_generic_variables_with_empty_list(self, detector):
        """Test _check_generic_variables with empty list"""
        score = detector._check_generic_variables([])
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_calculate_comment_ratio_with_many_comments(self, detector):
        """Test _calculate_comment_ratio with high comment density"""
        lines = [
            "# This is a comment",
            "x = 1",
            "# Another comment",
            "# Yet another comment",
            "y = 2"
        ]
        ratio = detector._calculate_comment_ratio(lines)
        assert isinstance(ratio, (int, float))
        assert ratio >= 0
        assert ratio <= 100
    
    def test_calculate_comment_ratio_with_no_comments(self, detector):
        """Test _calculate_comment_ratio with no comments"""
        lines = [
            "x = 1",
            "y = 2",
            "z = x + y"
        ]
        ratio = detector._calculate_comment_ratio(lines)
        assert isinstance(ratio, (int, float))
        assert ratio >= 0
        assert ratio <= 100
    
    def test_calculate_comment_ratio_with_empty_list(self, detector):
        """Test _calculate_comment_ratio with empty list"""
        ratio = detector._calculate_comment_ratio([])
        assert isinstance(ratio, (int, float))
        assert ratio >= 0
    
    def test_check_ai_phrases_with_ai_language(self, detector):
        """Test _check_ai_phrases with lines containing AI-typical phrases"""
        lines = [
            "# Initialize the database connection",
            "# This function handles user input",
            "# Helper function to process data",
            "# TODO: implement validation"
        ]
        score = detector._check_ai_phrases(lines)
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_check_ai_phrases_with_normal_language(self, detector):
        """Test _check_ai_phrases with lines containing normal code comments"""
        lines = [
            "# Connect to database",
            "# Process user request",
            "# Return results"
        ]
        score = detector._check_ai_phrases(lines)
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_check_style_consistency(self, detector):
        """Test _check_style_consistency with various code styles"""
        lines = [
            "def function_one():",
            "    x = 1",
            "def function_two():",
            "    y = 2"
        ]
        score = detector._check_style_consistency(lines)
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_check_style_consistency_with_empty_list(self, detector):
        """Test _check_style_consistency with empty list"""
        score = detector._check_style_consistency([])
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_create_result_structure(self, detector):
        """Test _create_result returns properly formatted result"""
        result = detector._create_result(50.0, "Medium risk", {"test": 1})
        assert isinstance(result, dict)
    
    def test_calculate_confidence(self, detector):
        """Test _calculate_confidence returns valid confidence score"""
        metrics = {
            'generic_vars': 50,
            'comments': 30,
            'ai_phrases': 40,
            'style': 60
        }
        confidence = detector._calculate_confidence(metrics)
        assert isinstance(confidence, (int, float, str))
    
    def test_get_assessment(self, detector):
        """Test _get_assessment returns appropriate assessment string"""
        assessment_low = detector._get_assessment(20)
        assessment_high = detector._get_assessment(80)
        assert isinstance(assessment_low, str)
        assert isinstance(assessment_high, str)
        assert len(assessment_low) > 0
        assert len(assessment_high) > 0