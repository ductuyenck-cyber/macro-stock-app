import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN TRANG ---
st.set_page_config(
    page_title="Hệ thống Vĩ mô & Phân tích Tài chính Cộng Đồng",
    page_icon="📈",
    layout="wide"
)

# --- HÀM ẨN DANH EMAIL (BẢO MẬT HIỂN THỊ CÔNG KHAI) ---
def mask_email(email):
    if not email or "@" not in email:
        return "Ẩn danh"
    parts = email.split("@")
    name = parts[0]
    domain = parts[1]
    if len(name) <= 3:
        masked_name = name[0] + "***"
    else:
        masked_name = name[:2] + "***" + name[-1]
    return f"{masked_name}@{domain}"

# --- HÀM ĐỌC DANH SÁCH THÀNH VIÊN TỪ GOOGLE SHEETS CỦA BẠN ---
@st.cache_data(ttl=30)
def load_members():
    try:
        # Đường dẫn Google Sheet đã được tối ưu hóa sang định dạng CSV để app đọc tự động
        sheet_url = "https://docs.google.com/spreadsheets/d/1K_lTOPWDKqipNWNRSX2IFtm5YF8oILVsfPrluqhhXI4/gviz/tq?tqx=out:csv"
        df = pd.read_csv(sheet_url)
        return df
    except Exception:
        return pd.DataFrame()

# --- KHỞI TẠO KHO LƯU TRỮ TẠM TRONG HỆ THỐNG ---
if 'community_db' not in st.session_state:
    st.session_state['community_db'] = [
        {
            "ID": "tuyen.duc@gmail.com_HPG",
            "Thời gian": "2026-10-15 09:30", 
            "Email Thật (Quản lý nội bộ)": "tuyen.duc@gmail.com", 
            "Mã CK": "HPG", 
            "Nhóm ngành": "Doanh nghiệp Thường", 
            "Kết quả / Đánh giá": "F-Score: 7/9 | M-Score: -2.15 (An toàn)"
        }
    ]

# --- THANH ĐĂNG NHẬP (XÁC THỰC QUA GOOGLE SHEETS) ---
st.sidebar.title("🔐 Đăng nhập hệ thống")
st.sidebar.markdown("*(Thành viên cần đăng ký qua Google Form trước khi đăng nhập)*")
user_email = st.sidebar.text_input("Nhập Gmail chính chủ của bạn:").strip().lower()

df_members = load_members()
is_authenticated = False

if user_email and "@gmail.com" in user_email:
    if not df_members.empty:
        # Tìm xem cột nào chứa email trong file Google Sheets của bạn
        email_col = next((col for col in df_members.columns if 'email' in col.lower()), None)
        if email_col:
            registered_emails = df_members[email_col].dropna().astype(str).str.lower().tolist()
            if user_email in registered_emails:
                is_authenticated = True
            else:
                st.sidebar.error("❌ Email này chưa đăng ký qua Google Form!")
        else:
            # Nếu file chưa có dữ liệu hoặc không tìm thấy cột email, tạm thời cho phép truy cập để test
            is_authenticated = True
    else:
        # Nếu chưa kết nối được file, cho phép chạy thử nghiệm
        is_authenticated = True

if not is_authenticated:
    st.warning("⚠️ Vui lòng nhập Gmail chính chủ đã đăng ký ở thanh bên trái để mở khóa ứng dụng.")
    st.stop()
else:
    st.sidebar.success(f"Xin chào: **{mask_email(user_email)}**")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Chọn phân hệ:", [
        "📊 Phần 1: Dashboard Vĩ Mô", 
        "🔍 Phần 2: Chấm điểm BCTC & Lưu kho", 
        "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)"
    ])

# =====================================================================
# PHẦN 1: DASHBOARD VĨ MÔ & MARKET TIMING
# =====================================================================
if menu == "📊 Phần 1: Dashboard Vĩ Mô":
    st.title("📊 Phần 1: Dashboard Vĩ Mô & Bảng Kiểm Market Timing")
    st.markdown("Nhập các thông số vĩ mô thực tế mới nhất để hệ thống kiểm định dòng tiền.")
    
    with st.expander("⚙️ Tùy chỉnh thông số vĩ mô thực tế", expanded=True):
        c_i1, c_i2, c_i3, c_i4 = st.columns(4)
        with c_i1:
            input_central_rate = st.text_input("Tỷ giá Trung tâm (SBV)", value="24,250 VND")
        with c_i2:
            input_rate_on = st.text_input("Lãi suất ON", value="4.25%")
        with c_i3:
            input_dxy = st.text_input("Chỉ số DXY", value="103.50")
        with c_i4:
            input_liquidity = st.text_input("Thanh khoản HOSE", value="18,500 Tỷ")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Tỷ giá SBV", input_central_rate)
    with col2: st.metric("Lãi suất ON", input_rate_on)
    with col3: st.metric("Chỉ số DXY", input_dxy)
    with col4: st.metric("Thanh khoản", input_liquidity)

    st.markdown("---")
    st.subheader("🚦 BẢNG KIỂM VĨ MÔ SỐNG CÒN (MARKET TIMING) 🚦")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        laisuat = st.selectbox("1. Xu hướng Lãi suất & OMO:", ["Giảm / Nới lỏng (Tốt)", "Đi ngang (Bình thường)", "Tăng / Thắt chặt (Xấu)"])
        tygia = st.selectbox("2. Tỷ giá USD/VND:", ["Ổn định, dưới 25.000 (Tốt)", "Căng thẳng, vượt 25.000 (Xấu)"])
    with col_v2:
        dxy = st.selectbox("3. Chỉ số DXY:", ["Dưới 102 (Tốt)", "Từ 102 đến 105 (Bình thường)", "Vượt 105 (Xấu)"])
        nhnn = st.selectbox("4. Động thái NHNN:", ["Bơm tiền / Mua USD vào (Tốt)", "Không can thiệp (Bình thường)", "Hút Tín phiếu / Bán USD ra (Xấu)"])
        
    if st.button("🔍 ĐÁNH GIÁ THỊ TRƯỜNG", type="primary", use_container_width=True):
        if "Xấu" in laisuat or "Xấu" in tygia or "Vượt 105" in dxy or "Hút Tín phiếu" in nhnn:
            st.error("### 🔴 ĐÈN ĐỎ (Defense / Retreat)\n**Hành động:** PHÒNG THỦ TUYỆT ĐỐI. Giữ tỷ lệ tiền mặt 80-100%.")
        elif "Giảm" in laisuat and "Ổn định" in tygia and "Dưới 102" in dxy and "Bơm tiền" in nhnn:
            st.success("### 🟢 ĐÈN XANH (All-in / Attack)\n**Hành động:** TẤN CÔNG TỔNG LỰC. Full tài khoản, dùng Margin tối đa.")
        else:
            st.warning("### 🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)\n**Hành động:** ĐÁNH DU KÍCH. Tỷ trọng 30-50% tiền mặt, đánh ngắn T+.")

# =====================================================================
# PHẦN 2: CHẤM ĐIỂM BCTC & LƯU KHO
# =====================================================================
elif menu == "🔍 Phần 2: Chấm điểm BCTC & Lưu kho":
    st.title("🔍 Chấm Điểm BCTC Chuẩn Gốc (F-Score & M-Score)")
    st.markdown(f"Thành viên thực hiện phân tích: **{mask_email(user_email)}** (Bảo mật danh tính)")
    
    ticker_symbol = st.text_input("Mã Cổ Phiếu / Doanh Nghiệp (VD: HPG, VNM):", "HPG").upper()
    
    st.markdown("---")
    col_t, col_t1 = st.columns(2)
    
    with col_t:
        st.subheader("🟢 NĂM NAY (Năm t)")
        rev_t = st.number_input("Doanh thu thuần (Sales_t)", value=10000.0)
        rec_t = st.number_input("Phải thu khách hàng (Rec_t)", value=1500.0)
        cogs_t = st.number_input("Giá vốn hàng bán (COGS_t)", value=7000.0)
        ca_t = st.number_input("Tài sản ngắn hạn (CA_t)", value=4000.0)
        ppe_t = st.number_input("TSCĐ hữu hình (Net PP&E_t)", value=5000.0)
        dep_t = st.number_input("Khấu hao (Dep_t)", value=400.0)
        sga_t = st.number_input("Chi phí SG&A", value=1000.0)
        ltd_t = st.number_input("Nợ dài hạn", value=2000.0)
        cl_t = st.number_input("Nợ ngắn hạn", value=3000.0)
        ni_t = st.number_input("Lợi nhuận sau thuế (Net Income)", value=1000.0)
        cfo_t = st.number_input("Dòng tiền HĐKD (CFO)", value=1200.0)
        ta_t = st.number_input("Tổng tài sản", value=12000.0)
        shares_t = st.number_input("Số lượng cổ phiếu", value=1000.0)

    with col_t1:
        st.subheader("🟠 NĂM TRƯỚC (Năm t-1)")
        rev_t1 = st.number_input("Doanh thu thuần (Sales_t-1)", value=9000.0)
        rec_t1 = st.number_input("Phải thu (Rec_t-1)", value=1300.0)
        cogs_t1 = st.number_input("Giá vốn (COGS_t-1)", value=6300.0)
        ca_t1 = st.number_input("Tài sản ngắn hạn (CA_t-1)", value=3800.0)
        ppe_t1 = st.number_input("TSCĐ hữu hình (Net PP&E_t-1)", value=4800.0)
        dep_t1 = st.number_input("Khấu hao (Dep_t-1)", value=380.0)
        sga_t1 = st.number_input("Chi phí SG&A t-1", value=900.0)
        ltd_t1 = st.number_input("Nợ dài hạn t-1", value=2200.0)
        cl_t1 = st.number_input("Nợ ngắn hạn t-1", value=2900.0)
        ni_t1 = st.number_input("Lợi nhuận sau thuế t-1", value=900.0)
        st.markdown("*(CFO t-1 không dùng)*")
        ta_t1 = st.number_input("Tổng tài sản t-1", value=11000.0)
        shares_t1 = st.number_input("Số lượng cổ phiếu t-1", value=1000.0)

    st.markdown("---")
    safe_div = lambda n, d: n / d if d != 0 else 0

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

    roa_t = safe_div(ni_t, (ta_t + ta_t1) / 2)
    roa_t1 = safe_div(ni_t1, ta_t1)
    f_score = sum([
        1 if ni_t > 0 else 0,
        1 if cfo_t > 0 else 0,
        1 if roa_t > roa_t1 else 0,
        1 if cfo_t > ni_t else 0,
        1 if safe_div(ltd_t, ta_t) < safe_div(ltd_t1, ta_t1) else 0,
        1 if safe_div(ca_t, cl_t) > safe_div(ca_t1, cl_t1) else 0,
        1 if shares_t <= shares_t1 else 0,
        1 if (gm_t - gm_t1) > 0 else 0,
        1 if (safe_div(rev_t, ta_t) - safe_div(rev_t1, ta_t1)) > 0 else 0
    ])

    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Beneish M-Score", f"{m_score:.2f}", "Ngưỡng: -1.78")
    col_res2.metric("Piotroski F-Score", f"{f_score} / 9")

    # Lưu bài viết (Tự động cập nhật nếu trùng Email + Mã CK)
    record_id = f"{user_email}_{ticker_symbol}"
    if st.button("💾 Lưu / Cập nhật bài phân tích vào Kho Cộng Đồng", type="primary", use_container_width=True):
        result_text = f"F-Score: {f_score}/9 | M-Score: {m_score:.2f}"
        
        existing_idx = next((i for i, item in enumerate(st.session_state['community_db']) if item['ID'] == record_id), None)
        
        new_record = {
            "ID": record_id,
            "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Email Thật (Quản lý nội bộ)": user_email,
            "Mã CK": ticker_symbol,
            "Nhóm ngành": "Doanh nghiệp Thường",
            "Kết quả / Đánh giá": result_text
        }
        
        if existing_idx is not None:
            st.session_state['community_db'][existing_idx] = new_record
            st.success(f"✅ Đã cập nhật (Sửa) bài phân tích mã **{ticker_symbol}** thành công!")
        else:
            st.session_state['community_db'].insert(0, new_record)
            st.success(f"✅ Đã lưu mới bài phân tích mã **{ticker_symbol}** vào Kho cộng đồng!")

# =====================================================================
# PHẦN 3: KHO DỮ LIỆU CỘNG ĐỒNG (BẢO MẬT ẨN DANH)
# =====================================================================
elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)":
    st.title("📚 Kho Lưu trữ & Tra cứu Kết quả Phân tích Cộng Đồng")
    st.markdown("Nơi lưu giữ toàn bộ báo cáo phân tích tài chính từ các thành viên (Đã tự động bảo mật ẩn danh).")
    
    df_show = pd.DataFrame(st.session_state['community_db'])
    if not df_show.empty:
        df_display = df_show.copy()
        df_display['Thành viên'] = df_display['Email Thật (Quản lý nội bộ)'].apply(mask_email)
        df_final = df_display[['Thời gian', 'Thành viên', 'Mã CK', 'Nhóm ngành', 'Kết quả / Đánh giá']]
        st.dataframe(df_final, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu trong kho.")
        
    st.markdown("---")
    st.subheader("🛠️ Quản lý bài phân tích của riêng bạn")
    
    my_posts = [item for item in st.session_state['community_db'] if item['Email Thật (Quản lý nội bộ)'] == user_email]
    if my_posts:
        st.write(f"Bạn đang sở hữu **{len(my_posts)}** bài phân tích trong kho bảo mật.")
        selected_my_stock = st.selectbox("Chọn mã cổ phiếu bạn muốn chỉnh sửa lại:", [item['Mã CK'] for item in my_posts])
        
        if st.button("✏️ Nạp lại dữ liệu để sửa bài"):
            st.success(f"✅ Đã xác nhận quyền sở hữu mã **{selected_my_stock}**! Hãy chuyển sang **Phần 2: Chấm điểm BCTC** để thay đổi thông số và bấm 'Lưu / Cập nhật' để ghi đè.")
    else:
        st.info("Bạn chưa có bài phân tích nào được lưu trong hệ thống với email này.")
