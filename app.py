import streamlit as st
from data_manager import DataManager
from llm_agent import CampusAIAgent

# ==========================================
# 页面全局配置
# ==========================================
st.set_page_config(
    page_title="AI 校园行动规划指南",
    page_icon="🎓",
    layout="wide"
)

# ==========================================
# 数据与 AI 初始化 (使用 st.cache_resource 避免重复加载)
# ==========================================
@st.cache_resource
def init_system():
    data_mgr = DataManager()
    context = data_mgr.get_all_context()
    agent = CampusAIAgent()
    return context, agent

context, agent = init_system()

if not context:
    st.error("❌ 数据加载失败，请检查 data 目录下的 JSON 文件！")
    st.stop()

schedule_data = context['schedule']
habits_data = context['habits']

# ==========================================
# 左侧边栏 (Sidebar) - 配置与画像
# ==========================================
with st.sidebar:
    st.header("⚙️ 全局设置")
    # 模拟时间控制器，方便测试
    current_time = st.text_input("🕒 当前模拟时间", value="周四 14:00", help="修改此时间可测试 AI 在不同情境下的规划逻辑")
    
    st.divider()
    
    st.header("🌟 你的个性化画像")
    b_routine = habits_data.get('basic_routine', {})
    s_habits = habits_data.get('study_habits', {})
    priorities = habits_data.get('high_priorities', [])
    
    st.write(f"**⏰ 作息：** {b_routine.get('wake_up_time')} 起床 | {b_routine.get('sleep_time')} 休息")
    st.write(f"**🎯 焦点：** {s_habits.get('current_focus')}")
    
    st.markdown("**🔥 高优习惯：**")
    for p in priorities:
        st.caption(f"- {p}")

# ==========================================
# 主功能区 (Main Area)
# ==========================================
st.title("🎓 校内行动规划 AI Agent")
st.markdown("基于 DeepSeek 大模型驱动，为你提供极其务实的校园行动建议。")

# 使用 Tabs 切换不同功能模块
tab1, tab2, tab3 = st.tabs(["📅 我的课表", "☀️ 行动规划", "🔍 智能问答"])

# --- Tab 1: 课表展示 ---
with tab1:
    st.subheader(f"本学期课表 - {schedule_data.get('semester', '')}")
    # Streamlit 会自动将包含字典的列表渲染为漂亮的交互式数据表
    st.dataframe(schedule_data.get('classes', []), use_container_width=True)

# --- Tab 2: 主动规划 ---
with tab2:
    st.subheader("☀️ 每日核心行动规划")
    st.info(f"AI 将基于左侧边栏设定的时间（**{current_time}**）为你生成接下来的规划。")
    
    if st.button("🚀 生成 / 更新今日规划", type="primary"):
        with st.spinner("DeepSeek 正在思考你的最佳路线..."):
            plan = agent.get_active_daily_plan(
                today_info=current_time, 
                schedule_data=schedule_data, 
                habits_data=habits_data
            )
            st.success("规划生成完毕！")
            st.markdown(plan)

# --- Tab 3: 被动推荐 ---
with tab3:
    st.subheader("🔍 场景推荐与智能问答")
    
    # 预设几个贴合你实际学习情况的 Prompt 示例，降低输入门槛
    example_prompts = [
        "下午没课，推荐个适合用 Pygame 做游戏开发的自习室？",
        "晚上想专心推进 WCCI 论文撰写，结合我的习惯给个建议。",
        "按艾宾浩斯遗忘曲线，帮我规划一下今天剩余的英语词汇复习时间。",
        "刚上完课，中午去哪里吃饭比较好？"
    ]
    
    selected_example = st.selectbox("💡 试试这些快捷提问，或在下方输入你的需求：", ["(自定义输入)"] + example_prompts)
    
    user_query = st.text_area("🗣️ 你的需求是：", value="" if selected_example == "(自定义输入)" else selected_example)
    
    if st.button("💡 提交需求"):
        if not user_query.strip():
            st.warning("请输入你的需求！")
        else:
            with st.spinner(f"正在结合当前情境 ({current_time}) 深度思考..."):
                recommendation = agent.get_passive_recommendation(
                    user_query=user_query,
                    current_time_info=current_time,
                    schedule_data=schedule_data,
                    habits_data=habits_data
                )
                st.markdown("### 🤖 AI 建议")
                st.write(recommendation)