# code_analyzer.py
import os

def analyze_project_structure(path):
    """Analisa a estrutura de um projeto em um dado caminho."""
    analysis = {
        "languages": {},
        "files": [],
        "dependencies": {}
    }

    dependency_files = {
        'requirements.txt': 'pip',
        'package.json': 'npm',
        'pom.xml': 'maven',
        'build.gradle': 'gradle'
    }

    for root, _, files in os.walk(path):
        for file in files:
            analysis["files"].append(file)
            
            ext = file.split('.')[-1]
            if ext in ['py', 'js', 'html', 'css', 'java', 'go', 'rb']:
                analysis["languages"][ext] = analysis["languages"].get(ext, 0) + 1

            if file in dependency_files:
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        analysis["dependencies"][file] = f.read()
                except Exception as e:
                    analysis["dependencies"][file] = f"Error reading file: {e}"

    return analysis
