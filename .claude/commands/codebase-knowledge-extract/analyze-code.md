# Analyze Code

Run static analysis to measure code quality and security.

## What This Does

Analyzes Python code using industry-standard tools:
- **Radon**: Cyclomatic complexity, maintainability index, Halstead metrics
- **Bandit**: Security vulnerability scanning
- **Raw Metrics**: LOC, SLOC, comments, blank lines

## Run

```bash
cd tac-learning-system
python analysis/static_analyzer.py
```

## Output

Saves to: `tac-learning-system/data/tac-2/static_analysis.json`

## Expected Results

### Complexity Metrics
- **Cyclomatic Complexity**: 1-40+ (A=simple, F=very complex)
- **Maintainability Index**: 0-100 (higher is better)
- **Halstead Volume**: Code complexity measure
- **Halstead Difficulty**: How hard to understand

### Security Scanning
- Vulnerability severity: HIGH, MEDIUM, LOW
- Issue types: SQL injection, hardcoded secrets, insecure API usage
- Line numbers for each issue
- Confidence levels

### Quality Insights
- Average complexity per module
- Complex functions identified (complexity > 10)
- Files with security issues
- Maintainability rankings

## Example Output

```json
{
  "metadata": {
    "average_complexity": 21.17,
    "average_maintainability": 76.24,
    "total_security_issues": 118,
    "high_severity_issues": 0
  },
  "detailed_results": [
    {
      "file_path": "server.py",
      "complexity": [
        {
          "name": "upload_file",
          "complexity": 2,
          "rank": "A"
        }
      ],
      "maintainability": {
        "mi_score": 76.24,
        "mi_rank": "A"
      },
      "security": [
        {
          "severity": "LOW",
          "issue_text": "Possible SQL injection",
          "line_number": 42
        }
      ]
    }
  ]
}
```

## Ranking System

### Complexity Ranks
- **A**: 1-5 (Simple)
- **B**: 6-10 (Well structured)
- **C**: 11-20 (Complex)
- **D**: 21-30 (Very complex)
- **E**: 31-40 (Extremely complex)
- **F**: 41+ (Unmaintainable)

### Maintainability Ranks
- **A**: 20-100 (Very maintainable)
- **B**: 10-20 (Maintainable)
- **C**: 0-10 (Hard to maintain)

## Performance Note

Bandit security scanning can take ~45 seconds for 12 files. For large repositories, consider running this separately.
