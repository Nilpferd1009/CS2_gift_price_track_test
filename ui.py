import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
from datetime import datetime
from alerts import check_price_alert, buy_price_map, sell_price_map
from matplotlib import font_manager
import seaborn as sns

st.set_page_config(page_title="CS2 多饰品价格监控", layout="wide")

data_file = os.path.join("data", "all_items.csv")
st.title("💎 CS2 多饰品价格监控")
df_all = pd.read_csv(data_file, encoding='utf-8-sig')

# 拉取按钮
if st.button("📥 拉取最新价格数据"):
    os.system("python fetch_logged_trend_data.py")

if os.path.exists(data_file):
    df_all["日期"] = pd.to_datetime(df_all["日期"])
    df_all.sort_values("日期", inplace=True)

    # 用户选择饰品
    skin_options = df_all["饰品名称"].unique()
    selected_skin = st.selectbox("🎯 选择饰品", skin_options)

    df = df_all[df_all["饰品名称"] == selected_skin].copy()

    # ===== 折线图 =====
    st.subheader("📈 价格趋势图")
    fig = px.line(
        df,
        x="日期",
        y="均价",
        markers=True,
        title=f"{selected_skin} 价格趋势图",
        labels={"日期": "交易日期", "均价": "均价（元）"},
        template="plotly_white"
    )

    # 标注最高最低点（可选）
    max_point = df.loc[df["均价"].idxmax()]
    min_point = df.loc[df["均价"].idxmin()]

    fig.add_scatter(x=[max_point["日期"]], y=[max_point["均价"]],
                    mode='markers+text',
                    marker=dict(color='red', size=10),
                    text=[f"最高 {max_point['均价']:.2f}"],
                    textposition='top center',
                    name="最高点")

    fig.add_scatter(x=[min_point["日期"]], y=[min_point["均价"]],
                    mode='markers+text',
                    marker=dict(color='green', size=10),
                    text=[f"最低 {min_point['均价']:.2f}"],
                    textposition='bottom center',
                    name="最低点")

    # 设置 hover 数据格式
    fig.update_traces(
        hovertemplate="<b>日期:</b> %{x|%Y-%m-%d}<br><b>均价:</b> %{y:.2f} 元<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ===== 最新价格 =====
    st.subheader("📌 最新价格")
    st.write(f"📅 日期：{df['日期'].iloc[-1].strftime('%Y-%m-%d')} | 💰 均价：{df['均价'].iloc[-1]:.2f} 元")

    # ===== 📧 邮件提醒 =====
    st.subheader("📧 邮件提醒")

    # 获取当前饰品ID
    # 中文名 → ID 的反向映射
    item_id_map = {
        "原皮骷髅匕首(★ StatTrak™)": "776879",
        "原皮骷髅匕首": "775988",
        "原皮蝴蝶刀": "42530",
        "原皮蝴蝶刀(★ StatTrak™)": "43389",
        "原皮 M9 刺刀": "43052",
        "原皮 M9 刺刀(★ StatTrak™)": "43774",
    }
    selected_id = item_id_map.get(selected_skin)
    buy_price = buy_price_map.get(selected_id)
    sell_price = sell_price_map.get(selected_id)

    if buy_price is None or sell_price is None:
        st.warning("⚠ 当前饰品未设置买入/卖出提醒阈值，已跳过提醒。")
    else:
        st.markdown(f"""
            当前饰品提醒配置：
            - 💰 买入提醒阈值：`{buy_price:.2f}` 元
            - 💸 卖出提醒阈值：`{sell_price:.2f}` 元
        """)

        if st.button("📩 检查是否需要提醒"):
            # 保存临时数据文件
            temp_file = f"temp_alert_{datetime.now().timestamp()}.csv"
            df[["日期", "均价"]].to_csv(temp_file, index=False, encoding="utf-8-sig")

            # 调用提醒逻辑
            ok, msg = check_price_alert(temp_file, buy_price, sell_price, selected_skin)
            os.remove(temp_file)

            if ok:
                st.success(msg)
            else:
                st.info(msg)

# ===== 🎯 当前饰品价格分析区域 =====
st.markdown("---")
st.header("📊 当前饰品价格分布分析")

# 👉 创建两个并排区域
col1, col2, col3 = st.columns(3)

# ===== 🎁 Boxplot 分布图显示在左边 =====
with col1:
    st.subheader("📉 价格分布 Boxplot")

    font_path = "fonts/NotoSansCJKsc-Regular.otf"
    font_prop = font_manager.FontProperties(fname=font_path)
    # plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False

    fig_box, ax_box = plt.subplots(figsize=(6, 5.3))
    sns.boxplot(data=df_all[df_all["饰品名称"] == selected_skin], x="饰品名称", y="均价", ax=ax_box)
    ax_box.set_title(f"{selected_skin} 价格分布", fontproperties=font_prop)
    ax_box.set_xlabel("饰品名称", fontproperties=font_prop)
    ax_box.set_ylabel("价格（元）", fontproperties=font_prop)
    st.pyplot(fig_box)

# ===== 📋 统计信息表格显示在右边 =====
with col2:
    st.subheader("📑 统计信息")

    stats = df_all.groupby("饰品名称")["均价"].agg(
        count="count",
        mean="mean",
        std="std",
        min="min",
        q1=lambda x: x.quantile(0.25),
        median="median",
        q3=lambda x: x.quantile(0.75),
        max="max",
        mode=lambda x: x.mode().iloc[0] if not x.mode().empty else None
    ).reset_index()

    selected_stats = stats[stats["饰品名称"] == selected_skin]

    # 中文列名映射
    column_rename = {
        "count": "数据量",
        "mean": "均值",
        "std": "标准差",
        "min": "最小值",
        "q1": "四分位数 Q1",
        "median": "中位数",
        "q3": "四分位数 Q3",
        "max": "最大值",
        "mode": "众数"
    }

    # 设置表格格式：转置+中文列名+保留两位小数
    st.table(
        selected_stats
        .set_index("饰品名称")
        .T
        .rename(index=column_rename)
        .style
        .format("{:.2f}"),
    )


with col3:
    st.subheader("📄 历史价格表")

    # 过滤当前饰品数据，并处理日期格式
    table_data = df_all[df_all["饰品名称"] == selected_skin].copy()
    table_data["日期"] = pd.to_datetime(table_data["日期"]).dt.strftime("%Y-%m-%d")

    # 只保留两列
    table_data = table_data[["日期", "均价"]]

    # 高亮最大最小值
    highlight_js = JsCode(f"""
    function(params) {{
        if (params.data['均价'] == {table_data['均价'].max()}) {{
            return {{'color': 'white', 'backgroundColor': '#ff4d4f'}}
        }}
        if (params.data['均价'] == {table_data['均价'].min()}) {{
            return {{'color': 'white', 'backgroundColor': '#52c41a'}}
        }}
    }}
    """)

    # 构建 AgGrid 表格
    gb = GridOptionsBuilder.from_dataframe(table_data)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(groupable=False, editable=False, filter=True)
    gb.configure_grid_options(getRowStyle=highlight_js)
    gb.configure_side_bar()
    grid_options = gb.build()

    # 渲染表格
    AgGrid(
        table_data,
        gridOptions=grid_options,
        height=330,
        allow_unsafe_jscode=True
    )
# ===== 运行 Streamlit 应用 =====
# streamlit run ui.py
