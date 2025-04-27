# MVP for Principles of Innovation & Entrepreneurship

### Installation

1. (Optional) Create and activate virtual environment:

    python3 -m venv venv
    source venv/bin/activate

2. pip install -r requirements.txt

3. Install Cursor (our MVP uses Cursor Agent to scan the user's repo)

    https://www.cursor.com/en

### Test

1. python repo_analyzer.py <git_repository_url>

    Recommended to use a public git repo. Example command:
    
    python repo_analyzer.py https://github.com/paeb37/ui-design.git

2. Open the cloned repo in Cursor, and run Agent mode with the produced "instructions.md" file. You can just say "Follow these instructions"

    Full analysis report will be saved to the "report.md" file
    
    Optional: Use cmd+shift+v to view report in cleaner format