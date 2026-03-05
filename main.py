import sys
from data_manager import DataManager
from llm_agent import CampusAIAgent

def render_schedule_table(schedule_data):
    """
    终端课表渲染器：将 JSON 数据转化为二维表格打印。
    处理了中文对齐的排版逻辑，让课表在终端显示更美观。
    """
    print("\n" + "="*70)
    print(f"📅 【本学期课表概览】 - {schedule_data.get('semester', '未知学期')}")
    print("="*70)
    
    days = ["周一", "周二", "周三", "周四", "周五"]
    periods = ["1-2节", "3-4节", "午休", "5-6节", "7-8节"]
    
    # 1. 初始化空课表矩阵
    grid = {p: {d: "无课" for d in days} for p in periods}
    
    # 2. 填充午休时间
    for d in days:
        grid["午休"][d] = "🍽️ 自由/午睡"
        
    # 3. 把课程填入矩阵
    for cls in schedule_data.get("classes", []):
        d = cls.get("day_of_week")
        p = cls.get("period")
        # 截取课程名称前6个字，防止表格被撑破
        name = cls.get("course_name", "")
        short_name = name[:6] + ".." if len(name) > 6 else name
        
        if p in grid and d in grid[p]:
            grid[p][d] = short_name

    # 4. 打印表头
    header = f"{'节次':<8} | {'周一':<10} | {'周二':<10} | {'周三':<10} | {'周四':<10} | {'周五':<10}"
    print(header)
    print("-" * 70)
    
    # 5. 打印每一行
    for p in periods:
        # 使用自定义的格式化方式尽量对齐中文终端
        row_str = f"{p:<6} | "
        for d in days:
            # 使用全角空格(chr(12288))填充，解决终端中英文混排对齐问题
            cell = grid[p][d]
            # 计算需要补齐的宽度（假定总宽为6个中文字符）
            pad_len = 6 - len(cell)
            if pad_len > 0:
                cell += chr(12288) * pad_len
            row_str += f"{cell} | "
        print(row_str)


def render_user_profile(habits_data):
    """
    习惯画像生成器：将硬编码的 JSON 转化为有温度的自然语言描述。
    """
    print("\n" + "="*70)
    print("🌟 【你的个性化画像】")
    print("="*70)
    
    b_routine = habits_data.get('basic_routine', {})
    t_habits = habits_data.get('travel_habits', {})
    d_habits = habits_data.get('dietary_habits', {})
    s_habits = habits_data.get('study_habits', {})
    priorities = habits_data.get('high_priorities', [])
    
    print(f"⏰ 【作息】：你通常在 {b_routine.get('wake_up_time')} 起床，晚上 {b_routine.get('sleep_time')} 休息。每天会在 {b_routine.get('nap_time')} 安排 {b_routine.get('nap_duration_mins')} 分钟午休。")
    print(f"🚲 【出行】：你喜欢乘坐{t_habits.get('preferred_transport')}，并且倾向于{t_habits.get('route_preference')}。")
    print(f"🍱 【饮食】：你偏好{d_habits.get('preference')}的食物，{d_habits.get('taboos')}。就餐时你{d_habits.get('meal_time_preference')}。")
    print(f"📚 【学习】：你最喜欢的自习地点是{s_habits.get('preferred_location')}。你的高效时段是 {', '.join(s_habits.get('efficient_time_slots', []))}。")
    print(f"🎯 【近期焦点】：{s_habits.get('current_focus')}")
    
    print("\n🔥 【不可妥协的高优先级习惯】:")
    for idx, p in enumerate(priorities):
        print(f"   {idx+1}. {p}")
    print("="*70 + "\n")


def main():
    print("===================================================")
    print("🎓 欢迎使用 校内行动规划 AI Agent (MVP 版本 - DeepSeek 驱动)")
    print("===================================================\n")

    # 1. 初始化数据管家并加载数据
    print("⏳ 正在加载本地用户数据...")
    data_mgr = DataManager()
    context = data_mgr.get_all_context()
    
    if not context:
        print("❌ 致命错误：数据加载失败，请检查 data 目录下的 JSON 文件！")
        sys.exit(1)
        
    schedule = context['schedule']
    habits = context['habits']
    
    # === 新增：渲染 UI 界面 ===
    render_schedule_table(schedule)
    render_user_profile(habits)
    # ========================

    # 2. 初始化真实的 AI 大脑
    print("⏳ 正在连接 DeepSeek AI 大脑...")
    agent = CampusAIAgent()
    print("✅ AI 大脑已就绪！\n")
    
    # 3. 核心交互循环 (极简控制台 UI)
    while True:
        print("\n" + "="*45)
        print("请选择你要体验的 Agent 功能：")
        print("1. ☀️ [主动推荐] 获取今日核心行动规划与冲突预警")
        print("2. 🔍 [被动推荐] 临时查询与场景推荐")
        print("3. 🚪 退出系统")
        print("="*45)
        
        choice = input("👉 请输入序号 (1/2/3): ").strip()
        
        if choice == '1':
            print("\n[测试配置] 为了测试不同日期的规划，请输入模拟时间。")
            mock_time = input("请输入 (例如: '周一 早上07:30'，直接回车默认为 '周四 早上08:00'): ").strip()
            if not mock_time:
                mock_time = "周四 早上08:00"
            
            print(f"\n[系统触发] 叮！Agent 检测到今天是 {mock_time}，正在请求 DeepSeek 生成规划...\n")
            
            plan = agent.get_active_daily_plan(
                today_info=mock_time, 
                schedule_data=schedule, 
                habits_data=habits
            )
            print(f"🤖 AI Agent 规划结果:\n{plan}")
            
        elif choice == '2':
            print("\n💡 提示：你可以输入任何想问的规划问题。例如：")
            print("  - '今天周四全天没课，我想用 Django 开发 Web 后端功能，帮我规划一下在哪自习比较好？'")
            print("  - '我下午想专心推进 WCCI 2026 会议论文的撰写，推荐个地点？'")
            print("  - '快到午饭时间了，结合我的饮食习惯推荐个去处？'")
            
            user_query = input("\n🗣️ 你的需求是: ").strip()
            if not user_query:
                continue
                
            print("\n[测试配置] 请输入当前的情境时间。")
            mock_time = input("请输入 (例如: '周四 下午14:00'，直接回车默认为 '周四 下午14:00'): ").strip()
            if not mock_time:
                mock_time = "周四 下午14:00"
                
            print(f"\n[系统触发] 正在结合当前情境 ({mock_time}) 深度思考最佳方案...\n")
            
            recommendation = agent.get_passive_recommendation(
                user_query=user_query,
                current_time_info=mock_time,
                schedule_data=schedule,
                habits_data=habits
            )
            print(f"🤖 AI Agent 推荐结果:\n{recommendation}")
            
        elif choice == '3':
            print("\n👋 感谢使用，期待与你共同进化！再见！")
            break
        else:
            print("\n⚠️ 输入有误，请输入 1、2 或 3。")

if __name__ == "__main__":
    main()