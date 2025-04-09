from django.shortcuts import render
import os
import markdown
from pathlib import Path
import logging
import re

# 获取logger
logger = logging.getLogger('docs')

# 清理无效Unicode字符的函数
def clean_unicode_surrogates(text):
    """清理文本中的Unicode代理对和其他无效字符"""
    # 清理代理对字符 (Unicode surrogate pairs)
    text = text.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
    # 替换任何其他无效Unicode字符为问号
    return re.sub(r'[\uD800-\uDFFF]', '?', text)

# Create your views here.

def document_list(request):
    """显示doc目录下的所有文档列表"""
    logger.info(f"文档列表页面被请求，请求方法: {request.method}, 用户IP: {request.META.get('REMOTE_ADDR')}")
    
    try:
        # 获取项目根目录
        base_dir = Path(__file__).resolve().parent.parent
        doc_dir = os.path.join(base_dir, 'doc')
        logger.debug(f"文档目录路径: {doc_dir}")
        
        # 检查文档目录是否存在
        if not os.path.exists(doc_dir):
            logger.error(f"文档目录不存在: {doc_dir}")
            documents = []
            context = {'documents': documents, 'error': '文档目录未找到'}
            return render(request, 'docs/document_list.html', context)
        
        # 获取doc目录下的所有文档
        documents = []
        logger.info(f"开始扫描目录中的Markdown文件: {doc_dir}")
        files_list = os.listdir(doc_dir)
        logger.debug(f"目录中的文件列表: {files_list}")
        
        for filename in files_list:
            if filename.endswith('.md'):
                file_path = os.path.join(doc_dir, filename)
                logger.debug(f"处理Markdown文件: {file_path}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='surrogateescape') as f:
                        content = f.read()
                        logger.debug(f"成功读取文件: {filename}, 大小: {len(content)} 字节")
                        
                        # 清理内容中的无效Unicode字符
                        content = clean_unicode_surrogates(content)
                        
                        # 转换Markdown为HTML，添加更多扩展支持
                        extensions = [
                            'tables',
                            'fenced_code',
                            'codehilite',
                            'nl2br',
                            'extra'
                        ]
                        html_content = markdown.markdown(content, extensions=extensions)
                        logger.debug(f"Markdown 转换为 HTML 成功: {filename}")
                    
                    # 确保HTML内容不包含代理对
                    html_content = clean_unicode_surrogates(html_content)
                    
                    documents.append({
                        'filename': filename,
                        'content': html_content
                    })
                except Exception as e:
                    logger.error(f"处理文件 {filename} 时出错: {str(e)}")
        
        logger.info(f"文档处理完成，共加载 {len(documents)} 个文档")
        context = {'documents': documents}
        return render(request, 'docs/document_list.html', context)
        
    except Exception as e:
        logger.error(f"document_list 视图函数错误: {str(e)}", exc_info=True)
        context = {'documents': [], 'error': f'加载文档时发生错误: {str(e)}'}
        return render(request, 'docs/document_list.html', context)
