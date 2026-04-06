"""
Vercel 無伺服器函數入口點
與 main.py 中的 FastAPI app 整合
"""
from main import app

def handler(request):
    """Vercel 無伺服器函數處理器"""
    return app(request)
