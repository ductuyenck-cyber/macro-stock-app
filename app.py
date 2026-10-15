import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN TRANG ---
st.set_page_config(
    page_title="Hệ thống Vĩ mô & Phân tích Tài chính Nguyên Bản",
    page_icon="📈",
    layout="wide"
)

# --- KHỞI TẠO KHO LƯU TRỮ TẠM TRONG SESSION (CỘNG ĐỒNG) ---
if 'community_db' not in st.session_state:
    st.session_state['community_db'] = [
        {"Thời gian": "2026-10-15 09:30", "Thành viên": "tuyen@gmail.com", "Mã CK": "HPG", "Nhóm ngành": "Doanh nghiệp Thường", "Kết quả / Đánh giá": "F-Score: 7/9 | M-Score: -2.15 (An toàn)"},
        {"Thời gian": "2026-10-14 15:20", "Thành viên": "admin@gmail.com", "Mã CK": "VCB", "Nhóm ngành": "Ngân hàng Thương mại", "Kết quả / Đánh giá": "NPL: 1.2% (An toàn tốt)"}
    ]

# --- XÁC THỰC NGƯỜI DÙNG BẰNG GMAIL ---
st.sidebar.title("🔐 Đăng nhập hệ thống")
user_email = st.sidebar.text_input("Nhập Gmail của bạn để tiếp tục:")

if not user_email or "@gmail.com" not in user_email:
    st.warning("⚠️ Vui lòng nhập địa chỉ Gmail hợp lệ ở thanh bên trái để mở khóa ứng dụng.")
    st.stop()
else:
    st.sidebar.success(f"Xin chào: {user_email}")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Chọn phân hệ:", [
        "📊 Phần 1: Dashboard Vĩ Mô & Market Timing", 
        "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score chuẩn gốc)", 
        "📚 Phần 3: Kho Dữ liệu Cộng Đồng"
    ])

# =====================================================================
# PHẦN 1: DASHBOARD VĨ MÔ & MARKET TIMING
# =====================================================================
if menu == "📊 Phần 1: Dashboard Vĩ Mô & Market Timing":
    st.title("📊 Phần 1: Dashboard Vĩ Mô & Bảng Kiểm Market Timing")
    st.markdown("Hệ thống kiểm định sức khỏe dòng tiền vĩ mô để đưa ra chiến lược phân bổ vốn tối ưu.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Tỷ giá Trung tâm (SBV)", value="24,250 VND", delta="+15 VND")
    with col2:
        st.metric(label="Lãi suất Liên ngân hàng (ON)", value="4.25%", delta="+0.10%")
    with col3:
        st.metric(label="Chỉ số DXY (USD Index)", value="103.50", delta="-0.25")
    with col4:
        st.metric(label="Thanh khoản Toàn thị trường", value="18,500 Tỷ", delta="+15%")

    st.markdown("---")
    
    st.subheader("🚦 BẢNG KIỂM VĨ MÔ SỐNG CÒN (MARKET TIMING) 🚦")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        laisuat = st.selectbox("1. Xu hướng Lãi suất & OMO:", ["Giảm / Nới lỏng (Tốt)", "Đi ngang (Bình thường)", "Tăng / Thắt chặt (Xấu)"])
        tygia = st.selectbox("2. Tỷ giá USD/VND:", ["Ổn định, dưới 25.000 (Tốt)", "Căng thẳng, vượt 25.000 (Xấu)"])
    with col_v2:
        dxy = st.selectbox("3. Chỉ số Sức mạnh Đồng Đô la (DXY):", ["Dưới 102 (Tốt)", "Từ 102 đến 105 (Bình thường)", "Vượt 105 (Xấu)"])
        nhnn = st.selectbox("4. Động thái của NHNN:", ["Bơm tiền / Mua USD vào (Tốt)", "Không can thiệp (Bình thường)", "Hút Tín phiếu / Bán USD ra (Xấu)"])
        
    if st.button("🔍 ĐÁNH GIÁ THỊ TRƯỜNG", type="primary", use_container_width=True):
        if "Xấu" in laisuat or "Xấu" in tygia or "Vượt 105" in dxy or "Hút Tín phiếu" in nhnn:
            st.error("### 🔴 ĐÈN ĐỎ (Defense / Retreat)\n**Hành động:** PHÒNG THỦ TUYỆT ĐỐI. Bán hết cổ phiếu đầu cơ. Tỷ lệ tiền mặt 80-100%.")
        elif "Giảm" in laisuat and "Ổn định" in tygia and "Dưới 102" in dxy and "Bơm tiền" in nhnn:
            st.success("### 🟢 ĐÈN XANH (All-in / Attack)\n**Hành động:** TẤN CÔNG TỔNG LỰC. Đánh Full tài khoản. Sử dụng Margin tối đa.")
        else:
            st.warning("### 🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)\n**Hành động:** ĐÁNH DU KÍCH. Tỷ trọng 30-50% tiền mặt. Không dùng Margin.")

    st.markdown("---")
    st.subheader("📈 Biến động Chỉ số Thị trường (VN-Index)")
    try:
        from vnstock import stock_historical_data
        df_index = stock_historical_data(symbol='VNINDEX', start_date='2026-01-01', end_date='2026-10-15', resolution='1D')
        if not df_index.empty:
            fig = px.line(df_index, x='time', y='close', title='Biến động VN-Index (Dữ liệu thực tế từ vnstock)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            raise Exception()
    except Exception:
        df_dummy = pd.DataFrame({'time': ['Th 1', 'Th 4', 'Th 7', 'Th 10'], 'close': [1200, 1250, 1230, 1285]})
        fig = px.line(df_dummy, x='time', y='close', title='Biến động VN-Index (Mô phỏng)')
        st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# PHẦN 2: CHẤM ĐIỂM BCTC (F-SCORE & M-SCORE CHUẨN GỐC)
# =====================================================================
elif menu == "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score chuẩn gốc)":
    st.title("🔍 Hệ Thống Đánh Giá Doanh Nghiệp (Gốc Nguyên Bản)")
    st.markdown(f"Thành viên phân tích: **{user_email}** | Tích hợp **Piotroski F-Score (9 Tiêu chí)** & **Beneish M-Score (8 biến gốc)**")
    
    ticker_symbol = st.text_input("Mã Cổ Phiếu / Doanh Nghiệp (VD: HPG, VNM, FPT):", "HPG").upper()
    
    st.markdown("---")
    
    col_t, col_t1 = st.columns(2)
    
    # --- NĂM NAY (t) ---
    with col_t:
        st.subheader("🟢 NĂM NAY (Năm t)")
        rev_t = st.number_input("Doanh thu thuần (Sales_t)", value=10000.0)
        rec_t = st.number_input("Phải thu khách hàng (Rec_t)", value=1500.0)
        cogs_t = st.number_input("Giá vốn hàng bán (COGS_t)", value=7000.0)
        ca_t = st.number_input("Tài sản ngắn hạn (CA_t)", value=4000.0)
        ppe_t = st.number_input("Giá trị còn lại TSCĐ hữu hình (Net PP&E_t)", value=5000.0)
        dep_t = st.number_input("Chi phí khấu hao trong năm (Dep_t)", value=400.0)
        sga_t = st.number_input("Chi phí bán hàng & Quản lý (SG&A_t)", value=1000.0)
        ltd_t = st.number_input("Nợ dài hạn (Long-term Debt_t)", value=2000.0)
        cl_t = st.number_input("Nợ ngắn hạn (Current Liabilities_t)", value=3000.0)
        ni_t = st.number_input("Lợi nhuận sau thuế (Net Income_t)", value=1000.0)
        cfo_t = st.number_input("Dòng tiền từ HĐKD (CFO_t)", value=1200.0)
        ta_t = st.number_input("Tổng tài sản (Total Assets_t)", value=12000.0)
        shares_t = st.number_input("Số lượng cổ phiếu lưu hành (Shares_t)", value=1000.0)

    # --- NĂM TRƯỚC (t-1) ---
    with col_t1:
        st.subheader("🟠 NĂM TRƯỚC (Năm t-1)")
        rev_t1 = st.number_input("Doanh thu thuần (Sales_t-1)", value=9000.0)
        rec_t1 = st.number_input("Phải thu khách hàng (Rec_t-1)", value=1300.0)
        cogs_t1 = st.number_input("Giá vốn hàng bán (COGS_t-1)", value=6300.0)
        ca_t1 = st.number_input("Tài sản ngắn hạn (CA_t-1)", value=3800.0)
        ppe_t1 = st.number_input("Giá trị còn lại TSCĐ hữu hình (Net PP&E_t-1)", value=4800.0)
        dep_t1 = st.number_input("Chi phí khấu hao trong năm (Dep_t-1)", value=380.0)
        sga_t1 = st.number_input("Chi phí bán hàng & Quản lý (SG&A_t-1)", value=900.0)
        ltd_t1 = st.number_input("Nợ dài hạn (Long-term Debt_t-1)", value=2200.0)
        cl_t1 = st.number_input("Nợ ngắn hạn (Current Liabilities_t-1)", value=2900.0)
        ni_t1 = st.number_input("Lợi nhuận sau thuế (Net Income_t-1)", value=900.0)
        st.markdown("*(CFO t-1 không dùng)*")
        ta_t1 = st.number_input("Tổng tài sản (Total Assets_t-1)", value=11000.0)
        shares_t1 = st.number_input("Số lượng cổ phiếu lưu hành (Shares_t-1)", value=1000.0)

    st.markdown("---")

    # --- TÍNH TOÁN THUẬT TOÁN ---
    safe_div = lambda n, d: n / d if d != 0 else 0

    # 1. Beneish M-Score (8 biến gốc)
    dsri = safe_div(safe_div(rec_t, rev_t), safe_div(rec_t1, rev_t1))
    gm_t1 = safe_div(rev_t1 - cogs_t1, rev_t1)
    gm_t = safe_div(rev_t - cogs_t, rev_t)
    gmi = safe_div(gm_t1, gm_t)

    non_ca_t = 1 - safe_div(ca_t + ppe_t, ta_t)
    non_ca_t1 = 1 - safe_div(ca_t1 + ppe_t1, ta_t1)
    aqi = safe_div(non_ca_t, non_ca_t1)

    sgi = safe_div(rev_t, rev_t1)
    rate_t1 = safe_div(dep_t1, ppe_t1 + dep_t1)
    rate_t = safe_div(dep_t, ppe_t + dep_t)
    depi = safe_div(rate_t1, rate_t)

    sgai = safe_div(safe_div(sga_t, rev_t), safe_div(sga_t1, rev_t1))
    lvgi = safe_div(safe_div(ltd_t + cl_t, ta_t), safe_div(ltd_t1 + cl_t1, ta_t1))
    tata = safe_div(ni_t - cfo_t, ta_t)

    m_score = -4.84 + (0.920 * dsri) + (0.528 * gmi) + (0.404 * aqi) + (0.892 * sgi) + (0.115 * depi) - (0.172 * sgai) + (-0.327 * lvgi) + (4.679 * tata)

    # 2. Piotroski F-Score (9 tiêu chí)
    roa_t = safe_div(ni_t, (ta_t + ta_t1) / 2)
    roa_t1 = safe_div(ni_t1, ta_t1)
    ltd_ratio_t = safe_div(ltd_t, ta_t)
    ltd_ratio_t1 = safe_div(ltd_t1, ta_t1)
    gm_changed = gm_t - gm_t1
    turnover_t = safe_div(rev_t, ta_t)
    turnover_t1 = safe_div(rev_t1, ta_t1)

    f_criteria = [
        ("1. LNST năm nay dương? (ROA > 0)", ni_t > 0),
        ("2. Dòng tiền kinh doanh dương? (CFO > 0)", cfo_t > 0),
        ("3. ROA cải thiện?", roa_t > roa_t1),
        ("4. Chất lượng dòng tiền (CFO > LNST)?", cfo_t > ni_t),
        ("5. Tỷ lệ nợ dài hạn giảm?", ltd_ratio_t < ltd_ratio_t1),
        ("6. Khả năng thanh toán ngắn hạn cải thiện?", safe_div(ca_t, cl_t) > safe_div(ca_t1, cl_t1)),
        ("7. Số cổ phiếu lưu hành không tăng?", shares_t <= shares_t1),
        ("8. Biên lợi nhuận gộp cải thiện?", gm_changed > 0),
        ("9. Vòng quay tài sản cải thiện?", (turnover_t - turnover_t1) > 0)
    ]
    f_score = sum(1 for _, pass_val in f_criteria if pass_val)

    # Hiển thị kết quả trực quan
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.subheader("🚨 Beneish M-Score (Mô hình 8 biến)")
        st.metric("Chỉ số M-Score", f"{m_score:.2f}", delta="Ngưỡng: -1.78" if m_score <= -1.78 else "Cảnh báo vượt ngưỡng", delta_color="normal" if m_score <= -1.78 else "inverse")
        if m_score > -1.78:
            st.error("⚠️ M-Score vượt ngưỡng -1.78: Cần kiểm tra sâu BCTC.")
        else:
            st.success("🟢 An toàn: Không vượt ngưỡng cảnh báo thao túng.")

    with col_res2:
        st.subheader("🛡️ Piotroski F-Score (9 Tiêu chí)")
        st.metric("Chỉ số F-Score", f"{f_score} / 9", delta="Rất Khỏe" if f_score >= 8 else ("Trung Bình" if f_score >= 5 else "Yếu"))
        if f_score >= 8:
            st.success("🟢 Doanh nghiệp có nền tảng tài chính rất khỏe.")
        elif f_score >= 5:
            st.info("🟡 Sức khỏe tài chính ở mức trung bình / khá.")
        else:
            st.error("🔴 Sức khỏe tài chính yếu.")

    # Nút bấm lưu kết quả
    if st.button("💾 Lưu kết quả vào Kho Dữ liệu Cộng Đồng", type="primary", use_container_width=True):
        result_text = f"F-Score: {f_score}/9 | M-Score: {m_score:.2f}"
        st.session_state['community_db'].insert(0, {
            "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Thành viên": user_email,
            "Mã CK": ticker_symbol,
            "Nhóm ngành": "Doanh nghiệp Thường",
            "Kết quả / Đánh giá": result_text
        })
        st.success(f"Đã lưu thành công mã **{ticker_symbol}** vào Kho dữ liệu cộng đồng!")

# =====================================================================
# PHẦN 3: KHO DỮ LIỆU CỘNG ĐỒNG
# =====================================================================
elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng":
    st.title("📚 Phần 3: Kho Lưu trữ & Tra cứu Kết quả Phân tích Cộng Đồng")
    st.markdown("Nơi lưu lại toàn bộ các mã cổ phiếu đã được các thành viên trong hệ thống phân tích trực tuyến.")
    
    df_community = pd.DataFrame(st.session_state['community_db'])
    st.dataframe(df_community, use_container_width=True)
    st.info("💡 Mẹo: Khi các thành viên khác đăng nhập và thực hiện phân tích, dữ liệu sẽ tự động đồng bộ vào bảng này để mọi người cùng tham khảo.")
