# AI Code Contribution Filter

> Protect your open source project from low-quality AI-generated pull requests

## The Problem

Open source maintainers are drowning in AI-generated "slop" code contributions. These PRs waste precious review time with generic variable names, excessive comments, hallucinated imports, and code that looks right but doesn't work.

As seen with Godot Engine and other major projects, the flood of AI-generated PRs is becoming unsustainable.

## What This Does

This tool analyzes pull request diffs and detects common patterns found in AI-generated code:

- **Generic variable names** (temp1, data2, result, obj)
- **Excessive commenting** (>40% comment ratio, AI-style boilerplate)
- **Suspicious imports** (hallucinated modules, generic helpers)
- **Boilerplate patterns** ("TODO: implement logic here")

Get a risk score for each PR to prioritize your review time.

## Installation

```bash
# Clone the repository
git clone https://github.com/LuluFoxy-AI/ai-code-contribution-filter-for-open-source-mainta.git
cd ai-code-contribution-filter-for-open-source-mainta

# No dependencies needed - uses Python stdlib only!
python ai_code_filter.py --help
```

## Usage

```bash
# Analyze a pull request
python ai_code_filter.py owner/repo 123

# With GitHub token (for private repos or higher rate limits)
python ai_code_filter.py owner/repo 123 --token YOUR_GITHUB_TOKEN

# Custom threshold
python ai_code_filter.py owner/repo 123 --threshold 20
```

## Free vs Pro

**Free (This Script)**
- Command-line tool
- Analyze individual PRs
- Core detection algorithms
- Unlimited local use

**Pro ($29/month)**
- GitHub Action integration
- Auto-label suspicious PRs
- Unlimited repositories
- Custom detection rules
- Slack/Discord notifications
- Priority support

**Enterprise ($199/month)**
- Multi-organization support
- Advanced ML models
- Custom training on your codebase
- Dedicated support
- SLA guarantees

## License

MIT License - Free for personal and commercial use