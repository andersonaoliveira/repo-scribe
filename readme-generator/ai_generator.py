# ai_generator.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def clean_ai_response(text):
    if text.startswith("```markdown"):
        text = text[9:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def generate_readme_content(project_analysis, repo_owner):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    Você é um especialista em documentação de software. Sua tarefa é criar um arquivo README.md profissional e bem estruturado para um projeto de software.

    Use o seguinte contexto, que foi analisado a partir do código-fonte do projeto:
    - Dono do Repositório: {repo_owner}
    - Linguagens detectadas (e contagem de arquivos): {project_analysis['languages']}
    - Arquivos de dependência e seu conteúdo: {project_analysis.get('dependencies', 'Nenhum encontrado')}

    Com base nesse contexto, gere um README.md completo em Markdown. O README deve incluir as seguintes seções:
    1.  **Título do Projeto**
    2.  **Descrição**
    3.  **Autor / Contribuidor Principal**: Mencione que o projeto foi criado por **{repo_owner}**.
    4.  **Tecnologias Utilizadas**
    5.  **Como Começar**

    NÃO envolva a resposta em um bloco de código markdown como ```markdown. Retorne apenas o conteúdo Markdown puro.
    """
    try:
        response = model.generate_content(prompt)
        cleaned_text = clean_ai_response(response.text)
        return cleaned_text
    except Exception as e:
        return f"Erro ao gerar conteúdo com a IA: {e}"