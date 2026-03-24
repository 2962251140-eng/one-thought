import streamlit as st
from openai import OpenAI
import uuid
import random
from datetime import datetime

# ==========================================
# 1. 页面配置 & 增强型 CSS
# ==========================================
st.set_page_config(page_title="一念 | 左右平衡版", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .main-title { text-align: center; color: #2E8B57; font-family: 'Georgia', serif; margin-bottom: 0px;}
    .sub-title { text-align: center; color: #666; font-size: 14px; margin-bottom: 30px;}
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
    if prompt_type == "init":
        msg = "行动教练。指出价值并给第一步（30字内）。"
    elif prompt_type == "heavy":
        msg = "犀利PM。指风险并给MVP方案(50字内)。"
    elif prompt_type == "heavy_retry":
        msg = "变通教练。根据反驳给新方案(50字内)。"
    elif prompt_type == "complete_and_categorize":
        cat_str = "、".join(st.session_state.categories)
        msg = f"归类。从 [{cat_str}] 选一并鼓励。格式：类别 || 鼓励。"
    try:
        res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": msg}, {"role": "user", "content": content}])
        return res.choices[0].message.content
    except Exception as e: return f"AI 休息中...({e})"

# ==========================================
# 3. 侧边栏
# ==========================================
with st.sidebar:
    st.header("⚙️ 能量源")
    api_key = st.text_input("DeepSeek Key", type="password")
    api_base = st.text_input("API Base", value="https://api.deepseek.com/v1")
    st.divider()
    st.header("🌿 枝桠管理")
    new_cat = st.text_input("新增分类：")
    if st.button("➕ 添加") and new_cat:
        if new_cat not in st.session_state.categories: st.session_state.categories.append(new_cat); st.rerun()
    for idx, cat in enumerate(st.session_state.categories):
        with st.expander(f"📍 {cat}"):
            new_n = st.text_input("改名", value=cat, key=f"ren_{idx}")
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
# 4. 顶部：灵感捕获与 AI 对线区
# ==========================================
st.markdown("<h1 class='main-title'>🌿 一 念</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>化瞬间灵感，为生命之树</p>", unsafe_allow_html=True)

# 校验 API Key
if not api_key:
    st.warning("🔑 请先在左侧边栏填入 API Key，否则无法唤醒 AI 教练。")
    st.stop()

header_left, header_right = st.columns([1.5, 1])

with header_left:
    st.subheader("🍃 定义灵感")
    new_idea = st.text_area("捕获瞬间想法...", height=100, key="idea_in", label_visibility="collapsed")
    c1, c2, c3 = st.columns(3)
    t_w = c1.slider("⏳ 时间", 1, 10, 5) + c2.slider("💰 金钱", 1, 10, 5) + c3.slider("🔋 耗神", 1, 10, 5)
    if st.button("✨ 凝结初叶", use_container_width=True):
        if new_idea:
            if t_w >= 21:
                st.session_state.heavy_advice = chat_with_ai("heavy", new_idea, api_key, api_base)
                st.session_state.heavy_idea_temp = new_idea; st.rerun()
            else:
                st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": new_idea, "status": "focusing", "ai_prompt": "", "reward_text": "", "weight": t_w, "detail": "", "category": "未分类", "notes": "", "done_time": None})
                st.session_state.heavy_advice = None; st.rerun()

with header_right:
    if st.session_state.heavy_advice:
        st.markdown("<div class='rebuttal-container'>", unsafe_allow_html=True)
        st.info(f"🤖 **AI 对线建议：**\n{st.session_state.heavy_advice}")
        reb = st.text_input("💬 不服？回怼理由：", key="reb")
        col_reb1, col_reb2 = st.columns(2)
        if col_reb1.button("🔄 重新规划"): st.session_state.heavy_advice = chat_with_ai("heavy_retry", f"{st.session_state.heavy_idea_temp}\n{reb}", api_key, api_base); st.rerun()
        if col_reb2.button("🎯 听劝采纳"): 
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": f"【降维】{st.session_state.heavy_idea_temp}", "status": "focusing", "ai_prompt": st.session_state.heavy_advice, "reward_text": "", "weight": 5, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        if st.button("🚀 头铁强行生成", use_container_width=True):
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": st.session_state.heavy_idea_temp, "status": "focusing", "ai_prompt": "⚠️重力警告", "reward_text": "", "weight": t_w, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:215px; display:flex; align-items:center; justify-content:center; border:1px dashed #ddd; border-radius:12px; color:#aaa; font-size:12px;'>等待重力检测 (AI博弈区)</div>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. 下方：生命树区域 (左未完成，右已完成)
# ==========================================
left_tree, right_tree = st.columns(2)

with left_tree:
    st.subheader("🌳 呼吸枝桠 (未完成)")
    focus_l = [L for L in st.session_state.leaves if L["status"] == "focusing"]
    if focus_l:
        st.caption("✨ 待激活的灵感")
        for l in focus_l:
            st.markdown(f'<div class="leaf-card leaf-focusing">{l["content"]}</div>', unsafe_allow_html=True)
            det = st.text_input("第一步计划？", key=f"det_{l['id']}")
            if st.button("☀️ 激活上树", key=f"act_{l['id']}"):
                if det:
                    l["ai_prompt"] = chat_with_ai("init", f"{l['content']}\n{det}", api_key, api_base)
                    l["detail"] = det; l["status"] = "active"; st.rerun()
    
    active_l = [L for L in st.session_state.leaves if L["status"] == "active"]
    if active_l:
        st.caption("🍃 进行中的枝头")
        cat_tabs_left = st.tabs(["🌐 全景"] + st.session_state.categories + ["📦 未分类"])
        for i, tab_n in enumerate(["🌐 全景"] + st.session_state.categories + ["📦 未分类"]):
            with cat_tabs_left[i]:
                cur_tab_leaves = active_l if i==0 else [L for L in active_l if L.get("category") == tab_n.replace("📦 ","")]
                for l in cur_tab_leaves:
                    # 使用 tab_n 保证 key 唯一
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
                            if st.button("确认修改", key=f"sv_mc_{l['id']}_{i}"): l["category"] = nc; st.rerun()
                            if st.button("彻底删除", key=f"dl_a_{l['id']}_{i}"): st.session_state.leaves.remove(l); st.rerun()

with right_tree:
    st.subheader("🌟 璀璨之林 (成就归档)")
    comp_l = [L for L in st.session_state.leaves if L["status"] == "completed"]
    comp_l.sort(key=lambda x: x["done_time"] if x["done_time"] else datetime.min)
    
    if comp_l:
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
                    
                    with st.popover("📝 感悟 / ⚙️ 管理", key=f"pop_c_{l['id']}_{i}", use_container_width=True):
                        # 核心修复点：key 加入了 i (tab 索引)，解决 Duplicate Key 报错
                        new_note = st.text_area("记录感悟...", value=l["notes"], key=f"nt_{l['id']}_{i}")
                        if st.button("保存感悟", key=f"sv_nt_{l['id']}_{i}"): l["notes"] = new_note; st.rerun()
                        st.divider()
                        new_c = st.selectbox("重选枝桠", ["未分类"] + st.session_state.categories, key=f"mc_c_{l['id']}_{i}")
                        if st.button("保存修改", key=f"sv_c_c_{l['id']}_{i}"): l["category"] = new_c; st.rerun()
                        if st.button("移除成就", key=f"del_c_{l['id']}_{i}"): st.session_state.leaves.remove(l); st.rerun()
    else:
        st.info("右侧枝头静待点亮...")

st.divider()
with st.expander("🪨 土壤 (暂存区)"):
    s_l = [L for L in st.session_state.leaves if L["status"] == "soil"]
    for l in s_l:
        st.markdown(f'<div class="leaf-card leaf-soil">{l["content"]}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🌱 复用上树", key=f"rv_{l['id']}"): l["status"] = "focusing"; st.rerun()
        if c2.button("❌ 彻底清除", key=f"ds_{l['id']}"): st.session_state.leaves.remove(l); st.rerun()
