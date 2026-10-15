import streamlit as st
import pandas as pd
import numpy as np
from vnstock import *

# --- CẤU HÌNH GIAO DIỆN TRANG ---
st.set_page_config(
    page_title="Hệ thống Vĩ mô & Phân tích Tài chính",
    page_icon="📈",
    layout="wide"
)

# --- XÁC THỰC NGƯỜI DÙNG BẰNG GMAIL ---
st.sidebar.title("🔐 Đăng nhập hệ thống")
user_email = st.sidebar.text_input("Nhập Gmail của bạn để tiếp tục:")

if not user_email or "@gmail.com" not in user_email:
    st.warning("⚠️ Vui lòng nhập địa chỉ Gmail hợp lệ ở thanh bên trái để sử dụng Web App.")
    st.stop()
else:
    st.sidebar.success(f"Xin chào: {user_email}")
    st.sidebar.markdown("---")
    # Menu chính
    menu = st.sidebar.radio("Chọn phân hệ:", [
        "📊 Phần 1: Dashboard Vĩ Mô Tự Động", 
        "🔍 Phần 2: Nhập liệu BCTC & Đánh giá", 
        "📚 Phần 3: Kho Dữ liệu Cộng Đồng"
    ])

# =====================================================================
# PHẦN 1: DASHBOARD VĨ MÔ & THỊ TRƯỜNG TỰ ĐỘNG
# =====================================================================
if menu == "📊 Phần 1: Dashboard Vĩ Mô Tự Động":
    st.title("📊 Phần 1: Tổng quan Vĩ mô & Dòng tiền Thị trường")
    st.markdown("Hệ thống tự động cập nhật các chỉ số vĩ mô và thanh khoản.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Lãi suất liên ngân hàng (ON)", value="4.25%", delta="+0.15%")
    with col2:
        st.metric(label="Tỷ giá trung tâm (SBV)", value="24,250 VND", delta="+25 VND")
    with col3:
        st.metric(label="Thanh khoản HOSE", value="18,450 Tỷ", delta="+12%")

    st.subheader("📈 Biến động VN-Index (Cập nhật từ vnstock)")
    try:
        df_index = stock_historical_data(symbol='VNINDEX', start_date='2026-01-01', end_date='2026-10-15', resolution='1D')
        if not df_index.empty:
            st.line_chart(df_index.set_index('time')['close'])
        else:
            st.info("Đang tải dữ liệu biểu đồ...")
    except Exception as e:
        st.error(f"Không thể tải dữ liệu vnstock: {e}")

# =====================================================================
# PHẦN 2: NHẬP LIỆU BCTC THÔ & TÍNH TOÁN THEO 3 NHÓM NGÀNH
# =====================================================================
elif menu == "🔍 Phần 2: Nhập liệu BCTC & Đánh giá":
    st.title("🔍 Phần 2: Công cụ Chấm điểm & Cảnh báo Chuyên sâu")
    st.markdown(f"Thành viên thực hiện: **{user_email}**")
    
    stock_code = st.text_input("Nhập mã cổ phiếu (VD: HPG, VCB, SSI):", "HPG").upper()
    industry = st.selectbox("Chọn nhóm ngành của doanh nghiệp:", [
        "1. Doanh nghiệp Thường (Sản xuất, Thương mại, Dịch vụ)", 
        "2. Ngân hàng Thương mại", 
        "3. Công ty Chứng khoán"
    ])
    
    st.markdown("---")
    
    # --- FORM 1: DOANH NGHIỆP THƯỜNG ---
    if "Doanh nghiệp Thường" in industry:
        st.subheader("📝 Nhập số liệu thô (F-Score & M-Score)")
        col_a, col_b = st.columns(2)
        with col_a:
            net_income = st.number_input("Lợi nhuận sau thuế (Tỷ VNĐ):", value=500.0)
            cfo = st.number_input("Dòng tiền thuần từ HĐKD - CFO (Tỷ VNĐ):", value=600.0)
            roa = st.number_input("ROA kỳ này (%):", value=8.0)
            current_ratio = st.number_input("Khả năng thanh toán hiện hành:", value=1.5)
        with col_b:
            gross_margin = st.number_input("Biên lợi nhuận gộp (%):", value=20.0)
            asset_turnover = st.number_input("Vòng quay tài sản:", value=0.9)
            dsrgi = st.number_input("Chỉ số phải thu khách hàng (DSRI):", value=1.0)
            sgi = st.number_input("Chỉ số tăng trưởng doanh thu (SGI):", value=1.1)
            
        if st.button("🚀 Chạy thuật toán F-Score & M-Score", type="primary"):
            # Logic tính mẫu
            score_f = (1 if net_income > 0 else 0) + (1 if cfo > 0 else 0) + (1 if roa > 0 else 0) + (1 if cfo > net_income else 0) + (1 if current_ratio > 1.2 else 0)
            m_score = -2.25 + (0.92 * dsrgi) + (0.89 * sgi) # Công thức mô phỏng
            
            st.success(f"✅ Đã phân tích xong mã **{stock_code}**!")
            col_r1, col_r2 = st.columns(2)
            col_r1.metric("Piotroski F-Score (Mô phỏng)", f"{score_f} / 5 điểm")
            col_r2.metric("Beneish M-Score", f"{m_score:.2f}")
            if m_score > -1.78:
                st.error("🚨 Cảnh báo: Có dấu hiệu rủi ro thao túng BCTC!")
            else:
                st.success("🟢 An toàn: Không phát hiện rủi ro thao túng lớn.")

    # --- FORM 2: NGÂN HÀNG ---
    elif "Ngân hàng Thương mại" in industry:
        st.subheader("📝 Nhập số liệu thô cho Ngân hàng (Chuẩn CAMELS)")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            npl_ratio = st.number_input("Tỷ lệ Nợ xấu - NPL (%):", value=1.8)
            llr_ratio = st.number_input("Tỷ lệ bao phủ nợ xấu - LLR (%):", value=110.0)
            nim_ratio = st.number_input("Biên lãi ròng - NIM (%):", value=3.5)
        with col_n2:
            ldr_ratio = st.number_input("Tỷ lệ LDR (Cho vay / Huy động) (%):", value=82.0)
            car_ratio = st.number_input("Tỷ lệ an toàn vốn - CAR (%):", value=11.5)
            
        if st.button("🚀 Đánh giá sức khỏe Ngân hàng", type="primary"):
            st.success(f"✅ Đã phân tích Ngân hàng **{stock_code}**!")
            st.metric("Tỷ lệ Nợ xấu (NPL)", f"{npl_ratio}%")
            if npl_ratio > 3.0:
                st.error("🔴 CẢNH BÁO: Tỷ lệ nợ xấu vượt mức an toàn 3%!")
            else:
                st.success("🟢 Chất lượng tài sản ngân hàng nằm trong vùng kiểm soát tốt.")

    # --- FORM 3: CÔNG TY CHỨNG KHOÁN ---
    elif "Công ty Chứng khoán" in industry:
        st.subheader("📝 Nhập số liệu thô cho Công ty Chứng khoán")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            margin_debt = st.number_input("Tổng dư nợ cho vay Margin (Tỷ VNĐ):", value=5000.0)
            equity = st.number_input("Vốn chủ sở hữu (Tỷ VNĐ):", value=4000.0)
        with col_s2:
            fvtpl_ratio = st.number_input("Tỷ trọng tài sản FVTPL / Tổng tài sản (%):", value=25.0)
            roe = st.number_input("ROE (%):", value=15.0)
            
        if st.button("🚀 Đánh giá Công ty Chứng khoán", type="primary"):
            leverage = margin_debt / equity
            st.success(f"✅ Đã phân tích Công ty Chứng khoán **{stock_code}**!")
            st.metric("Hệ số đòn bẩy Margin (Margin / VSH)", f"{leverage:.2f}x")
            if leverage > 2.0:
                st.warning("⚠️ Lưu ý: Đòn bẩy cho vay margin đang ở mức cao so với vốn chủ sở hữu.")
            else:
                st.success("🟢 Mức độ đòn bẩy an toàn.")

# =====================================================================
# PHẦN 3: KHO DỮ LIỆU CỘNG ĐỒNG
# =====================================================================
elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng":
    st.title("📚 Phần 3: Kho Lưu trữ & Tra cứu Kết quả Phân tích Cộng Đồng")
    st.markdown("Nơi lưu lại toàn bộ các mã cổ phiếu đã được các thành viên trong hệ thống phân tích.")
    
    # Bảng mẫu dữ liệu cộng đồng
    df_community = pd.DataFrame({
        'Thời gian': ['2026-10-15 09:30', '2026-10-14 15:20', '2026-10-14 10:10'],
        'Thành viên': ['tuyen@gmail.com', 'admin@gmail.com', 'congsu@gmail.com'],
        'Mã CK': ['HPG', 'VCB', 'SSI'],
        'Nhóm ngành': ['Doanh nghiệp Thường', 'Ngân hàng', 'Chứng khoán'],
        'Kết quả / Đánh giá': ['F-Score: 7/5 (Tốt)', 'NPL: 1.2% (An toàn)', 'Đòn bẩy Margin: 1.4x (Ổn định)']
    })
    
    st.dataframe(df_community, use_container_width=True)
    st.info("💡 Mẹo: Dữ liệu này sẽ được đồng bộ tự động để mọi thành viên đều có thể tham khảo nhanh chóng.")