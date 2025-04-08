from django.shortcuts import render
import os
import markdown
from pathlib import Path

# Create your views here.

def document_list(request):
    """显示doc目录下的所有文档列表"""
    # 获取项目根目录
    base_dir = Path(__file__).resolve().parent.parent
    doc_dir = os.path.join(base_dir, 'doc')
    
    # 获取doc目录下的所有文档
    documents = []
    if os.path.exists(doc_dir):
        for filename in os.listdir(doc_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(doc_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 转换Markdown为HTML，添加更多扩展支持
                    extensions = [
                        'tables',
                        'fenced_code',
                        'codehilite',
                        'nl2br',
                        'extra'
                    ]
                    html_content = markdown.markdown(content, extensions=extensions)
                    
                documents.append({
                    'filename': filename,
                    'content': html_content
                })
    
    context = {'documents': documents}
    return render(request, 'docs/document_list.html', context)
