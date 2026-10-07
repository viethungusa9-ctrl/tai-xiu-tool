import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Tài Xỉu - Tổng điểm 3-18",
    page_icon="🎲",
    layout="wide"
)

st.title("🎲 Tài Xỉu Analyzer – Tổng điểm (3–18)")
st.caption("Phiên bản nhẹ – Không dùng LSTM – Chạy tốt trên Android (Termux)")

# ====================== XÁC SUẤT LÝ THUYẾT ======================
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

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📥 Nhập dữ liệu")
    input_method = st.radio(
        "Cách nhập:",
        ["Nhập tay (tổng điểm)", "Upload CSV", "Dữ liệu giả lập"]
    )

    history = []

    if input_method == "Nhập tay (tổng điểm)":
        raw = st.text_area(
            "Nhập các tổng điểm (3-18), cách nhau bởi dấu cách hoặc xuống dòng:",
            value="10 12 8 14 9 11 7 13 10 15 6 12 9 11 8 14 10 13 7 12 11 9 16 8 10",
            height=150
        )
        try:
            history = [int(x.strip()) for x in raw.replace("\n", " ").split() if x.strip()]
            history = [x for x in history if 3 <= x <= 18]
        except:
            st.error("Chỉ được nhập số nguyên từ 3 đến 18")
            history = []

    elif input_method == "Upload CSV":
        file = st.file_uploader("Upload file CSV (cột tên 'total')", type=["csv"])
        if file is not None:
            try:
                df = pd.read_csv(file)
                if "total" in df.columns:
                    history = df["total"].dropna().astype(int).tolist()
                    history = [x for x in history if 3 <= x <= 18]
                else:
                    st.error("File phải có cột tên 'total'")
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")

    else:
        n = st.slider("Số phiên giả lập", 50, 1000, 200)
        sums = list(range(3, 19))
        probs = [theo_probs[s] for s in sums]
        history = np.random.choice(sums, size=n, p=probs).tolist()
        st.success(f"Đã tạo {n} phiên theo đúng xác suất lý thuyết")

# ====================== PHÂN TÍCH ======================
if not history:
    st.info("👈 Hãy nhập dữ liệu ở sidebar bên trái để bắt đầu")
    st.stop()

n = len(history)
cnt = Counter(history)

# Tạo bảng phân bố
df_dist = pd.DataFrame({
    "Tổng": list(range(3, 19)),
    "Số lần": [cnt.get(i, 0) for i in range(3, 19)],
    "Xác suất thực nghiệm": [cnt.get(i, 0) / n for i in range(3, 19)],
    "Xác suất lý thuyết": [theo_probs[i] for i in range(3, 19)],
    "Số cách lý thuyết": [theo_ways[i] for i in range(3, 19)]
})
df_dist["Chênh lệch"] = df_dist["Xác suất thực nghiệm"] - df_dist["Xác suất lý thuyết"]

# Tài / Xỉu
xiu_count = sum(cnt.get(i, 0) for i in range(3, 11))
tai_count = sum(cnt.get(i, 0) for i in range(11, 19))

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số phiên", n)
col2.metric("Xỉu (3-10)", f"{xiu_count} ({xiu_count/n:.1%})")
col3.metric("Tài (11-18)", f"{tai_count} ({tai_count/n:.1%})")
most_common = cnt.most_common(1)[0]
col4.metric("Tổng xuất hiện nhiều nhất", f"{most_common[0]} ({most_common[1]} lần)")

st.divider()

# ====================== BIỂU ĐỒ ======================
st.subheader("📊 Phân bố tổng điểm (Thực nghiệm vs Lý thuyết)")

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
    line=dict(color="#ef4444", width=3),
    marker=dict(size=8)
))
fig.update_layout(
    xaxis_title="Tổng điểm",
    yaxis_title="Xác suất",
    height=420,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(t=40, b=40)
)
st.plotly_chart(fig, use_container_width=True)

# ====================== BẢNG CHI TIẾT ======================
st.subheader("📋 Bảng thống kê chi tiết")

st.dataframe(
    df_dist.style.format({
        "Xác suất thực nghiệm": "{:.2%}",
        "Xác suất lý thuyết": "{:.2%}",
        "Chênh lệch": "{:+.2%}"
    }).background_gradient(subset=["Chênh lệch"], cmap="RdYlGn_r"),
    use_container_width=True,
    height=500
)

# ====================== CHUỖI & THÔNG TIN THÊM ======================
st.subheader("📈 Thông tin thêm")

current = history[-1]
streak = 1
for i in range(n - 2, -1, -1):
    if history[i] == current:
        streak += 1
    else:
        break

col_a, col_b = st.columns(2)
with col_a:
    st.write(f"**Chuỗi hiện tại:** Tổng **{current}** đang ra liên tiếp **{streak}** lần")
with col_b:
    recent_10 = history[-10:] if n >= 10 else history
    recent_cnt = Counter(recent_10)
    st.write(f"**10 phiên gần nhất:** {dict(recent_cnt)}")

st.divider()
st.markdown("""
**Ghi chú:**
- Cột **Chênh lệch** dương = tổng đó đang ra nhiều hơn lý thuyết.
- Cột **Chênh lệch** âm = tổng đó đang ra ít hơn lý thuyết.
- Tool này chỉ mang tính thống kê, không có khả năng dự đoán chính xác tương lai.
""")
