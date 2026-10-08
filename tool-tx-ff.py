import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Tài Xỉu Pro", page_icon="🎲", layout="wide")
st.title("🎲 Tài Xỉu Analyzer Pro")
st.caption("Cập nhật phiên liên tục • Thống kê nâng cao • Gợi ý đa phương pháp")

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

# ====================== NHẬP LIỆU TRÊN TRANG CHÍNH ======================
st.subheader("➕ Thêm phiên mới")
col_input, col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1, 1])

with col_input:
    new_total = st.number_input("Tổng điểm (3-18)", min_value=3, max_value=18, value=10, step=1, label_visibility="collapsed")

with col_btn1:
    if st.button("Thêm phiên", use_container_width=True, type="primary"):
        st.session_state.history.append(int(new_total))
        st.rerun()

with col_btn2:
    if st.button("Xóa phiên cuối", use_container_width=True):
        if st.session_state.history:
            st.session_state.history.pop()
            st.rerun()

with col_btn3:
    if st.button("Xóa tất cả", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# Nhập hàng loạt
with st.expander("Nhập hàng loạt / Upload CSV / Giả lập"):
    raw = st.text_area("Dán danh sách tổng điểm (cách nhau bởi dấu cách)", height=80)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Cập nhật từ ô nhập"):
            try:
                lst = [int(x) for x in raw.replace("\n", " ").split() if x.strip()]
                lst = [x for x in lst if 3 <= x <= 18]
                st.session_state.history = lst
                st.rerun()
            except:
                st.error("Dữ liệu không hợp lệ")
    with c2:
        file = st.file_uploader("Upload CSV (cột total)", type=["csv"], label_visibility="collapsed")
        if file and st.button("Tải CSV"):
            df = pd.read_csv(file)
            if "total" in df.columns:
                lst = [x for x in df["total"].dropna().astype(int) if 3 <= x <= 18]
                st.session_state.history = lst
                st.rerun()
    with c3:
        n_sim = st.number_input("Số phiên giả lập", 50, 1000, 200)
        if st.button("Tạo giả lập"):
            sums = list(range(3, 19))
            probs = [theo_probs[s] for s in sums]
            st.session_state.history = np.random.choice(sums, size=n_sim, p=probs).tolist()
            st.rerun()

history = st.session_state.history

if not history:
    st.info("Hãy thêm phiên để bắt đầu phân tích")
    st.stop()

n = len(history)
cnt = Counter(history)

# ====================== CHẾ ĐỘ HIỂN THỊ ======================
mode = st.radio("Chế độ hiển thị", ["Đầy đủ (Tổng điểm)", "Chỉ Tài / Xỉu"], horizontal=True)

# ====================== METRICS TỔNG QUAN ======================
xiu_count = sum(1 for x in history if x <= 10)
tai_count = n - xiu_count

m1, m2, m3, m4 = st.columns(4)
m1.metric("Tổng phiên", n)
m2.metric("Xỉu (3-10)", f"{xiu_count} ({xiu_count/n:.1%})")
m3.metric("Tài (11-18)", f"{tai_count} ({tai_count/n:.1%})")
m4.metric("Tổng nhiều nhất", f"{cnt.most_common(1)[0][0]} ({cnt.most_common(1)[0][1]} lần)")

# ====================== CỬA SỔ THỐNG KÊ ======================
st.subheader("📊 Thống kê theo cửa sổ gần đây")
window = st.selectbox("Chọn số phiên gần nhất", [20, 50, 100, "Toàn bộ"], index=0)
if window == "Toàn bộ":
    recent = history
else:
    recent = history[-int(window):]

recent_cnt = Counter(recent)
r_xiu = sum(1 for x in recent if x <= 10)
r_tai = len(recent) - r_xiu

c1, c2, c3 = st.columns(3)
c1.metric(f"Xỉu (gần {len(recent)} phiên)", f"{r_xiu} ({r_xiu/len(recent):.1%})")
c2.metric(f"Tài (gần {len(recent)} phiên)", f"{r_tai} ({r_tai/len(recent):.1%})")
c3.metric("Tổng phổ biến gần đây", f"{recent_cnt.most_common(1)[0][0]}")

# ====================== PHÂN TÍCH CHUỖI ======================
st.subheader("🔗 Phân tích chuỗi (Streak)")

def get_streak(data):
    if not data:
        return None, 0
    cur = data[-1]
    streak = 1
    for i in range(len(data)-2, -1, -1):
        if data[i] == cur:
            streak += 1
        else:
            break
    return cur, streak

cur_total, streak_total = get_streak(history)
tx_history = ["Xỉu" if x <= 10 else "Tài" for x in history]
cur_tx, streak_tx = get_streak(tx_history)

col_s1, col_s2 = st.columns(2)
col_s1.info(f"**Chuỗi tổng điểm:** {cur_total} đang ra liên tiếp **{streak_total}** lần")
col_s2.info(f"**Chuỗi Tài/Xỉu:** {cur_tx} đang ra liên tiếp **{streak_tx}** lần")

# ====================== GỢI Ý ĐA PHƯƠNG PHÁP + CẢNH BÁO ======================
st.subheader("🎯 Gợi ý thống kê phiên tiếp theo")

df_dist = pd.DataFrame({
    "Tổng": list(range(3, 19)),
    "Số lần": [cnt.get(i, 0) for i in range(3, 19)],
    "Thực nghiệm": [cnt.get(i, 0)/n for i in range(3, 19)],
    "Lý thuyết": [theo_probs[i] for i in range(3, 19)]
})
df_dist["Chênh lệch"] = df_dist["Thực nghiệm"] - df_dist["Lý thuyết"]

under = df_dist.nsmallest(3, "Chênh lệch")["Tổng"].tolist()
over = df_dist.nlargest(3, "Chênh lệch")["Tổng"].tolist()

# ---- CẢNH BÁO CHUỖI CAO ----
cur_total, streak_total = get_streak(history)
tx_history = ["Xỉu" if x <= 10 else "Tài" for x in history]
cur_tx, streak_tx = get_streak(tx_history)

# Kiểm tra cặp giống nhau liên tiếp (ví dụ 9-9, 10-10...)
same_pair = False
if n >= 2 and history[-1] == history[-2]:
    same_pair = True

# Hiển thị cảnh báo mạnh
if streak_total >= 3 or same_pair:
    st.error(f"⚠️ CẢNH BÁO CHUỖI CAO: Tổng **{cur_total}** đang ra liên tiếp **{streak_total}** lần")
    if same_pair:
        st.error(f"⚠️ Vừa xuất hiện cặp giống nhau **{history[-2]}-{history[-1]}** → Thống kê thường dễ bị bẻ ở nhịp tiếp theo")
    st.error("→ Khả năng đảo chiều ở phiên tới **cao hơn bình thường** (chỉ mang tính tham khảo)")

if streak_tx >= 3:
    opposite = "Tài" if cur_tx == "Xỉu" else "Xỉu"
    st.warning(f"Chuỗi **{cur_tx}** đã kéo dài {streak_tx} lần → Gợi ý nghiêng về **{opposite}**")

# Các gợi ý khác
goi_y = []
goi_y.append(f"**Mean-reversion:** Các tổng đang thấp hơn lý thuyết nhiều nhất → {under}")
goi_y.append(f"**Đang cao hơn lý thuyết:** {over}")

if r_xiu > r_tai + 3:
    goi_y.append("**Cửa sổ gần:** Xỉu đang chiếm ưu thế → gợi ý nghiêng Tài")
elif r_tai > r_xiu + 3:
    goi_y.append("**Cửa sổ gần:** Tài đang chiếm ưu thế → gợi ý nghiêng Xỉu")

for g in goi_y:
    st.markdown(f"• {g}")

st.info("Tất cả chỉ là gợi ý thống kê dựa trên dữ liệu quá khứ. Không có độ chính xác đảm bảo.")
# ====================== XÁC SUẤT CÓ ĐIỀU KIỆN ======================
st.subheader("📉 Xác suất có điều kiện (sau tổng hiện tại)")

if n >= 5:
    prev = history[-1]
    next_after = []
    for i in range(len(history)-1):
        if history[i] == prev:
            next_after.append(history[i+1])
    if next_after:
        next_cnt = Counter(next_after)
        st.write(f"Sau khi ra **{prev}**, các tổng tiếp theo từng xuất hiện:")
        st.write(dict(next_cnt.most_common(5)))
    else:
        st.write("Chưa đủ dữ liệu để tính xác suất có điều kiện.")
else:
    st.write("Cần ít nhất 5 phiên để tính.")

# ====================== BỘ BA (TRIPLE) ======================
st.subheader("🎲 Thống kê bộ ba (ước lượng)")
triple_like = sum(1 for x in history if x in [3, 18])  # chắc chắn triple
st.write(f"Số lần tổng 3 hoặc 18 (chắc chắn bộ ba): **{triple_like}** lần")
st.caption("Lưu ý: Chỉ tổng 3 và 18 là chắc chắn triple. Các tổng khác không thể biết chính xác từ tổng điểm.")

# ====================== BIỂU ĐỒ XU HƯỚNG ======================
st.subheader("📈 Xu hướng gần đây")
trend_len = st.slider("Số phiên hiển thị trên biểu đồ", 20, min(100, n), 30)
trend_data = history[-trend_len:]
fig_trend = px.line(
    x=list(range(1, len(trend_data)+1)),
    y=trend_data,
    markers=True,
    labels={"x": "Phiên", "y": "Tổng điểm"},
    title=f"Xu hướng {len(trend_data)} phiên gần nhất"
)
fig_trend.add_hline(y=10.5, line_dash="dash", line_color="gray")
st.plotly_chart(fig_trend, use_container_width=True)

# ====================== BIỂU ĐỒ PHÂN BỐ ======================
if mode == "Đầy đủ (Tổng điểm)":
    st.subheader("📊 Phân bố tổng điểm")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_dist["Tổng"], y=df_dist["Thực nghiệm"], name="Thực nghiệm", marker_color="#3b82f6"))
    fig.add_trace(go.Scatter(x=df_dist["Tổng"], y=df_dist["Lý thuyết"], name="Lý thuyết", mode="lines+markers", line=dict(color="red", width=2)))
    fig.update_layout(height=380, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        df_dist.style.format({"Thực nghiệm": "{:.2%}", "Lý thuyết": "{:.2%}", "Chênh lệch": "{:+.2%}"}),
        use_container_width=True,
        height=400
    )

# ====================== DANH SÁCH LỊCH SỬ ======================
st.subheader("📋 Lịch sử các phiên")
st.write(" → ".join(map(str, history[-50:])) + (" ..." if n > 50 else ""))
st.caption(f"Hiển thị tối đa 50 phiên gần nhất (tổng cộng {n} phiên)")
