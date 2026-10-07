import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import plotly.graph_objects as go

st.set_page_config(
    page_title="Tài Xỉu - Tổng điểm 3-18",
    page_icon="🎲",
    layout="wide"
)

st.title("🎲 Tài Xỉu Analyzer – Tổng điểm (3–18)")
st.caption("Hỗ trợ cập nhật phiên liên tục + Gợi ý thống kê")

@st.cache_data
def theoretical_distribution():
    ways = {i: 0 for i in range(3, 19)}
    for a in range(1, 7):
        for b in range(1, 7):
            for c in range(1, 7):
                ways[a + b + c] += 1
    total = 216
    probs = {k: v / total for k, v in ways.items()}
    return ways, probs

theo_ways, theo_probs = theoretical_distribution()

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("📥 Nhập dữ liệu")

    st.subheader("Thêm phiên mới")
    new_total = st.number_input(
        "Tổng điểm phiên mới (3-18):",
        min_value=3,
        max_value=18,
        value=10,
        step=1
    )
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("➕ Thêm phiên", use_container_width=True):
            st.session_state.history.append(int(new_total))
            st.rerun()
    with col_clear:
        if st.button("🗑️ Xóa hết", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.divider()
    st.subheader("Hoặc nhập hàng loạt")
    input_method = st.radio("Cách nhập:", ["Nhập tay", "Upload CSV", "Dữ liệu giả lập"])

    if input_method == "Nhập tay":
        raw = st.text_area("Nhập các tổng điểm (3-18):", height=100)
        if st.button("Cập nhật từ ô nhập tay"):
            try:
                new_list = [int(x.strip()) for x in raw.replace("\n", " ").split() if x.strip()]
                new_list = [x for x in new_list if 3 <= x <= 18]
                st.session_state.history = new_list
                st.rerun()
            except:
                st.error("Chỉ nhập số từ 3 đến 18")

    elif input_method == "Upload CSV":
        file = st.file_uploader("Upload CSV (cột total)", type=["csv"])
        if file and st.button("Tải từ CSV"):
            try:
                df = pd.read_csv(file)
                if "total" in df.columns:
                    new_list = [x for x in df["total"].dropna().astype(int).tolist() if 3 <= x <= 18]
                    st.session_state.history = new_list
                    st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")

    else:
        n = st.slider("Số phiên giả lập", 50, 1000, 200)
        if st.button("Tạo dữ liệu giả lập"):
            sums = list(range(3, 19))
            probs = [theo_probs[s] for s in sums]
            st.session_state.history = np.random.choice(sums, size=n, p=probs).tolist()
            st.rerun()

history = st.session_state.history

if not history:
    st.info("👈 Hãy thêm phiên mới ở sidebar để bắt đầu")
    st.stop()

n = len(history)
cnt = Counter(history)

df_dist = pd.DataFrame({
    "Tổng": list(range(3, 19)),
    "Số lần": [cnt.get(i, 0) for i in range(3, 19)],
    "Xác suất thực nghiệm": [cnt.get(i, 0) / n for i in range(3, 19)],
    "Xác suất lý thuyết": [theo_probs[i] for i in range(3, 19)],
    "Số cách lý thuyết": [theo_ways[i] for i in range(3, 19)]
})
df_dist["Chênh lệch"] = df_dist["Xác suất thực nghiệm"] - df_dist["Xác suất lý thuyết"]

xiu_count = sum(cnt.get(i, 0) for i in range(3, 11))
tai_count = sum(cnt.get(i, 0) for i in range(11, 19))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số phiên", n)
col2.metric("Xỉu (3-10)", f"{xiu_count} ({xiu_count/n:.1%})")
col3.metric("Tài (11-18)", f"{tai_count} ({tai_count/n:.1%})")
most_common = cnt.most_common(1)[0]
col4.metric("Tổng nhiều nhất", f"{most_common[0]} ({most_common[1]} lần)")

st.divider()

# ====================== GỢI Ý THỐNG KÊ ======================
st.subheader("🎯 Gợi ý thống kê phiên tiếp theo")

# Tìm các tổng đang ra ít hơn lý thuyết nhiều nhất
df_dist["Độ lệch"] = df_dist["Chênh lệch"]
under = df_dist.nsmallest(3, "Độ lệch")["Tổng"].tolist()

# Chuỗi hiện tại
current = history[-1]
streak = 1
for i in range(n-2, -1, -1):
    if history[i] == current:
        streak += 1
    else:
        break

# Gợi ý đơn giản
goi_y = []
goi_y.append(f"Các tổng đang ra **ít hơn lý thuyết** nhiều nhất: {under}")
if streak >= 3:
    goi_y.append(f"Chuỗi **{current}** đang dài ({streak} lần) → thống kê thường hay đảo chiều")
else:
    goi_y.append(f"Chuỗi **{current}** còn ngắn ({streak} lần)")

# Tài / Xỉu
if xiu_count > tai_count:
    goi_y.append("Xỉu đang nhiều hơn Tài → gợi ý nghiêng về **Tài**")
else:
    goi_y.append("Tài đang nhiều hơn Xỉu → gợi ý nghiêng về **Xỉu**")

for g in goi_y:
    st.write("• " + g)

st.warning("⚠️ Đây chỉ là gợi ý dựa trên thống kê quá khứ. Tài Xỉu là ngẫu nhiên, không có quy luật để đoán chính xác.")

st.divider()

st.subheader("📊 Phân bố tổng điểm")

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df_dist["Tổng"],
    y=df_dist["Xác suất thực nghiệm"],
    name="Thực nghiệm",
    marker_color="#3b82f6"
))
fig.add_trace(go.Scatter(
    x=df_dist["Tổng"],
    y=df_dist["Xác suất lý thuyết"],
    name="Lý thuyết",
    mode="lines+markers",
    line=dict(color="#ef4444", width=3)
))
fig.update_layout(height=400, margin=dict(t=30, b=30))
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Bảng thống kê")

st.dataframe(
    df_dist[["Tổng", "Số lần", "Xác suất thực nghiệm", "Xác suất lý thuyết", "Chênh lệch"]].style.format({
        "Xác suất thực nghiệm": "{:.2%}",
        "Xác suất lý thuyết": "{:.2%}",
        "Chênh lệch": "{:+.2%}"
    }),
    use_container_width=True,
    height=450
)

st.subheader("📈 Thông tin thêm")
col_a, col_b = st.columns(2)
with col_a:
    st.write(f"**Chuỗi hiện tại:** {current} × {streak}")
with col_b:
    recent_10 = history[-10:] if n >= 10 else history
    st.write(f"**10 phiên gần nhất:** {dict(Counter(recent_10))}")
