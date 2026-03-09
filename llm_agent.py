#Q：你怎么保证你的规划是合理的
#A：我们的智能体是React架构：提出问题，草拟答案，思考能否回答，若不行，继续草拟答案，思考能否回答；直到若行，输出答案；

#Q：你的框架是什么。langchain还是langgraph
#A：我用的是CoT（call of tools），用openai库

import json
from openai import OpenAI###Q：openai库？，使用智能体百分百要用的库，三个参数，导入智能体的

class CampusAIAgent:
    """
    校园AI助手大脑类：负责将本地数据转化为 Prompt，并与真实的 DeepSeek 大模型交互。
    """
    #正常一般是要写.env文件
    def __init__(self, api_key="sk-e1a059c5a2e2471ab11ee30f2d0a19f1", base_url="https://api.deepseek.com", model="deepseek-chat"):
        """
        初始化真实的 DeepSeek 客户端。
        使用 DeepSeek 的官方兼容接口和 deepseek-chat 模型。
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)

    def _build_system_prompt(self, schedule_data, habits_data):#Q：二者区别；系统提示词：你给大模型的角色设计；user_promot：你说的话
        """
        私有方法：构建系统提示词 (System Prompt)。
        这是整个 Agent 最核心的“灵魂”，决定了它回答的质量和逻辑。
        """
        # 将 Python 字典转化为排版良好的 JSON 字符串，喂给大模型
        schedule_str = json.dumps(schedule_data, ensure_ascii=False, indent=2)
        habits_str = json.dumps(habits_data, ensure_ascii=False, indent=2)#Q：你的系统提示词设计思路：系统提示词的思路：设定任务和角色、（给他数据）、提出要求
        
        system_prompt = f"""你是一个专门为大学生设计的“校内行动规划AI助手”。
你的核心任务是根据用户的【课表数据】和【个人习惯数据】，提供极其务实、没有废话的行动建议。

【当前用户的课表数据】：
{schedule_str}

【当前用户的个人习惯数据】：
{habits_str}

【你的工作原则（严格遵守）】：
1. 冲突预警：必须优先保证课表不冲突。如果发现用户想做的事与课表冲突，或与高优先级习惯冲突，必须明确提出预警！
2. 尊重习惯：严格尊重用户的出行、饮食、作息偏好，不要推荐违背习惯的建议。
3. 务实简短：回答要像一个专业的私人助理，直接给出建议、地点、时间，不需要讲大道理和废话。
"""
        return system_prompt

    def _call_llm(self, system_prompt, user_message):
        """
        私有方法：向 DeepSeek 发起真实的 API 请求并返回结果。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7 # 0.7 比较适合在逻辑性和创造性之间找平衡
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ 调用 DeepSeek API 时发生错误：{e}"  #Q：怎么调用大模型；A：Openai包内部方法，传入我的三个关键参数就行

    # ==========================================
    # 以下为对外的核心业务方法 (MVP 闭环功能)
    # ==========================================

    def get_active_daily_plan(self, today_info, schedule_data, habits_data):
        """主动推荐：生成每日基础行动规划与冲突预警"""
        sys_prompt = self._build_system_prompt(schedule_data, habits_data)
        #Q:功能1：系统当天8am主动给用户弹消息，结合用户今日课表、习惯、出行偏好给出一个规划建议
        
        # ⚠️ 核心修复点：通过强指令（Prompt）锁死时间锚点，杜绝大模型规划过去的时间
        user_msg = (
            f"现在的时间是：【{today_info}】。\n"
            f"请为我生成从【现在这一刻开始，到今天结束】的核心行动规划。\n"
            f"【时间红线警告】：绝对不要为已经过去的时间安排任务！对于当前时间点之前的课程或习惯，最多只能一笔带过或直接忽略。\n"
            f"请重点关注接下来即将发生的课程安排、我的高优先级任务，并在需要时提前给出出行和冲突预警。"
        )
        
        return self._call_llm(sys_prompt, user_msg)

    def get_passive_recommendation(self, user_query, current_time_info, schedule_data, habits_data):
        """被动推荐：处理用户的个性化查询与出行推荐"""
        sys_prompt = self._build_system_prompt(schedule_data, habits_data)
        #功能2：用户主动询问某个时间后的安排，智能体根据后续用户今日课表、习惯、出行偏好给出最合适的规划建议
        user_msg = f"当前时间/情境：{current_time_info}。\n用户的需求是：【{user_query}】。\n请结合我的数据给出最直接的推荐。"
        
        return self._call_llm(sys_prompt, user_msg)


# ==========================================
# 本地测试模块（独立运行此文件时执行）
# ==========================================
if __name__ == "__main__":
    try:
        from data_manager import DataManager
    except ImportError:
        print("❌ 找不到 data_manager.py，请确保它们在同一个文件夹下！")
        exit()

    print("🚀 开始测试 llm_agent (真实 DeepSeek 大脑)...\n")
    print("⏳ 正在请求 API，这可能需要几秒钟...\n")
    
    data_mgr = DataManager()
    context = data_mgr.get_all_context()
    
    if not context:
        print("⚠️ 读取数据失败，请先修复 data_manager.py 的问题。")
        exit()
        
    schedule = context['schedule']
    habits = context['habits']

    # 实例化真实的 Agent
    agent = CampusAIAgent() 
    
    print("=============================================")
    print("场景 1: 测试【主动推荐】(每日清晨规划)")
    print("=============================================")
    plan = agent.get_active_daily_plan(today_info="周四 早上07:30", schedule_data=schedule, habits_data=habits)
    print(f"👉 DeepSeek 输出:\n{plan}\n")

    print("=============================================")
    print("场景 2: 测试【被动推荐】(临时查询)")
    print("=============================================")
    recommendation = agent.get_passive_recommendation(
        user_query="刚上完课，中午去哪里吃饭比较好？", 
        current_time_info="周一 中午12:00", 
        schedule_data=schedule, 
        habits_data=habits
    )
    print(f"👉 DeepSeek 输出:\n{recommendation}\n")