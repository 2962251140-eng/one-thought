import streamlit as st
from openai import OpenAI
import uuid
import random
from datetime import datetime

# ==========================================
# 1. 页面配置 & 增强型 CSS
# ==========================================
st.set_page_config(page_title="一念", page_icon="🌿", layout="wide")

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
        msg = "行动教练。指出价值并给第一步（50字内）。"
    elif prompt_type == "heavy":
        # 【修改点】明确限制100字以内，并要求分析分数分布
        msg = "犀利PM。根据用户提供的时间、金钱、耗神得分分布，一针见血指出完成该想法最核心的困难点，并给1个破局建议。语气干练，严格控制在100字以内。不要说废话，细节等用户反驳后再补充。"
    elif prompt_type == "heavy_retry":
        # 变通教练可以根据用户的回怼给出稍微多一点的细节
        msg = "变通教练。用户对你的降维建议提出了反驳，请结合反驳理由，给出一个务实的新方案(50-100字内)。"
    elif prompt_type == "complete_and_categorize":
        cat_str = "、".join(st.session_state.categories)
        msg = f"归类。从 [{cat_str}] 选一并鼓励。格式：类别 || 鼓励。"
        
    try:
        res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": msg}, {"role": "user", "content": content}])
        return res.choices[0].message.content
    except Exception as e: return f"AI 休息中...({e})"

# ==========================================
# 3. 侧边栏 (支持云端密钥静默读取)
# ==========================================
with st.sidebar:
    st.header("⚙️ 能量源")
    
    try:
        default_api_key = st.secrets["DEEPSEEK_API_KEY"]
    except:
        default_api_key = ""

    if default_api_key:
        api_key = default_api_key
        api_base = "https://api.deepseek.com/v1"
        st.success("✨ 已连接专属 AI 引擎，直接可用！")
    else:
        # 【修改点】添加 help 提示
        api_key = st.text_input("DeepSeek Key", type="password", help="输入你的模型 API Key 以激活 AI 对话能力。")
        api_base = st.text_input("API Base", value="https://api.deepseek.com/v1", help="默认接口地址，通常不需要修改。")
        
    st.divider()
    st.header("🌿 枝桠管理")
    # 【修改点】添加 help 提示
    new_cat = st.text_input("新增分类：", help="为你的想法创建自定义领域，比如'学习计划'或'旅行'。")
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

if not api_key:
    st.warning("🔑 请先在左侧边栏填入 API Key，激活一念。")
    st.stop()

header_left, header_right = st.columns([1.5, 1])

with header_left:
    st.subheader("🍃 定义灵感")
    # 【修改点】添加 placeholder 引导新用户
    new_idea = st.text_area("捕获瞬间想法...", height=100, key="idea_in", label_visibility="collapsed", placeholder="写下此刻闪现的念头，比如：想做一个记账App...")
    
    c1, c2, c3 = st.columns(3)
    # 【修改点】拆分滑块取值，并添加 help 解释“重力”概念
    t = c1.slider("⏳ 时间", 1, 10, 5, help="1最省时，10最耗时。评估这个想法需要花费的周期。")
    m = c2.slider("💰 金钱", 1, 10, 5, help="1最省钱，10最烧钱。评估这个想法的财务成本。")
    e = c3.slider("🔋 耗神", 1, 10, 5, help="1最轻松，10最内耗。评估执行过程中的心智消耗。")
    t_w = t + m + e
    
    # 【修改点】为按钮添加提示
    if st.button("✨ 凝结初叶", use_container_width=True, help="点击记录。如果三项重力总和大于20，将触发AI对想法完成难度的分析。"):
        if new_idea:
            if t_w >= 21:
                # 【修改点】将分数分布拼接进 content，传给 AI 分析
                prompt_content = f"想法：{new_idea}\n难度得分(满分10)：时间={t}, 金钱={m}, 耗神={e}"
                st.session_state.heavy_advice = chat_with_ai("heavy", prompt_content, api_key, api_base)
                st.session_state.heavy_idea_temp = new_idea; st.rerun()
            else:
                st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": new_idea, "status": "focusing", "ai_prompt": "", "reward_text": "", "weight": t_w, "detail": "", "category": "未分类", "notes": "", "done_time": None})
                st.session_state.heavy_advice = None; st.rerun()

with header_right:
    if st.session_state.heavy_advice:
        st.markdown("<div class='rebuttal-container'>", unsafe_allow_html=True)
        st.info(f"🤖 **AI 重力诊断：**\n{st.session_state.heavy_advice}")
        # 【修改点】引导用户反驳的占位符
        reb = st.text_input("💬 继续交流：", key="reb", placeholder="例如：其实我懂代码，时间成本没那么高...")
        col_reb1, col_reb2 = st.columns(2)
        if col_reb1.button("🔄 重新规划", help="让 AI 根据你的补充理由重新评估"): 
            st.session_state.heavy_advice = chat_with_ai("heavy_retry", f"原想法：{st.session_state.heavy_idea_temp}\n反驳理由：{reb}", api_key, api_base); st.rerun()
        if col_reb2.button("🎯 听取建议", help="接受 AI 的建议，化繁为简"): 
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": f"【降维】{st.session_state.heavy_idea_temp}", "status": "focusing", "ai_prompt": st.session_state.heavy_advice, "reward_text": "", "weight": 5, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        if st.button("🚀 直接生成", use_container_width=True, help="无视 AI 建议，坚持按原想法实现想法"):
            st.session_state.leaves.insert(0, {"id": str(uuid.uuid4()), "content": st.session_state.heavy_idea_temp, "status": "focusing", "ai_prompt": "⚠️重力警告：坚持硬核路线，随时注意内耗度。", "reward_text": "", "weight": t_w, "detail": "", "category": "未分类", "notes": "", "done_time": None})
            st.session_state.heavy_advice = None; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:215px; display:flex; align-items:center; justify-content:center; border:1px dashed #ddd; border-radius:12px; color:#aaa; font-size:12px; text-align:center;'>高难度想法(重力≥21)<br>将在此触发 AI 博弈诊断</div>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. 下方：生命树区域 (左未完成，右已完成)
# ==========================================
left_tree, right_tree = st.columns(2)

with left_tree:
    st.subheader("🌳 呼吸枝桠 (未完成)")
    focus_l = [L for L in st.session_state.leaves if L["status"] == "focusing"]
    if focus_l:
        st.caption("✨ 待激活的灵感 (想想第一步要做什么，然后激活它)")
        for l in focus_l:
            st.markdown(f'<div class="leaf-card leaf-focusing">{l["content"]}</div>', unsafe_allow_html=True)
            # 【修改点】添加 placeholder 引导
            det = st.text_input("第一步计划？", key=f"det_{l['id']}", placeholder="例如：查资料 / 写提纲 / 买工具")
            if st.button("☀️ 激活上树", key=f"act_{l['id']}", help="锁定第一步行动，让灵感正式进入执行期"):
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
                    st.markdown(f'<div class="leaf-card leaf-active"><b>{l["content"]}</b><br><small>👣 {l.get("detail","")}<br>🤖 {l["ai_prompt"]}</small></div>', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([2, 1, 1])
                    if c1.button("✅ 完成", key=f"do_{l['id']}_{i}", use_container_width=True, help="搞定了！点击获取成就鼓励并归档"):
                        res = chat_with_ai("complete_and_categorize", l["content"], api_key, api_base)
                        if "||" in res:
                            p = res.split("||"); l["category"] = p[0].strip(); l["reward_text"] = p[1].strip()
                        else: l["reward_text"] = res; l["category"] = "未分类"
                        l["status"] = "completed"; l["done_time"] = datetime.now(); st.rerun()
                    if c2.button("🍂 搁置", key=f"dr_{l['id']}_{i}", help="现在不想做，先放进暂存土壤里等待时机"): l["status"] = "soil"; st.rerun()
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
        st.caption("🏆 每一个小念头的生根发芽都在这里")
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
                        # 【修改点】添加 placeholder
                        new_note = st.text_area("记录感悟...", value=l["notes"], key=f"nt_{l['id']}_{i}", placeholder="写下做完这件事后的复盘或心情吧...")
                        if st.button("保存感悟", key=f"sv_nt_{l['id']}_{i}"): l["notes"] = new_note; st.rerun()
                        st.divider()
                        new_c = st.selectbox("重选枝桠", ["未分类"] + st.session_state.categories, key=f"mc_c_{l['id']}_{i}")
                        if st.button("保存修改", key=f"sv_c_c_{l['id']}_{i}"): l["category"] = new_c; st.rerun()
                        if st.button("移除成就", key=f"del_c_{l['id']}_{i}"): st.session_state.leaves.remove(l); st.rerun()
    else:
        st.info("右侧枝头静待点亮... 完成你的第一个想法吧！")

st.divider()
with st.expander("🪨 土壤 (暂存区)"):
    s_l = [L for L in st.session_state.leaves if L["status"] == "soil"]
    if not s_l:
        st.write("暂无搁置的想法。")
    for l in s_l:
        st.markdown(f'<div class="leaf-card leaf-soil">{l["content"]}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🌱 复用上树", key=f"rv_{l['id']}", help="时机已到，重新将它变成待办状态"): l["status"] = "focusing"; st.rerun()
        if c2.button("❌ 彻底清除", key=f"ds_{l['id']}", help="断舍离，永久删除"): st.session_state.leaves.remove(l); st.rerun()
