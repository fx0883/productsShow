"""
WSGI config for product_show project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import logging

# 设置基本日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
    filename='wsgi_debug.log',
    filemode='a'
)

# 记录WSGI启动信息
logging.info("WSGI 脚本正在初始化")

try:
    # 添加项目路径到 Python 路径
    # 获取当前文件的目录
    current_path = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录 (current_path的父目录)
    project_path = os.path.dirname(current_path)
    
    logging.info(f"项目路径: {project_path}")
    
    # 将项目根目录添加到Python路径
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
        logging.info(f"已添加路径到sys.path: {project_path}")
    
    # 设置Django设置模块
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_show.settings')
    logging.info("环境变量DJANGO_SETTINGS_MODULE已设置为'product_show.settings'")
    
    # 导入Django的WSGI应用
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logging.info("Django应用已成功初始化")
    
except Exception as e:
    # 记录任何异常
    logging.error(f"初始化WSGI应用时出错: {str(e)}")
    import traceback
    logging.error(f"详细错误信息: {traceback.format_exc()}")
    # 重新抛出异常以便web服务器可以记录它
    raise
