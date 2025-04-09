"""
部署调试工具 - 在cPanel环境中使用

此文件提供了额外的调试功能，帮助排查在cPanel环境中的部署问题。
在遇到500 Internal Server Error时，可以在cPanel主机上执行此脚本以获取更详细的错误信息。
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# 创建日志目录
def setup_debug_logging():
    """设置详细的日志记录"""
    try:
        # 获取项目根目录
        base_dir = Path(__file__).resolve().parent.parent
        logs_dir = os.path.join(base_dir, 'logs')
        
        # 确保日志目录存在
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # 设置详细的日志文件
        debug_log = os.path.join(logs_dir, 'cpanel_debug.log')
        
        # 配置日志
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            filename=debug_log,
            filemode='a',
            encoding='utf-8'  # 添加UTF-8编码支持
        )
        
        # 记录系统信息
        logger = logging.getLogger('debug_setup')
        logger.info('='*50)
        logger.info('部署调试工具启动')
        logger.info(f'Python 版本: {sys.version}')
        logger.info(f'Python 路径: {sys.executable}')
        logger.info(f'工作目录: {os.getcwd()}')
        logger.info(f'项目目录: {base_dir}')
        
        # 检查关键目录是否存在
        doc_dir = os.path.join(base_dir, 'doc')
        docs_dir = os.path.join(base_dir, 'docs')
        templates_dir = os.path.join(docs_dir, 'templates')
        
        logger.info(f'文档目录存在: {os.path.exists(doc_dir)}')
        logger.info(f'docs应用目录存在: {os.path.exists(docs_dir)}')
        logger.info(f'templates目录存在: {os.path.exists(templates_dir)}')
        
        # 尝试导入关键模块
        try:
            import django
            logger.info(f'Django 版本: {django.__version__}')
            
            # 尝试设置Django环境
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_show.settings')
            
            try:
                from django.conf import settings
                logger.info(f'成功导入Django设置')
                logger.info(f'DEBUG模式: {settings.DEBUG}')
                logger.info(f'允许的主机: {settings.ALLOWED_HOSTS}')
            except Exception as e:
                logger.error(f'导入Django设置失败: {e}')
        
            try:
                from django.urls import path, include
                logger.info('成功导入Django URL模块')
            except Exception as e:
                logger.error(f'导入Django URL模块失败: {e}')
                
            try:
                from docs.views import document_list
                logger.info('成功导入文档视图函数')
            except Exception as e:
                logger.error(f'导入文档视图函数失败: {e}')
                
        except ImportError as e:
            logger.error(f'导入Django失败: {e}')
            
        # 检查wsgi.py文件
        wsgi_path = os.path.join(base_dir, 'product_show', 'wsgi.py')
        if os.path.exists(wsgi_path):
            logger.info(f'wsgi.py文件存在: {wsgi_path}')
            with open(wsgi_path, 'r', encoding='utf-8') as f:  # 添加编码
                logger.info(f'wsgi.py文件内容:\n{f.read()}')
        else:
            logger.error(f'wsgi.py文件不存在: {wsgi_path}')
            
        # 检查wsgi_debug.log文件
        wsgi_log = os.path.join(base_dir, 'wsgi_debug.log')
        if os.path.exists(wsgi_log):
            logger.info(f'wsgi_debug.log文件存在，内容:')
            with open(wsgi_log, 'r', encoding='utf-8') as f:  # 添加编码
                logger.info(f.read())
        else:
            logger.info(f'wsgi_debug.log文件不存在')
            
        return debug_log
            
    except Exception as e:
        print(f"设置调试日志时出错: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_log = setup_debug_logging()
    if debug_log:
        print(f"调试日志已创建: {debug_log}")
        print("请查看此日志文件以获取更多关于部署错误的信息。")
    else:
        print("创建调试日志失败，请检查权限和路径设置。")
