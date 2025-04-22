from dotenv import load_dotenv
import os

def load_env():
    """加载环境变量"""
    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # 加载.env文件
        env_path = os.path.join(project_root, '.env')
        
        if not os.path.exists(env_path):
            print(f"警告: 环境变量文件不存在: {env_path}")
            print("请复制.env.example为.env并配置相应的环境变量")
            return False
            
        load_dotenv(env_path)
        return True
    except Exception as e:
        print(f"加载环境变量失败: {str(e)}")
        return False

def get_env(key: str, default: str = None) -> str:
    """获取环境变量值"""
    value = os.getenv(key, default)
    if value is None:
        print(f"警告: 环境变量 {key} 未设置")
    return value