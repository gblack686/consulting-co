"""
Static code analysis using Radon, Bandit, and custom metrics.

Analyzes:
- Complexity (cyclomatic, cognitive)
- Maintainability index
- Security vulnerabilities
- Code quality metrics
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze


@dataclass
class ComplexityMetrics:
    """Cyclomatic complexity metrics for a function"""
    name: str
    complexity: int
    rank: str  # A (simple) to F (very complex)
    line_start: int
    line_end: int


@dataclass
class MaintainabilityMetrics:
    """Maintainability index for a module"""
    mi_score: float  # 0-100, higher is better
    mi_rank: str  # A (very maintainable) to C (hard to maintain)
    halstead_volume: float
    halstead_difficulty: float


@dataclass
class RawMetrics:
    """Raw code metrics"""
    loc: int  # Lines of code
    lloc: int  # Logical lines of code
    sloc: int  # Source lines of code
    comments: int
    multi: int  # Multi-line strings
    blank: int
    single_comments: int


@dataclass
class SecurityIssue:
    """Security vulnerability found by Bandit"""
    severity: str  # HIGH, MEDIUM, LOW
    confidence: str  # HIGH, MEDIUM, LOW
    issue_text: str
    line_number: int
    test_id: str


class StaticAnalyzer:
    """Run static analysis tools on Python code"""

    COMPLEXITY_RANKS = {
        (1, 5): 'A',    # Simple
        (6, 10): 'B',   # Well structured
        (11, 20): 'C',  # Complex
        (21, 30): 'D',  # Very complex
        (31, 40): 'E',  # Extremely complex
        (41, float('inf')): 'F'  # Unmaintainable
    }

    MAINTAINABILITY_RANKS = {
        (20, 100): 'A',   # Very maintainable
        (10, 20): 'B',    # Maintainable
        (0, 10): 'C'      # Hard to maintain
    }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Run all static analysis on a single file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            return {
                'file_path': str(file_path),
                'complexity': self._analyze_complexity(content),
                'maintainability': self._analyze_maintainability(content),
                'raw_metrics': self._analyze_raw_metrics(content),
                'security': self._analyze_security(file_path)
            }

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _analyze_complexity(self, content: str) -> List[Dict[str, Any]]:
        """Calculate cyclomatic complexity using Radon"""
        try:
            complexity_data = cc_visit(content)

            metrics = []
            for item in complexity_data:
                rank = self._get_complexity_rank(item.complexity)
                metrics.append({
                    'name': item.name,
                    'complexity': item.complexity,
                    'rank': rank,
                    'line_start': item.lineno,
                    'line_end': item.endline
                })

            return metrics

        except Exception as e:
            print(f"Complexity analysis error: {e}")
            return []

    def _analyze_maintainability(self, content: str) -> Optional[Dict[str, Any]]:
        """Calculate maintainability index using Radon"""
        try:
            # Maintainability index
            mi_score = mi_visit(content, multi=True)

            # Halstead metrics
            halstead = h_visit(content)

            if halstead:
                halstead_total = halstead[0]
                volume = halstead_total.volume
                difficulty = halstead_total.difficulty
            else:
                volume = 0
                difficulty = 0

            rank = self._get_maintainability_rank(mi_score)

            return {
                'mi_score': round(mi_score, 2),
                'mi_rank': rank,
                'halstead_volume': round(volume, 2),
                'halstead_difficulty': round(difficulty, 2)
            }

        except Exception as e:
            print(f"Maintainability analysis error: {e}")
            return None

    def _analyze_raw_metrics(self, content: str) -> Optional[Dict[str, Any]]:
        """Calculate raw code metrics using Radon"""
        try:
            raw = analyze(content)

            return {
                'loc': raw.loc,
                'lloc': raw.lloc,
                'sloc': raw.sloc,
                'comments': raw.comments,
                'multi': raw.multi,
                'blank': raw.blank,
                'single_comments': raw.single_comments
            }

        except Exception as e:
            print(f"Raw metrics error: {e}")
            return None

    def _analyze_security(self, file_path: Path) -> List[Dict[str, Any]]:
        """Run Bandit security scanner"""
        try:
            # Run Bandit with JSON output
            result = subprocess.run(
                ['bandit', '-f', 'json', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                data = json.loads(result.stdout)
                issues = []

                for item in data.get('results', []):
                    issues.append({
                        'severity': item['issue_severity'],
                        'confidence': item['issue_confidence'],
                        'issue_text': item['issue_text'],
                        'line_number': item['line_number'],
                        'test_id': item['test_id']
                    })

                return issues

            return []

        except subprocess.TimeoutExpired:
            print(f"Bandit timeout on {file_path}")
            return []
        except Exception as e:
            print(f"Security analysis error: {e}")
            return []

    def _get_complexity_rank(self, complexity: int) -> str:
        """Get rank letter for complexity score"""
        for (low, high), rank in self.COMPLEXITY_RANKS.items():
            if low <= complexity <= high:
                return rank
        return 'F'

    def _get_maintainability_rank(self, mi_score: float) -> str:
        """Get rank letter for maintainability score"""
        for (low, high), rank in self.MAINTAINABILITY_RANKS.items():
            if low <= mi_score <= high:
                return rank
        return 'C'


def analyze_directory(root_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Run static analysis on all Python files in a directory.

    Args:
        root_path: Root directory to analyze
        output_dir: Where to save analysis results

    Returns:
        Analysis summary and detailed results
    """
    analyzer = StaticAnalyzer()
    results = []

    # Find all Python files
    python_files = list(root_path.rglob('*.py'))
    print(f"Analyzing {len(python_files)} Python files...")

    for py_file in python_files:
        print(f"Analyzing: {py_file.relative_to(root_path)}")
        analysis = analyzer.analyze_file(py_file)
        if analysis:
            results.append(analysis)

    # Calculate summary statistics
    total_complexity = 0
    total_mi_score = 0
    total_security_issues = 0
    high_severity_issues = 0
    complex_functions = []  # Complexity > 10

    for result in results:
        # Complexity stats
        for func in result.get('complexity', []):
            total_complexity += func['complexity']
            if func['complexity'] > 10:
                complex_functions.append({
                    'file': result['file_path'],
                    'function': func['name'],
                    'complexity': func['complexity'],
                    'rank': func['rank']
                })

        # Maintainability stats
        if result.get('maintainability'):
            total_mi_score += result['maintainability']['mi_score']

        # Security stats
        for issue in result.get('security', []):
            total_security_issues += 1
            if issue['severity'] == 'HIGH':
                high_severity_issues += 1

    # Create catalog
    catalog = {
        "metadata": {
            "root_path": str(root_path),
            "total_files": len(results),
            "average_complexity": round(total_complexity / max(len(results), 1), 2),
            "average_maintainability": round(total_mi_score / max(len(results), 1), 2),
            "total_security_issues": total_security_issues,
            "high_severity_issues": high_severity_issues
        },
        "summary": {
            "complex_functions": complex_functions,
            "files_with_security_issues": [
                {
                    'file': r['file_path'],
                    'issues': len(r['security'])
                }
                for r in results if r.get('security')
            ]
        },
        "detailed_results": results
    }

    # Save to file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "static_analysis.json"
    output_file.write_text(json.dumps(catalog, indent=2))

    print(f"\n✅ Analysis complete!")
    print(f"✅ Average complexity: {catalog['metadata']['average_complexity']}")
    print(f"✅ Average maintainability: {catalog['metadata']['average_maintainability']}/100")
    print(f"✅ Security issues: {total_security_issues} ({high_severity_issues} high severity)")
    print(f"✅ Complex functions (>10): {len(complex_functions)}")
    print(f"✅ Saved to: {output_file}")

    return catalog


if __name__ == "__main__":
    # Analyze tac-2
    root = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\tac-2")
    output = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data\tac-2")

    catalog = analyze_directory(root, output)

    # Print detailed summary
    print("\n" + "="*60)
    print("STATIC ANALYSIS SUMMARY")
    print("="*60)

    if catalog['summary']['complex_functions']:
        print("\n⚠️  Complex Functions (Complexity > 10):")
        for func in catalog['summary']['complex_functions'][:10]:  # Show top 10
            print(f"  {func['function']} - Complexity: {func['complexity']} ({func['rank']})")
            print(f"    File: {Path(func['file']).name}")

    if catalog['summary']['files_with_security_issues']:
        print("\n🔒 Security Issues by File:")
        for file_info in catalog['summary']['files_with_security_issues']:
            print(f"  {Path(file_info['file']).name}: {file_info['issues']} issues")
