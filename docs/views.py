from django.shortcuts import render
import os
import markdown
from pathlib import Path
import logging
import re
import json
from django.http import HttpResponse

# 获取logger
logger = logging.getLogger('docs')

# 强力清理无效Unicode字符的函数
def clean_unicode_surrogates(text):
    """清理文本中的Unicode代理对和其他无效字符"""
    if text is None:
        return ""
        
    # 方法1: 使用正则表达式替换
    cleaned = re.sub(r'[\uD800-\uDFFF]', '?', text)
    
    # 方法2: 使用encode/decode循环处理
    try:
        cleaned = cleaned.encode('utf-8', 'ignore').decode('utf-8')
    except UnicodeError:
        # 如果仍然失败，采用更激进的措施
        cleaned = ''.join(c for c in cleaned if ord(c) < 0xD800 or ord(c) > 0xDFFF)
    
    return cleaned

# 安全渲染函数
def safe_render(request, template_name, context):
    """安全的渲染函数，确保所有字符串都不含代理对"""
    # 深度清理context中的所有字符串
    safe_context = {}
    
    for key, value in context.items():
        if isinstance(value, str):
            safe_context[key] = clean_unicode_surrogates(value)
        elif isinstance(value, list):
            safe_list = []
            for item in value:
                if isinstance(item, dict):
                    safe_dict = {}
                    for k, v in item.items():
                        if isinstance(v, str):
                            safe_dict[k] = clean_unicode_surrogates(v)
                        else:
                            safe_dict[k] = v
                    safe_list.append(safe_dict)
                else:
                    safe_list.append(item)
            safe_context[key] = safe_list
        else:
            safe_context[key] = value
    
    try:
        # 尝试普通渲染
        return render(request, template_name, safe_context)
    except UnicodeError as e:
        # 如果仍然失败，记录错误并返回纯文本响应
        logger.error(f"渲染模板失败: {str(e)}", exc_info=True)
        error_response = HttpResponse(
            f"<html><body><h1>渲染错误</h1><p>渲染模板时发生错误。请检查文档中是否包含无效字符。</p><p>错误信息: {str(e)}</p></body></html>",
            content_type='text/html'
        )
        return error_response

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
            return safe_render(request, 'docs/document_list.html', context)
        
        # 获取doc目录下的所有文档
        documents = []
        logger.info(f"开始扫描目录中的Markdown文件: {doc_dir}")
        files_list = os.listdir(doc_dir)
        logger.debug(f"目录中的文件列表: {files_list}")
        
        # 过滤只包含英文文件名的文件，避免中文编码问题
        md_files = [f for f in files_list if f.endswith('.md') and not any(ord(c) > 127 for c in f)]
        logger.info(f"找到 {len(md_files)} 个有效的Markdown文件")
        
        for index, filename in enumerate(md_files, 1):
            file_path = os.path.join(doc_dir, filename)
            logger.debug(f"处理Markdown文件 #{index}: {file_path}")
            
            try:
                # 尝试使用二进制模式读取文件，然后手动解码
                with open(file_path, 'rb') as f:
                    binary_content = f.read()
                    
                # 尝试删除任何非法UTF-8序列
                try:
                    content = binary_content.decode('utf-8', 'ignore')
                    logger.debug(f"成功读取文件: {filename}, 大小: {len(content)} 字节")
                except UnicodeError:
                    logger.warning(f"文件解码问题: {filename}, 使用fallback解码")
                    content = binary_content.decode('latin1')
                
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
                
                # 确保文件名也被清理
                clean_filename = clean_unicode_surrogates(filename)
                
                documents.append({
                    'id': index,  # 添加明确的ID
                    'filename': clean_filename,
                    'content': html_content
                })
                logger.debug(f"添加文档到列表: ID={index}, 文件名={clean_filename}")
            except Exception as e:
                logger.error(f"处理文件 {filename} 时出错: {str(e)}", exc_info=True)
        
        logger.info(f"文档处理完成，共加载 {len(documents)} 个文档")
        context = {'documents': documents, 'debug_info': {'doc_dir': doc_dir, 'file_count': len(md_files)}}
        return safe_render(request, 'docs/document_list.html', context)
        
    except Exception as e:
        logger.error(f"document_list 视图函数错误: {str(e)}", exc_info=True)
        context = {'documents': [], 'error': f'加载文档时发生错误: {str(e)}'}
        return safe_render(request, 'docs/document_list.html', context)
