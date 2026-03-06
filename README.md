# AI Code Contribution Filter

> Protect your open source project from low-quality AI-generated pull requests

## The Problem

Open source maintainers are drowning in AI-generated code contributions. These PRs often feature:
- Generic variable names (temp1, data2, result3)
- Excessive commenting that adds no value
- Inconsistent code style
- Boilerplate patterns that don't match project conventions

Reviewing these takes time away from genuine contributions and can pollute your codebase.

## What This Tool Does

AI Code Contribution Filter analyzes pull request diffs and provides:
- **AI Likelihood Score** (0-100): How likely the code is AI-generated
- **Confidence Level**: How certain the analysis is
- **Detailed Metrics**: Generic variables, comment ratio, AI phrases, style consistency
- **Clear Recommendation**: APPROVE or REVIEW

## Installation

```bash
# Clone the repository
git clone https://github.com/LuluFoxy-AI/ai-code-contribution-filter-for-open-source-mainta.git
cd ai-code-contribution-filter-for-open-source-mainta

# No dependencies needed - uses Python stdlib only!
python ai_code_filter.py --help
```

## Usage

### Analyze a PR diff file

```bash
# Generate a diff from your PR
git diff main feature-branch > pr_diff.txt

# Run the analyzer
python ai_code_filter.py --diff-file pr_diff.txt

# Get JSON output
python ai_code_filter.py --diff-file pr_diff.txt --output json
```

### Example Output

```
AI Code Detection Results
==================================================
AI Likelihood Score: 67.5/100
Confidence: 75%
Assessment: High likelihood of AI generation - careful review needed
Recommendation: REVIEW

Details:
  generic_variable_score: 45.0
  comment_ratio: 72.5
  ai_phrase_score: 83.3
  style_consistency: 65.0
  lines_analyzed: 156
```

## Free vs Pro

**Free Version** (This Script):
- Command-line tool
- Analyze unlimited diffs locally
- All core detection features
- Perfect for individual maintainers

**Pro Version** ($29/month):
- GitHub Action integration
- Automatic PR analysis
- Custom detection rules
- Webhook notifications
- Priority support

**Enterprise** ($199/month):
- Multi-repository support
- Team management
- Advanced analytics dashboard
- Custom model training
- SLA support

## How It Works

The tool analyzes four key dimensions:

1. **Generic Variables**: Detects temp1, data2, result3 patterns
2. **Comment Ratio**: Flags excessive commenting (AI loves to over-explain)
3. **AI Phrases**: Identifies common AI-generated text patterns
4. **Style Consistency**: Checks for mixed indentation and formatting

## Contributing

Contributions welcome! Please ensure your PRs are human-written 😉

## License

MIT License - Free for personal and commercial use

## Support

Found a bug? Have a feature request? Open an issue on GitHub.

For Pro/Enterprise support: support@aicodefiler.dev