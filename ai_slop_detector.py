python
#!/usr/bin/env python3
"""
AI Code Contribution Filter - Detects AI-generated code patterns in pull requests
Helps open source maintainers identify low-quality AI slop submissions

Usage: python ai_slop_detector.py <github_repo> <pr_number> [--token GITHUB_TOKEN]
"""

import re
import sys
import json
import argparse
from collections import Counter
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class AICodeDetector:
    """Analyzes code diffs for AI-generated patterns"""
    
    def __init__(self):
        # Patterns commonly found in AI-generated code
        self.generic_var_patterns = [
            r'\btemp\d*\b', r'\bdata\d*\b', r'\bresult\d*\b',
            r'\bvalue\d*\b', r'\bitem\d*\b', r'\bobj\d*\b'
        ]
        
        # AI models love these comment patterns
        self.ai_comment_patterns = [
            r'#\s*TODO:.*implement.*logic',
            r'#\s*This (function|method|class) (handles|manages|processes)',
            r'//\s*Initialize.*variables?',
            r'#\s*Main.*logic.*here'
        ]
        
    def analyze_diff(self, diff_text):
        """Analyze a git diff for AI slop indicators"""
        if not diff_text or not isinstance(diff_text, str):
            return {}, 0
            
        scores = {
            'generic_vars': 0,
            'excessive_comments': 0,
            'suspicious_imports': 0,
            'boilerplate_ratio': 0
        }
        
        lines = diff_text.split('\n')
        added_lines = [l[1:] for l in lines if l.startswith('+') and not l.startswith('+++')]
        
        if not added_lines:
            return scores, 0
        
        # Check for generic variable names
        code_text = '\n'.join(added_lines)
        for pattern in self.generic_var_patterns:
            scores['generic_vars'] += len(re.findall(pattern, code_text, re.IGNORECASE))
        
        # Check comment density (AI loves over-commenting)
        comment_lines = sum(1 for l in added_lines if l.strip().startswith(('#', '//', '/*', '*')))
        if added_lines:
            comment_ratio = comment_lines / len(added_lines)
            scores['excessive_comments'] = int(comment_ratio > 0.4) * 10
        
        # Check for AI comment patterns
        for pattern in self.ai_comment_patterns:
            scores['excessive_comments'] += len(re.findall(pattern, code_text)) * 3
        
        # Check for hallucinated/unusual imports
        import_lines = [l for l in added_lines if 'import' in l.lower()]
        suspicious_imports = ['utils.helper', 'common.base', 'core.main', 'lib.generic']
        for imp in import_lines:
            if any(sus in imp for sus in suspicious_imports):
                scores['suspicious_imports'] += 5
        
        # Calculate total risk score
        total_score = sum(scores.values())
        return scores, total_score


def fetch_pr_diff(repo, pr_number, token=None):
    """Fetch PR diff from GitHub API"""
    if not repo or not isinstance(repo, str) or '/' not in repo:
        raise ValueError("Repository must be in format 'owner/repo'")
    
    if not isinstance(pr_number, int) or pr_number <= 0:
        raise ValueError("PR number must be a positive integer")
    
    url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}'
    headers = {'Accept': 'application/vnd.github.v3.diff'}
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except HTTPError as e:
        if e.code == 404:
            print(f"Error: PR #{pr_number} not found in repository {repo}", file=sys.stderr)
        elif e.code == 401:
            print("Error: Authentication failed. Check your GitHub token.", file=sys.stderr)
        elif e.code == 403:
            print("Error: Rate limit exceeded or access forbidden.", file=sys.stderr)
        else:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error fetching PR: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description='Detect AI-generated code patterns in GitHub PRs'
    )
    parser.add_argument('repo', help='GitHub repository (owner/repo)')
    parser.add_argument('pr_number', type=int, help='Pull request number')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--threshold', type=int, default=15,
                       help='Risk score threshold (default: 15)')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    
    args = parser.parse_args()
    
    if not args.json:
        print(f"Analyzing PR #{args.pr_number} in {args.repo}...")
    
    # Fetch the PR diff
    try:
        diff = fetch_pr_diff(args.repo, args.pr_number, args.token)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Analyze for AI patterns
    detector = AICodeDetector()
    scores, total_score = detector.analyze_diff(diff)
    
    # Determine verdict
    is_suspicious = total_score >= args.threshold
    
    # Output results
    if args.json:
        result = {
            'repo': args.repo,
            'pr_number': args.pr_number,
            'total_score': total_score,
            'threshold': args.threshold,
            'is_suspicious': is_suspicious,
            'scores': scores
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"AI Code Detection Results")
        print(f"{'='*60}")
        print(f"Repository: {args.repo}")
        print(f"PR Number: #{args.pr_number}")
        print(f"\nDetailed Scores:")
        for category, score in scores.items():
            print(f"  {category.replace('_', ' ').title()}: {score}")
        print(f"\nTotal Risk Score: {total_score}")
        print(f"Threshold: {args.threshold}")
        print(f"\nVerdict: {'⚠️  SUSPICIOUS - Possible AI-generated code' if is_suspicious else '✓ PASS - Looks human-written'}")
        print(f"{'='*60}\n")
    
    # Exit with appropriate code
    sys.exit(1 if is_suspicious else 0)


if __name__ == '__main__':
    main()