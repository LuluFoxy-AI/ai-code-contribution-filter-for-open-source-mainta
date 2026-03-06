#!/usr/bin/env python3
"""
AI Code Contribution Filter - Analyzes pull requests for AI-generated code patterns
Helps open source maintainers identify low-quality AI-generated contributions

Usage:
    python ai_code_filter.py --diff-file pr_diff.txt
    python ai_code_filter.py --github-pr owner/repo/123 --token YOUR_TOKEN
"""

import re
import sys
import json
import argparse
from collections import Counter
from typing import Dict, List, Tuple


class AICodeDetector:
    """Detects patterns commonly found in AI-generated code"""
    
    def __init__(self):
        # Patterns that indicate AI-generated code
        self.generic_var_patterns = [
            r'\btemp\d*\b', r'\bdata\d*\b', r'\bresult\d*\b',
            r'\bvalue\d*\b', r'\bitem\d*\b', r'\bobj\d*\b'
        ]
        
        # AI models tend to over-comment
        self.comment_markers = ['//', '#', '/*', '*/', '<!--', '-->']
        
        # Common AI-generated phrases
        self.ai_phrases = [
            'initialize the', 'create a new', 'set up the',
            'this function', 'this method', 'helper function',
            'utility function', 'TODO: implement', 'FIXME:'
        ]

    def analyze_diff(self, diff_content: str) -> Dict:
        """Analyze a git diff for AI-generated patterns"""
        lines = diff_content.split('\n')
        added_lines = [l[1:] for l in lines if l.startswith('+') and not l.startswith('+++')]
        
        if not added_lines:
            return self._create_result(0, "No added lines found", {})
        
        # Calculate various metrics
        generic_var_score = self._check_generic_variables(added_lines)
        comment_ratio = self._calculate_comment_ratio(added_lines)
        ai_phrase_score = self._check_ai_phrases(added_lines)
        style_consistency = self._check_style_consistency(added_lines)
        
        # Weighted scoring (0-100)
        total_score = (
            generic_var_score * 0.3 +
            comment_ratio * 0.25 +
            ai_phrase_score * 0.25 +
            (100 - style_consistency) * 0.2
        )
        
        confidence = self._calculate_confidence({
            'generic_vars': generic_var_score,
            'comments': comment_ratio,
            'ai_phrases': ai_phrase_score,
            'style': style_consistency
        })
        
        details = {
            'generic_variable_score': round(generic_var_score, 2),
            'comment_ratio': round(comment_ratio, 2),
            'ai_phrase_score': round(ai_phrase_score, 2),
            'style_consistency': round(style_consistency, 2),
            'lines_analyzed': len(added_lines)
        }
        
        assessment = self._get_assessment(total_score)
        
        return self._create_result(total_score, assessment, details, confidence)

    def _check_generic_variables(self, lines: List[str]) -> float:
        """Check for generic variable names (higher = more generic)"""
        matches = 0
        for line in lines:
            for pattern in self.generic_var_patterns:
                matches += len(re.findall(pattern, line, re.IGNORECASE))
        return min(100, (matches / max(len(lines), 1)) * 200)

    def _calculate_comment_ratio(self, lines: List[str]) -> float:
        """Calculate comment-to-code ratio (higher = more comments)"""
        comment_lines = sum(1 for line in lines if any(m in line for m in self.comment_markers))
        ratio = comment_lines / max(len(lines), 1)
        # AI code often has 30%+ comments
        return min(100, ratio * 250)

    def _check_ai_phrases(self, lines: List[str]) -> float:
        """Check for common AI-generated phrases"""
        text = ' '.join(lines).lower()
        matches = sum(1 for phrase in self.ai_phrases if phrase in text)
        return min(100, (matches / max(len(self.ai_phrases), 1)) * 300)

    def _check_style_consistency(self, lines: List[str]) -> float:
        """Check code style consistency (lower = less consistent)"""
        indent_styles = []
        for line in lines:
            if line and line[0] in [' ', '\t']:
                indent_styles.append('tab' if line[0] == '\t' else 'space')
        
        if not indent_styles:
            return 50
        
        counter = Counter(indent_styles)
        most_common_ratio = counter.most_common(1)[0][1] / len(indent_styles)
        return most_common_ratio * 100

    def _calculate_confidence(self, metrics: Dict) -> float:
        """Calculate confidence level based on metric agreement"""
        high_scores = sum(1 for v in metrics.values() if v > 60)
        return min(100, (high_scores / len(metrics)) * 100)

    def _get_assessment(self, score: float) -> str:
        """Get human-readable assessment"""
        if score < 30:
            return "Low likelihood of AI generation - appears human-written"
        elif score < 60:
            return "Moderate likelihood - review recommended"
        else:
            return "High likelihood of AI generation - careful review needed"

    def _create_result(self, score: float, assessment: str, details: Dict, confidence: float = 0) -> Dict:
        """Create standardized result dictionary"""
        return {
            'ai_likelihood_score': round(score, 2),
            'confidence': round(confidence, 2),
            'assessment': assessment,
            'details': details,
            'recommendation': 'REVIEW' if score > 50 else 'APPROVE'
        }


def main():
    parser = argparse.ArgumentParser(
        description='AI Code Contribution Filter - Detect AI-generated code in PRs'
    )
    parser.add_argument('--diff-file', help='Path to diff file')
    parser.add_argument('--output', default='json', choices=['json', 'text'], help='Output format')
    
    args = parser.parse_args()
    
    if not args.diff_file:
        print("Error: --diff-file is required", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(args.diff_file, 'r', encoding='utf-8') as f:
            diff_content = f.read()
    except FileNotFoundError:
        print(f"Error: File {args.diff_file} not found", file=sys.stderr)
        sys.exit(1)
    
    detector = AICodeDetector()
    result = detector.analyze_diff(diff_content)
    
    if args.output == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(f"\nAI Code Detection Results")
        print(f"={'=' * 50}")
        print(f"AI Likelihood Score: {result['ai_likelihood_score']}/100")
        print(f"Confidence: {result['confidence']}%")
        print(f"Assessment: {result['assessment']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"\nDetails:")
        for key, value in result['details'].items():
            print(f"  {key}: {value}")


if __name__ == '__main__':
    main()