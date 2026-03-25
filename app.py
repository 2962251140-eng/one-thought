import streamlit as st
from openai import OpenAI
import uuid
import random
from datetime import datetime

# ==========================================
# 1. 页面配置 & 增强型 CSS (新手引导+左右布局)
# ==========================================
st.set_page_config(page_title="一念 | 终极版", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .main-title { text-align: center; color: #2E8B57; font-family: 'Georgia', serif; margin-bottom: 0px;}
    .sub-title { text-align: center; color: #666; font-size: 14px; margin-bottom: 30px;}
    
    /* 引导性空态框 */
    .guide-box { 
        border: 2px dashed #E0E0E0; border-radius: 12px; padding: 20px; 
        text-align: center; color: #9E9E9E; font-size: 14px;
        background-color: rgba(255,255,255,0.5);
    }

    .leaf-card { padding: 15px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .leaf-focusing { background: #F3E5F5; border-left: 6px solid #9C27B0; border-style: dashed; } 
    .leaf-active { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border-left: 6px solid #4CAF50; }
    .leaf-completed { background: linear-gradient(135deg, #FFFDE7 0%, #FFF9C4 100%); border-right: 6px solid #FFD700; text-align: right; }
    .leaf-soil { background: #EFEBE9; border-left: 6px solid #8D6E63; color: #5D4037;}
    
    .rebuttal-container { background: #fff; border: 1px solid #E1BEE7; padding: 12px; border-radius: 12px; box-shadow: 0 4px 12px rgba(156, 39, 176, 0.1); }
    .category-badge { background-color: #E0F2F1; color: #00695C; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .time-tag { font-size: 10px; color: #999; font-style: italic; }
    .note-text { font-size: 13px; color: #555; background: rgba(255,255,255,0.5); padding: 8px; border-radius: 5px; margin-top: 5px; text-align: left; border-left: 2px dotted #FFD700;}
</style>
""", unsafe_allow_html=True)

# --- 状态初始化 ---
if 'leaves' not in st.session_state: st.session_state.leaves = []
if 'grafting_pair' not in st.session_state: st.session_state.grafting_pair = []
if 'heavy_advice' not in st.session_state: st.session_state.heavy_advice = None
if 'heavy_idea_temp' not in st.session_state: st.session_state.heavy_idea_temp = ""
if 'categories' not in st.session_state: 
    st.session_state.categories = ["💡 认知跃迁", "💰 搞钱事业", "🧘‍♀️ 旷野人生"]

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
# 3. 侧边栏 (安全密钥静默读取版)
# ==========================================
with st.sidebar:
    st.header("⚙️ 能量源")
    
    api_key = ""
    api_base = "https://api.deepseek.com/v1"

    # 尝试静默读取 (Secrets)
    if "DEEPSEEK_API_KEY" in st.secrets:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        st.success("✨ 已通过 Secrets 安全连接 AI")
    else:
        api_key = st.text_input("DeepSeek Key (未检测到预设，请手动输入)", type="password")
        api_base = st.text_input("API Base", value="https://api.deepseek.com/v1")
    
    st.divider()
    st.header("🌿 枝桠管理")
    new_cat = st.text_input("新增分类：", key="sidebar_add_cat")
    if st.button("➕ 添加", key="btn_add_cat") and new_cat:
        if new_cat not in st.session_state.categories: 
            st.session_state.categories.append(new_cat); st.rerun()
            
    for idx, cat in enumerate(st.session_state.categories):
        with st.expander(f"📍 {cat}"):
            new_n = st.text_input("改名", value=cat, key=f"ren_c_{idx}")
            if st.button("保存", key=f"sv_c_{idx}"):
                for l in st.session_state.leaves:
                    if l.get("category") == cat: l["category"] = new_n
                st.session_state.categories[idx] = new_n; st.rerun()
            if st.button("删除", key=f"dl_c_{idx}"):
                st.session_state.categories.remove(cat)
                for l in st.session_state.leaves:
                    if l.get("category") == cat: l["category"] = "未分类"
                st.rerun()

# ==========================================
# 4. 顶部布局：灵感捕获 (Placeholders 引导)
# ==========================================
st.markdown("<h1 class='main-title'>🌿 一 念</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>化瞬间灵感，为生命之树</p>", unsafe_allow_html=True)

if not api_key:
    st.warning("🔑 请先在左侧边栏填入 API Key，激活一念。")
    st.stop()

# 新手 Tip
if not st.session_state.leaves:
    st.info("👋 **欢迎开启《一念》**。尝试在下方输入一个微小的念头，看看它会如何生长。")

header_left, header_right = st.columns([1.5, 1])

with header_left:
    st.subheader("🍃 定义灵感")
    new_idea = st.text_area(
        "在此输入你的灵感...", height=100, key="idea_in", label_visibility="collapsed",
        placeholder="『叶子用途』：记录一个想做还没做的念头、一个新点子、或一个小计划。\n『示例』：我想学滑板、去宿舍楼下卖旧书、这周末看一本心理学书。"
    )
    st.caption("👇 **重力评估**：评估实现这个想法需要耗费的时间、金钱和精力资源。")
    c1, c2, c3 = st.columns(3)
    t_w = c1.slider("⏳ 时间", 1, 10, 5, help="完成这件事需要多少时间成本？")
    m_w = c2.slider("💰 金钱", 1, 10, 5, help="需要多少资金投入？")
    e_w = c3.slider("🔋 耗神", 1, 10, 5, help="心理压力或勇气成本大吗？")
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
        st.info(f"🤖 **AI 对线建议：**\n{st.session_state.heavy_advice}")
        reb = st.text_input("💬 反驳：", key="reb", placeholder="比如：我有空 / 设备已买齐...")
        col_reb1, col_reb2 = st.columns(2)
        if col_reb1.button("🔄 重新规划"): st.session_state.heavy_advice = chat_with_ai("heavy_retry", f"{st.session_state.heavy_idea_temp}\n{reb}", api_key, api_base); st.rerun()
        if col_reb2.button("🎯 采纳"): 
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": f"【降维】{st.session_state.heavy_idea_temp}", "status": "focusing", "ai_prompt": st.session_state.heavy_advice, "reward_text": "", "weight": 5, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        if st.button("🚀 直接生成", use_container_width=True):
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": st.session_state.heavy_idea_temp, "status": "focusing", "ai_prompt": "⚠️重力警告", "reward_text": "", "weight": total_w, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='guide-box' style='height:215px; display:flex; flex-direction:column; justify-content:center;'><div>⚖️ <b>AI 重力检测区</b></div><div style='margin-top:10px;'>当想法重力过高（总分≥21）时，AI 会现身协助你进行拆解。</div></div>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. 生命树核心区 (左右对峙布局)
# ==========================================
left_tree, right_tree = st.columns(2)

with left_tree:
    st.subheader("🌳 呼吸枝桠 (未完成)")
    focus_l = [L for L in st.session_state.leaves if L["status"] == "focusing"]
    active_l = [L for L in st.session_state.leaves if L["status"] == "active"]
    
    if not focus_l and not active_l:
        st.markdown("<div class='guide-box'>这里展示<b>『进行中』</b>的灵感。<br>新点子需注入第一步行动计划方能激活。</div>", unsafe_allow_html=True)

    if focus_l:
        st.caption("✨ 待激活的初叶")
        for l in focus_l:
            st.markdown(f'<div class="leaf-card leaf-focusing">{l["content"]}</div>', unsafe_allow_html=True)
            det = st.text_input("第一步计划？", key=f"det_{l['id']}", placeholder="如：买书 / 查路线 / 打个电话")
            if st.button("☀️ 激活上树", key=f"act_{l['id']}"):
                if det:
                    l["ai_prompt"] = chat_with_ai("init", f"{l['content']}\n{det}", api_key, api_base)
                    l["detail"] = det; l["status"] = "active"; st.rerun()
    
    if active_l:
        cat_tabs_left = st.tabs(["🌐 全景"] + st.session_state.categories + ["📦 未分类"])
        for i, tab_n in enumerate(["🌐 全景"] + st.session_state.categories + ["📦 未分类"]):
            with cat_tabs_left[i]:
                cur_tab_leaves = active_l if i==0 else [L for L in active_l if L.get("category") == tab_n.replace("📦 ","")]
                for l in cur_tab_leaves:
                    st.markdown(f'<div class="leaf-card leaf-active"><b>{l["content"]}</b><br><small>👣 {l.get("detail","")}<br>🤖 {l["ai_prompt"]}</small></div>', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([2, 1, 1])
                    if c1.button("✅ 完成", key=f"do_{l['id']}_{i}", use_container_width=True):
                        res = chat_with_ai("complete_and_categorize", l["content"], api_key, api_base)
                        if "||" in res:
                            p = res.split("||"); l["category"] = p[0].strip(); l["reward_text"] = p[1].strip()
                        else: l["reward_text"] = res; l["category"] = "未分类"
                        l["status"] = "completed"; l["done_time"] = datetime.now(); st.rerun()
                    if c2.button("🍂 搁置", key=f"dr_{l['id']}_{i}"): l["status"] = "soil"; st.rerun()
                    with c3:
                        with st.popover("⚙️", key=f"pop_a_{l['id']}_{i}"):
                            nc = st.selectbox("修改分类", ["未分类"] + st.session_state.categories, key=f"mc_a_{l['id']}_{i}")
                            if st.button("确认", key=f"sv_mc_{l['id']}_{i}"): l["category"] = nc; st.rerun()
                            if st.button("删除", key=f"dl_a_{l['id']}_{i}"): st.session_state.leaves.remove(l); st.rerun()

with right_tree:
    st.subheader("🌟 璀璨之林 (成就归档)")
    comp_l = [L for L in st.session_state.leaves if L["status"] == "completed"]
    comp_l.sort(key=lambda x: x["done_time"] if x["done_time"] else datetime.min)
    
    if not comp_l:
        st.markdown("<div class='guide-box'>这里是你的<b>『勋章墙』</b>。<br>点亮后的灵感会按时间顺序在此排列。</div>", unsafe_allow_html=True)
    else:
        cat_tabs_right = st.tabs(["🌐 全景"] + st.session_state.categories + ["📦 未分类"])
        for i, tab_n in enumerate(["🌐 全景"] + st.session_state.categories + ["📦 未分类"]):
            with cat_tabs_right[i]:
                cur_tab_leaves = comp_l if i==0 else [L for L in comp_l if L.get("category") == tab_n.replace("📦 ","")]
                for l in cur_tab_leaves:
                    st.markdown(f"""
                    <div class="leaf-card leaf-completed">
                        <span class="category-badge">{l.get('category','未分类')}</span>
                        <div class="time-tag">{l['done_time'].strftime('%m-%d %H:%M')}</div>
                        <p><b>{l['content']}</b></p>
                        <p style="color:#B8860B; font-size:12px;">“{l['reward_text']}”</p>
                        {f'<div class="note-text">📝 <b>心路历程：</b>{l["notes"]}</div>' if l["notes"] else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    with st.popover("📝 笔记 / ⚙️ 管理", key=f"pop_c_{l['id']}_{i}", use_container_width=True):
                        new_n = st.text_area("记录感悟...", value=l["notes"], key=f"nt_{l['id']}_{i}", placeholder="实现此念头时的心情...")
                        if st.button("保存笔记", key=f"sv_nt_{l['id']}_{i}"): l["notes"] = new_n; st.rerun()
                        st.divider()
                        nc = st.selectbox("重选枝桠", ["未分类"] + st.session_state.categories, key=f"mc_c_{l['id']}_{i}")
                        if st.button("确认迁移", key=f"sv_c_c_{l['id']}_{i}"): l["category"] = nc; st.rerun()
                        if st.button("彻底移除", key=f"del_c_{l['id']}_{i}"): st.session_state.leaves.remove(l); st.rerun()

st.divider()
with st.expander("🪨 土壤 (暂存区)"):
    s_l = [L for L in st.session_state.leaves if L["status"] == "soil"]
    if not s_l: st.caption("目前土壤里还没有落叶...")
    for l in s_l:
        st.markdown(f'<div class="leaf-card leaf-soil">{l["content"]}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🌱 复用上树", key=f"rv_{l['id']}"): l["status"] = "focusing"; st.rerun()
        if c2.button("❌ 彻底清除", key=f"ds_{l['id']}"): st.session_state.leaves.remove(l); st.rerun()
