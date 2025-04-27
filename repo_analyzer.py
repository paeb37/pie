#!/usr/bin/env python3

import os
import sys
import json
import git
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class RepoAnalyzer:
    def __init__(self, output_dir: str = "analysis_output"):
        """Initialize the repository analyzer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_repository(self, repo_url: str) -> Tuple[bool, str]:
        """
        Analyze a GitHub repository and generate prompts for Cursor.
        Returns (success, message) tuple.
        """
        try:
            # Generate repository directory name
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            repo_dir = self.output_dir / repo_name
            repo_dir.mkdir(exist_ok=True)
            
            # Step 1: Clone and validate repository
            repo_path = self._clone_repository(repo_url, repo_dir)
            if not repo_path:
                return False, "Failed to clone repository"
            
            # Step 2: Analyze the repository
            analysis_results = self._analyze_codebase(repo_path)
            
            # Step 3: Generate combined prompt
            prompt = self._generate_combined_prompt(analysis_results, repo_path)
            
            # Step 4: Save results
            instructions_path = repo_dir / "instructions.md"
            
            with open(instructions_path, "w") as f:
                f.write(prompt)
            
            # Step 5: Create an empty report.md file
            report_path = repo_dir / "report.md"
            with open(report_path, "w") as f:
                f.write("# Repository Analysis Report\n\n")
                f.write("## Overview\n")
                f.write("This report contains the analysis of the repository based on the instructions provided.\n\n")
                f.write("## Repository Information\n")
                f.write(f"- Repository: {repo_name}\n")
                f.write(f"- Analysis Date: {datetime.now().strftime('%B %d, %Y')}\n\n")
                f.write("## Analysis Results\n")
                f.write("[Your analysis results will be added here]\n\n")
                f.write("## Recommendations\n")
                f.write("[Your recommendations will be added here]\n\n")
                f.write("## Next Steps\n")
                f.write("[Your next steps will be added here]\n")
            
            return True, f"""Analysis complete. Repository and analysis files are in: {repo_dir}
- Repository files: {repo_path}
- Instructions file: {instructions_path}
- Report file: {report_path}
You can now open the repository in Cursor and use the generated prompt."""
            
        except Exception as e:
            return False, f"Error during analysis: {str(e)}"
    
    def _clone_repository(self, repo_url: str, repo_dir: Path) -> Optional[Path]:
        """Clone the repository and return the path to the cloned repo."""
        try:
            repo_path = repo_dir / "repo"
            
            # If repository exists, update it instead of removing
            if repo_path.exists():
                try:
                    repo = git.Repo(repo_path)
                    repo.remotes.origin.pull()
                    return repo_path
                except git.exc.GitCommandError:
                    # If pull fails, remove and clone fresh
                    shutil.rmtree(repo_path)
            
            # Clone the repository
            git.Repo.clone_from(repo_url, repo_path)
            return repo_path
            
        except git.exc.GitCommandError as e:
            print(f"Git error: {e}")
            return None
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return None
    
    def _analyze_codebase(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze the codebase and return analysis results."""
        analysis = {
            "repository_info": self._get_repository_info(repo_path),
            "file_structure": self._analyze_file_structure(repo_path),
            "technologies": self._identify_technologies(repo_path),
            "code_metrics": self._analyze_code_metrics(repo_path)
        }
        return analysis
    
    def _get_repository_info(self, repo_path: Path) -> Dict[str, Any]:
        """Get basic repository information."""
        repo = git.Repo(repo_path)
        return {
            "name": repo_path.name,
            "description": repo.description or "No description available",
            "last_commit": str(repo.head.commit.committed_datetime),
            "branch": repo.active_branch.name,
            "total_commits": len(list(repo.iter_commits())),
            "contributors": len(set(commit.author.name for commit in repo.iter_commits()))
        }
    
    def _analyze_file_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze the file structure of the repository."""
        structure = {
            "directories": {},
            "files": {},
            "file_types": {},
            "total_files": 0
        }
        
        for root, dirs, files in os.walk(repo_path):
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == ".":
                continue
                
            # Skip .git directory
            if ".git" in rel_path:
                continue
                
            structure["directories"][rel_path] = {
                "file_count": len(files),
                "subdirectories": len(dirs)
            }
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                structure["total_files"] += 1
                
                file_path = os.path.join(rel_path, file)
                structure["files"][file_path] = {
                    "size": os.path.getsize(os.path.join(root, file)),
                    "extension": ext
                }
        
        return structure
    
    def _identify_technologies(self, repo_path: Path) -> Dict[str, Any]:
        """Identify technologies and dependencies used in the project."""
        tech_stack = {
            "languages": {},
            "frameworks": {},
            "dependencies": {}
        }
        
        # Check for common configuration files
        config_files = {
            "package.json": "Node.js",
            "requirements.txt": "Python",
            "pom.xml": "Java/Maven",
            "build.gradle": "Java/Gradle",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "Gemfile": "Ruby",
            "composer.json": "PHP",
            "Dockerfile": "Docker",
            "docker-compose.yml": "Docker"
        }
        
        for file, tech in config_files.items():
            if (repo_path / file).exists():
                tech_stack["languages"][tech] = "detected"
        
        return tech_stack
    
    def _analyze_code_metrics(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze code metrics and quality indicators."""
        metrics = {
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "file_sizes": {
                "small": 0,  # < 100 lines
                "medium": 0,  # 100-500 lines
                "large": 0   # > 500 lines
            }
        }
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.cpp', '.cs', '.rb', '.php', '.go')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            metrics["total_lines"] += len(lines)
                            metrics["code_lines"] += len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*', '*', '*/'))])
                            metrics["comment_lines"] += len([l for l in lines if l.strip().startswith(('#', '//', '/*', '*', '*/'))])
                            metrics["blank_lines"] += len([l for l in lines if not l.strip()])
                            
                            # Categorize file size
                            if len(lines) < 100:
                                metrics["file_sizes"]["small"] += 1
                            elif len(lines) < 500:
                                metrics["file_sizes"]["medium"] += 1
                            else:
                                metrics["file_sizes"]["large"] += 1
                    except Exception:
                        continue
        
        return metrics
    
    def _generate_combined_prompt(self, analysis: Dict[str, Any], repo_path: Path) -> str:
        """Generate a single, comprehensive prompt for Cursor."""
        repo_info = analysis['repository_info']
        file_structure = analysis['file_structure']
        tech_stack = analysis['technologies']
        code_metrics = analysis['code_metrics']
        
        prompt = f"""# Repository Analysis and Recommendations

## 1. Overview (Current Architecture and Design)

### Repository Information
- Name: {repo_info['name']}
- Description: {repo_info['description']}
- Last Updated: {repo_info['last_commit']}
- Branch: {repo_info['branch']}
- Total Commits: {repo_info['total_commits']}
- Contributors: {repo_info['contributors']}
- Repository Path: {repo_path}

### Codebase Structure
- Total Files: {file_structure['total_files']}
- File Types: {', '.join(f"{k}: {v}" for k, v in file_structure['file_types'].items())}

### Directory Structure
{self._format_directory_structure(file_structure['directories'])}

## 2. Tech Stack and Code Quality

### Technology Stack
- Languages Detected: {', '.join(tech_stack['languages'].keys())}
- Frameworks: {', '.join(tech_stack['frameworks'].keys())}
- Dependencies: {', '.join(tech_stack['dependencies'].keys())}

### Code Metrics
- Total Lines: {code_metrics['total_lines']}
- Code Lines: {code_metrics['code_lines']}
- Comment Lines: {code_metrics['comment_lines']}
- Blank Lines: {code_metrics['blank_lines']}
- File Size Distribution:
  - Small Files (<100 lines): {code_metrics['file_sizes']['small']}
  - Medium Files (100-500 lines): {code_metrics['file_sizes']['medium']}
  - Large Files (>500 lines): {code_metrics['file_sizes']['large']}

## 3. Recommendations

Please analyze this repository and provide specific, actionable recommendations in the following areas:

### A. Architecture and Design Improvements
- Evaluate current architecture and design patterns
- Identify potential architectural improvements
- Suggest design pattern implementations
- Recommend structural changes

### B. Code Quality and Security
- Identify code quality issues and suggest improvements
- Review error handling and logging practices
- Identify security vulnerabilities
- Suggest security improvements
- Review authentication and authorization

### C. Technology and Performance
- Evaluate technology choices and suggest modern alternatives
- Identify performance bottlenecks
- Suggest optimization opportunities
- Recommend dependency updates
- Evaluate scalability considerations

### D. Testing and Documentation
- Evaluate test coverage and quality
- Suggest testing improvements and tools
- Review existing documentation
- Identify documentation gaps
- Recommend documentation tools and practices

### E. Development Workflow
- Evaluate CI/CD practices
- Suggest workflow improvements
- Recommend development tools
- Identify automation opportunities

### F. Project Ideas and Extensions
- Suggest complementary projects to build
- Recommend features to add
- Identify integration opportunities
- Suggest experimental improvements

Please provide specific, actionable recommendations for each area, with examples where appropriate. Focus on practical improvements that can be implemented incrementally. When referencing specific files or code, please use the actual file paths from the cloned repository.

## 4. Output Instructions

After completing your analysis, please save your findings to the report.md file in the same directory as this instructions.md file. The report.md file has already been created with a basic structure. Please update the "Analysis Results" section with your detailed analysis and the "Recommendations" and "Next Steps" sections with your specific recommendations.
"""
        return prompt
    
    def _format_directory_structure(self, directories: Dict[str, Any]) -> str:
        """Format the directory structure for markdown output."""
        result = ""
        for dir_name, info in sorted(directories.items()):
            result += f"- **{dir_name}**\n"
            result += f"  - Files: {info['file_count']}\n"
            result += f"  - Subdirectories: {info['subdirectories']}\n"
        return result
    
    def cleanup_repository(self, repo_name: str) -> bool:
        """Manually clean up a repository and its analysis files."""
        try:
            repo_dir = self.output_dir / repo_name
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
                return True
            return False
        except Exception as e:
            print(f"Error cleaning up repository: {e}")
            return False
    
    def cleanup_all_repositories(self) -> bool:
        """Clean up all repositories and their analysis files."""
        try:
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                self.output_dir.mkdir(exist_ok=True)
            return True
        except Exception as e:
            print(f"Error cleaning up repositories: {e}")
            return False

    def save_cursor_output(self, repo_name: str, output_content: str) -> Tuple[bool, str]:
        """
        Save the Cursor agent's output to a markdown file.
        Returns (success, message) tuple.
        """
        try:
            repo_dir = self.output_dir / repo_name
            if not repo_dir.exists():
                return False, f"Repository directory not found: {repo_dir}"
            
            output_path = repo_dir / "output.md"
            with open(output_path, "w") as f:
                f.write(output_content)
            
            return True, f"Cursor output saved to: {output_path}"
            
        except Exception as e:
            return False, f"Error saving Cursor output: {str(e)}"

def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python repo_analyzer.py <repository_url>")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    analyzer = RepoAnalyzer()
    success, message = analyzer.analyze_repository(repo_url)
    
    if success:
        print(message)
    else:
        print(f"Error: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main() 