import streamlit as st
from openai import OpenAI
import uuid
import random
from datetime import datetime

# ==========================================
# 1. 页面配置 & 增强型 CSS (支持新手引导)
# ==========================================
st.set_page_config(page_title="一念 | 终极版", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .main-title { text-align: center; color: #2E8B57; font-family: 'Georgia', serif; margin-bottom: 0px;}
    .sub-title { text-align: center; color: #666; font-size: 14px; margin-bottom: 30px;}
    .guide-box { border: 2px dashed #E0E0E0; border-radius: 12px; padding: 20px; text-align: center; color: #9E9E9E; font-size: 14px; background-color: rgba(255,255,255,0.5); }
    .leaf-card { padding: 15px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .leaf-focusing { background: #F3E5F5; border-left: 6px solid #9C27B0; border-style: dashed; } 
    .leaf-active { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border-left: 6px solid #4CAF50; }
    .leaf-completed { background: linear-gradient(135deg, #FFFDE7 0%, #FFF9C4 100%); border-right: 6px solid #FFD700; text-align: right; }
    .rebuttal-container { background: #fff; border: 1px solid #E1BEE7; padding: 12px; border-radius: 12px; box-shadow: 0 4px 12px rgba(156, 39, 176, 0.1); }
    .category-badge { background-color: #E0F2F1; color: #00695C; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .time-tag { font-size: 10px; color: #999; font-style: italic; }
    .note-text { font-size: 13px; color: #555; background: rgba(255,255,255,0.5); padding: 8px; border-radius: 5px; margin-top: 5px; text-align: left; border-left: 2px dotted #FFD700;}
</style>
""", unsafe_allow_html=True)

# --- 状态初始化 ---
if 'leaves' not in st.session_state: st.session_state.leaves = []
if 'categories' not in st.session_state: st.session_state.categories = ["💡 认知跃迁", "💰 搞钱事业", "🧘‍♀️ 旷野人生"]
if 'heavy_advice' not in st.session_state: st.session_state.heavy_advice = None

# ==========================================
# 2. AI 助手函数
# ==========================================
def chat_with_ai(prompt_type, content, api_key, api_base):
    if not api_key: return "请配置 API Key。"
    client = OpenAI(api_key=api_key, base_url=api_base)
    if prompt_type == "init": msg = "行动教练。指出价值并给第一步。"
    elif prompt_type == "heavy": msg = "犀利PM。指风险并给MVP方案。"
    elif prompt_type == "heavy_retry": msg = "变通教练。根据反驳给方案。"
    elif prompt_type == "complete_and_categorize":
        cat_str = "、".join(st.session_state.categories)
        msg = f"归类。从 [{cat_str}] 选一并鼓励。格式：类别 || 鼓励。"
    try:
        res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": msg}, {"role": "user", "content": content}])
        return res.choices[0].message.content
    except Exception as e: return f"AI 休息中...({e})"

# ==========================================
# 3. 侧边栏 (静默读取 Secrets)
# ==========================================
with st.sidebar:
    st.header("⚙️ 能量源")
    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    api_base = "https://api.deepseek.com/v1"

    if api_key:
        st.success("✨ 已安全连接专属 AI")
    else:
        api_key = st.text_input("DeepSeek Key", type="password")
        api_base = st.text_input("API Base", value="https://api.deepseek.com/v1")
    
    st.divider()
    st.header("🌿 枝桠管理")
    new_cat = st.text_input("新增分类：")
    if st.button("➕ 添加") and new_cat:
        if new_cat not in st.session_state.categories: st.session_state.categories.append(new_cat); st.rerun()

# ==========================================
# 4. 顶部布局 (新手引导)
# ==========================================
st.markdown("<h1 class='main-title'>🌿 一 念</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>化瞬间灵感，为生命之树</p>", unsafe_allow_html=True)

if not api_key:
    st.warning("🔑 请先在左侧边栏填入 API Key。")
    st.stop()

header_left, header_right = st.columns([1.5, 1])

with header_left:
    st.subheader("🍃 定义灵感")
    new_idea = st.text_area(
        "输入灵感...", height=100, key="idea_in", label_visibility="collapsed",
        placeholder="『示例』：我想学滑板、去宿舍楼下卖旧书、这周末看一本心理学书。"
    )
    c1, c2, c3 = st.columns(3)
    t_w = c1.slider("⏳ 时间", 1, 10, 5)
    m_w = c2.slider("💰 金钱", 1, 10, 5)
    e_w = c3.slider("🔋 耗神", 1, 10, 5)
    total_w = t_w + m_w + e_w

    if st.button("✨ 凝结初叶", use_container_width=True):
        if new_idea:
            if total_w >= 21:
                st.session_state.heavy_advice = chat_with_ai("heavy", new_idea, api_key, api_base)
                st.session_state.heavy_idea_temp = new_idea; st.rerun()
            else:
                st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": new_idea, "status": "focusing", "ai_prompt": "", "reward_text": "", "weight": total_w, "detail": "", "category": "未分类", "notes": "", "done_time": None})
                st.session_state.heavy_advice = None; st.rerun()

with header_right:
    if st.session_state.heavy_advice:
        st.markdown("<div class='rebuttal-container'>", unsafe_allow_html=True)
        st.info(f"🤖 **AI 对线：**\n{st.session_state.heavy_advice}")
        reb = st.text_input("💬 对线理由：", key="reb")
        col1, col2 = st.columns(2)
        if col1.button("🔄 重划"): st.session_state.heavy_advice = chat_with_ai("heavy_retry", f"{st.session_state.heavy_idea_temp}\n{reb}", api_key, api_base); st.rerun()
        if col2.button("🎯 听劝"): 
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": f"【降维】{st.session_state.heavy_idea_temp}", "status": "focusing", "ai_prompt": st.session_state.heavy_advice, "reward_text": "", "weight": 5, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        if st.button("🚀 头铁", use_container_width=True):
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": st.session_state.heavy_idea_temp, "status": "focusing", "ai_prompt": "⚠️警告", "reward_text": "", "weight": total_w, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='guide-box' style='height:215px; display:flex; align-items:center; justify-content:center;'>⚖️ AI 重力监测区</div>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. 生命树区域 (左右对峙)
# ==========================================
left_tree, right_tree = st.columns(2)

with left_tree:
    st.subheader("🌳 呼吸枝桠")
    active_l = [L for L in st.session_state.leaves if L["status"] == "active"]
    focus_l = [L for L in st.session_state.leaves if L["status"] == "focusing"]
    
    if not focus_l and not active_l:
        st.markdown("<div class='guide-box'>这里展示进行中的灵感。</div>", unsafe_allow_html=True)
    
    for l in focus_l:
        st.markdown(f'<div class="leaf-card leaf-focusing">{l["content"]}</div>', unsafe_allow_html=True)
        det = st.text_input("第一步计划？", key=f"det_{l['id']}")
        if st.button("☀️ 激活", key=f"act_{l['id']}"):
            l["ai_prompt"] = chat_with_ai("init", f"{l['content']}\n{det}", api_key, api_base)
            l["detail"] = det; l["status"] = "active"; st.rerun()

    if active_l:
        tabs = st.tabs(["🌐 全景"] + st.session_state.categories + ["📦 未分类"])
        for i, tab_n in enumerate(["🌐 全景"] + st.session_state.categories + ["📦 未分类"]):
            with tabs[i]:
                cur = active_l if i==0 else [L for L in active_l if L.get("category") == tab_n.replace("📦 ","")]
                for l in cur:
                    st.markdown(f'<div class="leaf-card leaf-active"><b>{l["content"]}</b></div>', unsafe_allow_html=True)
                    if st.button("✅ 完成", key=f"do_{l['id']}_{i}"):
                        res = chat_with_ai("complete_and_categorize", l["content"], api_key, api_base)
                        p = res.split("||") if "||" in res else ["未分类", res]
                        l["category"] = p[0].strip(); l["reward_text"] = p[1].strip(); l["status"] = "completed"; l["done_time"] = datetime.now(); st.rerun()

with right_tree:
    st.subheader("🌟 璀璨之林")
    comp_l = [L for L in st.session_state.leaves if L["status"] == "completed"]
    comp_l.sort(key=lambda x: x["done_time"] if x["done_time"] else datetime.min)
    
    if not comp_l:
        st.markdown("<div class='guide-box'>这里是你的成就墙。</div>", unsafe_allow_html=True)
    else:
        tabs_r = st.tabs(["🌐 全景"] + st.session_state.categories + ["📦 未分类"])
        for i, tab_n in enumerate(["🌐 全景"] + st.session_state.categories + ["📦 未分类"]):
            with tabs_r[i]:
                cur_r = comp_l if i==0 else [L for L in comp_l if L.get("category") == tab_n.replace("📦 ","")]
                for l in cur_r:
                    st.markdown(f'<div class="leaf-card leaf-completed"><b>{l["content"]}</b><br><small>“{l["reward_text"]}”</small></div>', unsafe_allow_html=True)
                    with st.popover("📝 笔记", key=f"pop_{l['id']}_{i}"):
                        l["notes"] = st.text_area("记录感悟", value=l["notes"], key=f"nt_{l['id']}_{i}")
                        if st.button("保存", key=f"sv_{l['id']}_{i}"): st.rerun()
