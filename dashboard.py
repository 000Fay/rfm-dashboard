import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── 页面基础配置 ──────────────────────────────────
st.set_page_config(
    page_title="电商用户RFM分析仪表盘",
    page_icon="📊",
    layout="wide"
)

# ── 读取数据 ──────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('output/rfm_segments.csv', dtype={'CustomerID': str})
    return df

rfm = load_data()

# ── 颜色配置 ──────────────────────────────────────
color_map = {
    '重要价值客户': '#2E86AB',
    '重要唤回客户': '#E76F51',
    '潜力客户':    '#A8DADC',
    '需关注客户':  '#F4A261',
    '其他客户':    '#8ECAE6',
    '流失客户':    '#CCCCCC',
}

# ══════════════════════════════════════════════════
# 顶部标题
# ══════════════════════════════════════════════════
st.title("📊 电商用户RFM分析仪表盘")
st.caption("数据来源：UCI Online Retail Dataset | 分析周期：2010.12 – 2011.12")
st.divider()

# ══════════════════════════════════════════════════
# 第一行：核心指标卡片
# ══════════════════════════════════════════════════
col1, col2, col3, col4 = st.columns(4)

total_users    = len(rfm)
total_revenue  = rfm['Monetary'].sum()
avg_monetary   = rfm['Monetary'].mean()
vip_ratio      = len(rfm[rfm['Segment'] == '重要价值客户']) / total_users * 100

with col1:
    st.metric(label="👥 总用户数",    value=f"{total_users:,} 人")
with col2:
    st.metric(label="💰 总销售额",    value=f"£{total_revenue:,.0f}")
with col3:
    st.metric(label="🛒 人均消费",    value=f"£{avg_monetary:,.0f}")
with col4:
    st.metric(label="⭐ 高价值用户占比", value=f"{vip_ratio:.1f}%")

st.divider()

# ══════════════════════════════════════════════════
# 第二行：两列图表
# ══════════════════════════════════════════════════
col_left, col_right = st.columns(2)

# ── 左：客户层级用户数量条形图 ──
with col_left:
    st.subheader("各层级用户数量")
    seg_count = rfm['Segment'].value_counts().reset_index()
    seg_count.columns = ['层级', '用户数']
    seg_count['占比%'] = (seg_count['用户数'] / total_users * 100).round(1)

    fig_bar = px.bar(
        seg_count,
        x='用户数', y='层级',
        orientation='h',
        color='层级',
        color_discrete_map=color_map,
        text=seg_count.apply(lambda r: f"{r['用户数']}人 ({r['占比%']}%)", axis=1),
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        showlegend=False,
        xaxis_title="用户数",
        yaxis_title="",
        height=350,
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── 右：销售额贡献饼图 ──
with col_right:
    st.subheader("各层级销售额贡献")
    seg_revenue = rfm.groupby('Segment')['Monetary'].sum().reset_index()
    seg_revenue.columns = ['层级', '总销售额']

    fig_pie = px.pie(
        seg_revenue,
        names='层级',
        values='总销售额',
        color='层级',
        color_discrete_map=color_map,
        hole=0.4,
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(
        showlegend=True,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════
# 第三行：气泡散点图
# ══════════════════════════════════════════════════
st.subheader("用户分布气泡图（R vs F，气泡大小 = 消费金额）")

fig_scatter = px.scatter(
    rfm,
    x='Recency', y='Frequency',
    size='Monetary',
    color='Segment',
    color_discrete_map=color_map,
    hover_data={'CustomerID': True, 'Monetary': ':,.0f', 'Recency': True, 'Frequency': True},
    labels={
        'Recency': '距上次购买天数（越小越活跃）',
        'Frequency': '购买频次',
        'Segment': '客户层级'
    },
    size_max=40,
    opacity=0.6,
)
fig_scatter.update_layout(
    height=420,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════
# 第四行：交互筛选 + 用户明细表
# ══════════════════════════════════════════════════
st.subheader("用户明细数据")

col_filter1, col_filter2 = st.columns([1, 3])
with col_filter1:
    seg_options = ['全部'] + sorted(rfm['Segment'].unique().tolist())
    selected_seg = st.selectbox("筛选客户层级", seg_options)

filtered = rfm if selected_seg == '全部' else rfm[rfm['Segment'] == selected_seg]

with col_filter2:
    st.caption(f"当前显示：{len(filtered)} 名用户")

display_cols = {
    'CustomerID': '用户ID',
    'Recency':    '距上次购买(天)',
    'Frequency':  '购买次数',
    'Monetary':   '消费金额(£)',
    'R_score':    'R得分',
    'F_score':    'F得分',
    'M_score':    'M得分',
    'RFM_Score':  'RFM编码',
    'Segment':    '客户层级',
}

display_df = filtered[list(display_cols.keys())].rename(columns=display_cols)
display_df['消费金额(£)'] = display_df['消费金额(£)'].round(2)

st.dataframe(
    display_df.sort_values('消费金额(£)', ascending=False),
    use_container_width=True,
    height=350,
)

# ══════════════════════════════════════════════════
# 底部：核心结论
# ══════════════════════════════════════════════════
st.divider()
st.subheader("📌 核心分析结论")

c1, c2, c3 = st.columns(3)
with c1:
    st.info("**二八定律验证**\n\n重要价值客户仅占 **26.3%**，却贡献了 **66.5%** 的销售额")
with c2:
    st.warning("**流失风险**\n\n流失客户占比 **24.6%**，平均 **218天** 未产生购买行为")
with c3:
    st.success("**转化机会**\n\n**319名**潜力客户近期活跃，复购率低，是最具转化价值的群体")