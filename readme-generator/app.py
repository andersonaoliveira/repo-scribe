import os
import zipfile
import tempfile
import requests
from urllib.parse import urlparse
from flask import Flask, request, render_template, redirect, url_for, flash
from code_analyzer import analyze_project_structure
from ai_generator import generate_readme_content

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-dificil'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

def get_repo_parts(github_url):
    try:
        path = urlparse(github_url).path
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] and parts[1]:
            return parts[0], parts[1]
        return None, None
    except Exception:
        return None, None

@app.route('/generate', methods=['POST'])
def generate_readme():
    github_url = request.form.get('github_url')
    if not github_url:
        flash('Por favor, insira uma URL do GitHub.')
        return redirect(url_for('index'))

    owner, repo_name = get_repo_parts(github_url)
    if not owner or not repo_name:
        flash('URL do GitHub inválida. O formato deve ser https://github.com/dono/repositorio')
        return redirect(url_for('index'))

    for branch in ['main', 'master']:
        zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip"
        response = requests.get(zip_url, stream=True)
        if response.status_code == 200:
            break
    else:
        flash(f"Não foi possível encontrar o repositório ou as branches 'main'/'master' para '{owner}/{repo_name}'.")
        return redirect(url_for('index'))

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'repo.zip')
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            extract_path = os.path.join(temp_dir, 'source')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.infolist():
                    member_path = os.path.join(extract_path, *member.filename.split('/')[1:])
                    if not member_path: continue
                    
                    if member.is_dir():
                        os.makedirs(member_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(member_path), exist_ok=True)
                        with open(member_path, 'wb') as outfile, zip_ref.open(member.filename) as infile:
                            outfile.write(infile.read())
            analysis_result = analyze_project_structure(extract_path)
            readme_content = generate_readme_content(analysis_result, owner)
            return render_template('index.html', readme_content=readme_content)

    except Exception as e:
        flash(f"Ocorreu um erro ao processar o repositório: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)