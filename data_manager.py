import json
import os

class DataManager:
    """
    数据管家类：负责读取和管理本地的 JSON 数据文件。
    将文件读取逻辑与主业务逻辑隔离，便于统一管理和排错。
    """
    
    def __init__(self, data_dir="data"):
        """
        初始化方法，设定数据文件夹路径和核心文件的具体路径。
        使用 os.path.join 保证在 Windows 和 Mac/Linux 下路径拼接都不会出错。
        """
        self.data_dir = data_dir
        self.schedule_path = os.path.join(self.data_dir, "schedule.json")
        self.habits_path = os.path.join(self.data_dir, "habits.json")

    def _load_json(self, file_path):
        """
        私有方法（以单下划线开头）：通用的读取 JSON 文件的方法。
        集中处理文件不存在或格式错误等异常情况（初学者必备好习惯）。
        """
        try:
            # 必须指定 encoding='utf-8'，否则读取中文会乱码
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"❌ 错误：找不到文件 '{file_path}'。请检查 'data' 文件夹及文件是否存在！")
            return None
        except json.JSONDecodeError:
            print(f"❌ 错误：文件 '{file_path}' 格式不正确。请检查 JSON 语法（如漏了逗号或双引号）。")
            return None
        except Exception as e:
            print(f"❌ 发生未知错误读取 '{file_path}': {e}")
            return None

    def get_schedule(self):
        """获取课表数据"""
        return self._load_json(self.schedule_path)

    def get_habits(self):
        """获取个人习惯数据"""
        return self._load_json(self.habits_path)

    def get_all_context(self):
        """
        一键获取所有上下文数据。
        后续在 llm_agent.py 中，可以直接调用这个方法，把所有数据打包塞给大模型。
        """
        schedule = self.get_schedule()
        habits = self.get_habits()
        
        # 如果任一文件读取失败，返回 None，防止后续逻辑报错
        if schedule is None or habits is None:
            return None
            
        return {
            "schedule": schedule,
            "habits": habits
        }


# ==========================================
# 本地测试模块（仅在直接运行此文件时执行）
# ==========================================
if __name__ == "__main__":
    print("🚀 开始测试 DataManager...\n")
    
    # 实例化数据管家
    manager = DataManager()
    
    print("--- 1. 测试读取课表数据 (schedule.json) ---")
    schedule_data = manager.get_schedule()
    if schedule_data:
        print("✅ 读取成功！")
        print(f"   学生: {schedule_data.get('student_id')}")
        print(f"   课程总数: {len(schedule_data.get('classes', []))} 门")
        print(f"   第一门课: {schedule_data['classes'][0]['course_name']}\n")
        
    print("--- 2. 测试读取习惯数据 (habits.json) ---")
    habits_data = manager.get_habits()
    if habits_data:
        print("✅ 读取成功！")
        print(f"   起床时间: {habits_data.get('basic_routine', {}).get('wake_up_time')}")
        print(f"   高优先级任务数: {len(habits_data.get('high_priorities', []))} 项")
        print(f"   饮食偏好: {habits_data.get('dietary_habits', {}).get('preference')}\n")

    print("--- 3. 测试合并上下文 (get_all_context) ---")
    all_context = manager.get_all_context()
    if all_context:
        print("✅ 合并成功！可以随时将数据喂给大模型了。")
    else:
        print("⚠️ 合并失败，请检查上方是否有报错信息。")