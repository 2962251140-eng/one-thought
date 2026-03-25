import streamlit as st
from openai import OpenAI
import uuid
import random
from datetime import datetime

# ==========================================
# 1. 页面配置 & 增强型 CSS
# ==========================================
st.set_page_config(page_title="一念 | 灵感全生命周期版", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .main-title { text-align: center; color: #2E8B57; font-family: 'Georgia', serif; margin-bottom: 0px;}
    .sub-title { text-align: center; color: #666; font-size: 14px; margin-bottom: 30px;}
    .guide-box { border: 2px dashed #E0E0E0; border-radius: 12px; padding: 20px; text-align: center; color: #9E9E9E; font-size: 13px; background-color: rgba(255,255,255,0.5); }
    .leaf-card { padding: 15px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); position: relative;}
    .leaf-focusing { background: #F3E5F5; border-left: 6px solid #9C27B0; border-style: dashed; } 
    .leaf-active { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border-left: 6px solid #4CAF50; }
    .leaf-completed { background: linear-gradient(135deg, #FFFDE7 0%, #FFF9C4 100%); border-right: 6px solid #FFD700; text-align: right; }
    .leaf-soil { background: #EFEBE9; border-left: 6px solid #8D6E63; color: #5D4037; opacity: 0.8;}
    
    .rebuttal-container { background: #fff; border: 1px solid #E1BEE7; padding: 12px; border-radius: 12px; box-shadow: 0 4px 12px rgba(156, 39, 176, 0.1); }
    .ai-analysis-text { font-size: 12.5px; color: #4A148C; line-height: 1.5; margin-bottom: 10px; }
    .ai-label { font-size: 11px; font-weight: bold; color: #9C27B0; text-transform: uppercase; margin-bottom: 2px; }
    .category-badge { background-color: #E0F2F1; color: #00695C; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; margin-bottom: 5px; display: inline-block;}
</style>
""", unsafe_allow_html=True)

# --- 状态初始化 ---
if 'leaves' not in st.session_state: st.session_state.leaves = []
if 'categories' not in st.session_state: st.session_state.categories = ["💡 认知跃迁", "💰 搞钱事业", "🧘‍♀️ 旷野人生"]
if 'heavy_advice' not in st.session_state: st.session_state.heavy_advice = None

def chat_with_ai(prompt_type, content, api_key, api_base):
    if not api_key: return "请配置 API Key。"
    client = OpenAI(api_key=api_key, base_url=api_base)
    if prompt_type == "init": msg = "行动教练。给出一个100字内的极简第一步。"
    elif prompt_type == "heavy": msg = "犀利PM。说出1项最大风险，并给出一个100字内的建议。精炼。"
    elif prompt_type == "heavy_retry": msg = "针对用户的反馈，给出一个针对性的、100字内的执行策略。"
    elif prompt_type == "complete_and_categorize":
        cat_str = "、".join(st.session_state.categories)
        msg = f"归类。从 [{cat_str}] 选一并鼓励。格式：类别 || 鼓励。"
    try:
        res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": msg}, {"role": "user", "content": content}])
        return res.choices[0].message.content
    except: return "AI 休息中..."

# ==========================================
# 3. 侧边栏 & 顶部布局
# ==========================================
with st.sidebar:
    st.header("⚙️ 能量源")
    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    api_base = "https://api.deepseek.com/v1"
    if api_key: st.success("✨ 已安全连接 AI")
    else: api_key = st.text_input("DeepSeek Key", type="password")
    
    st.divider()
    st.header("🌿 枝桠管理")
    new_cat = st.text_input("新增分类：")
    if st.button("➕ 添加") and new_cat:
        if new_cat not in st.session_state.categories: st.session_state.categories.append(new_cat); st.rerun()

st.markdown("<h1 class='main-title'>🌿 一 念</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>化瞬间灵感，为生命之树</p>", unsafe_allow_html=True)

if not api_key: st.warning("🔑 请在侧边栏填入 Key。"); st.stop()

# --- 灵感定义区 ---
header_left, header_right = st.columns([1.5, 1])
with header_left:
    new_idea = st.text_area("输入灵感...", height=100, placeholder="『示例』：我想学滑板...", label_visibility="collapsed")
    c1, c2, c3 = st.columns(3)
    t_w, m_w, e_w = c1.slider("⏳ 时间", 1, 10, 5), c2.slider("💰 金钱", 1, 10, 5), c3.slider("🔋 耗神", 1, 10, 5)
    if st.button("✨ 凝结初叶", use_container_width=True):
        if new_idea:
            if (t_w+m_w+e_w) >= 21:
                st.session_state.heavy_advice = chat_with_ai("heavy", new_idea, api_key, api_base)
                st.session_state.heavy_idea_temp = new_idea; st.rerun()
            else:
                st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": new_idea, "status": "focusing", "ai_prompt": "", "reward_text": "", "category": "未分类", "notes": "", "done_time": None})
                st.session_state.heavy_advice = None; st.rerun()

with header_right:
    if st.session_state.heavy_advice:
        st.markdown("<div class='rebuttal-container'><div class='ai-label'>🔍 AI 分析</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-analysis-text'>{st.session_state.heavy_advice}</div>", unsafe_allow_html=True)
        reb = st.text_input("💬 继续交流：", key="reb")
        col1, col2 = st.columns(2)
        if col1.button("🔄 重新分析"): st.session_state.heavy_advice = chat_with_ai("heavy_retry", f"{st.session_state.heavy_idea_temp}\n{reb}", api_key, api_base); st.rerun()
        if col2.button("🎯 听取建议"): 
        if st.button("🚀 头铁执行", use_container_width=True):
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": f"{st.session_state.heavy_idea_temp}", "status": "focusing", "ai_prompt": st.session_state.heavy_advice, "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else: st.markdown("<div class='guide-box' style='height:215px; display:flex; align-items:center; justify-content:center;'>⚖️ AI 分析区</div>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. 生命树核心逻辑 (含土壤)
# ==========================================
left_tree, right_tree = st.columns(2)

with left_tree:
    st.subheader("🌳 呼吸枝桠")
    active_l = [L for L in st.session_state.leaves if L["status"] == "active"]
    focus_l = [L for L in st.session_state.leaves if L["status"] == "focusing"]
    
    for l in focus_l:
        st.markdown(f'<div class="leaf-card leaf-focusing">{l["content"]}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        det = c1.text_input("第一步？", key=f"det_{l['id']}")
        if c1.button("☀️ 激活", key=f"act_{l['id']}"):
            l["ai_prompt"] = chat_with_ai("init", f"{l['content']}\n{det}", api_key, api_base)
            l["detail"] = det; l["status"] = "active"; st.rerun()
        if c2.button("🍂 丢弃", key=f"del_f_{l['id']}"): l["status"] = "soil"; st.rerun()

    if active_l:
        tabs = st.tabs(["🌐 全景"] + st.session_state.categories + ["📦 未分类"])
        for i, tab_n in enumerate(["🌐 全景"] + st.session_state.categories + ["📦 未分类"]):
            with tabs[i]:
                cur = active_l if i==0 else [L for L in active_l if L.get("category") == tab_n.replace("📦 ","")]
                for l in cur:
                    st.markdown(f'<div class="leaf-card leaf-active"><b>{l["content"]}</b></div>', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 1])
                    if c1.button("✅ 完成", key=f"do_{l['id']}_{i}"):
                        res = chat_with_ai("complete_and_categorize", l["content"], api_key, api_base)
                        p = res.split("||") if "||" in res else ["未分类", res]
                        l["category"] = p[0].strip(); l["reward_text"] = p[1].strip(); l["status"] = "completed"; l["done_time"] = datetime.now(); st.rerun()
                    if c2.button("🍂 移至土壤", key=f"del_a_{l['id']}_{i}"): l["status"] = "soil"; st.rerun()

with right_tree:
    st.subheader("🌟 璀璨之林")
    comp_l = [L for L in st.session_state.leaves if L["status"] == "completed"]
    if not comp_l: st.markdown("<div class='guide-box'>成就墙待点亮</div>", unsafe_allow_html=True)
    else:
        tabs_r = st.tabs(["🌐 全景"] + st.session_state.categories + ["📦 未分类"])
        for i, tab_n in enumerate(["🌐 全景"] + st.session_state.categories + ["📦 未分类"]):
            with tabs_r[i]:
                cur_r = [L for L in comp_l if i==0 or L.get("category") == tab_n.replace("📦 ","")]
                for l in cur_r:
                    st.markdown(f'<div class="leaf-card leaf-completed"><span class="category-badge">{l.get("category","未分类")}</span><br><b>{l["content"]}</b></div>', unsafe_allow_html=True)
                    if st.button("🍂 归于土壤", key=f"del_c_{l['id']}_{i}"): l["status"] = "soil"; st.rerun()

st.divider()
# --- 土壤区 (暂存区) ---
with st.expander("🪨 土壤 (暂存与埋葬区)"):
    soil_l = [L for L in st.session_state.leaves if L["status"] == "soil"]
    if not soil_l: st.caption("土壤里空空如也，这里可以容纳你暂时放下的灵感。")
    for l in soil_l:
        st.markdown(f'<div class="leaf-card leaf-soil">{l["content"]}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🌱 复用上树", key=f"rev_{l['id']}"): l["status"] = "focusing"; st.rerun()
        if c2.button("⚰️ 永久埋葬", key=f"bury_{l['id']}"): st.session_state.leaves.remove(l); st.rerun()
