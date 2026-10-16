import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- CẤU HÌNH GIAO DIỆN & TỐI ƯU HÓA MOBILE (RESPONSIVE) ---
st.set_page_config(
    page_title="Hệ thống Vĩ mô & Tài chính Cộng Đồng",
    page_icon="📈",
    layout="wide"
)

# Chèn CSS tùy chỉnh để giao diện đẹp, hiện đại và thân thiện với điện thoại
st.markdown("""
    <style>
    /* Tổng thể font chữ và màu nền nhẹ nhàng */
    .main {
        background-color: #fdfdfd;
    }
    /* Bo tròn và làm nổi bật các nút bấm (rất tốt cho thao tác chạm trên mobile) */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        height: 3em;
        width: 100%;
        background-color: #0056b3;
        color: white;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #004494;
        color: white;
    }
    /* Tùy chỉnh các tiêu đề phụ */
    h3, h2 {
        color: #1e293b;
    }
    /* Tối ưu khung chứa (Cards) cho gọn gàng */
    .card {
        padding: 20px;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- NHÚNG GOOGLE FORM TRÊN THANH BÊN (ĐĂNG KÝ NHANH) ---
st.sidebar.markdown("---")
with st.sidebar.expander("📝 Chưa có tài khoản? Đăng ký ngay"):
    st.markdown("Điền form bên dưới để cấp quyền:")
    form_embed_url = "https://docs.google.com/forms/d/e/1FAIpQLSeGyXK_-dnAq4IjHsKaJjKp9O89ziolpuQyvr7sXWCL7fELoA/viewform?embedded=true"
    components.iframe(form_embed_url, height=380, scrolling=True)

# --- HÀM ẨN DANH EMAIL (BẢO MẬT CÔNG KHAI) ---
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

# --- HÀM ĐỌC DANH SÁCH THÀNH VIÊN TỪ GOOGLE SHEETS ---
@st.cache_data(ttl=30)
def load_members():
    try:
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
            "Loại": "Phân tích BCTC",
            "Mã CK / Nội dung": "HPG", 
            "Nhóm ngành": "Doanh nghiệp Thường", 
            "Kết quả / Đánh giá": "F-Score: 7/9 | M-Score: -2.15 (An toàn)"
        },
        {
            "ID": "tuyen.duc@gmail.com_MACRO",
            "Thời gian": "2026-10-15 10:00", 
            "Email Thật (Quản lý nội bộ)": "tuyen.duc@gmail.com", 
            "Loại": "Nhận định Vĩ mô",
            "Mã CK / Nội dung": "VĨ MÔ TOÀN CẢNH", 
            "Nhóm ngành": "Market Timing", 
            "Kết quả / Đánh giá": "🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)"
        }
    ]

# --- THANH ĐĂNG NHẬP (XÁC THỰC QUA GOOGLE SHEETS) ---
st.sidebar.markdown("---")
st.sidebar.title("🔐 Xác thực Thành viên")
user_email = st.sidebar.text_input("Nhập Gmail chính chủ:").strip().lower()

df_members = load_members()
is_authenticated = False

if user_email and "@gmail.com" in user_email:
    if not df_members.empty:
        email_col = next((col for col in df_members.columns if 'email' in col.lower()), None)
        if email_col:
            registered_emails = df_members[email_col].dropna().astype(str).str.lower().tolist()
            if user_email in registered_emails:
                is_authenticated = True
            else:
                st.sidebar.error("❌ Email này chưa đăng ký qua Google Form!")
        else:
            is_authenticated = True
    else:
        is_authenticated = True

if not is_authenticated:
    st.warning("📱 **Chào mừng bạn!** Vui lòng nhập Gmail chính chủ đã đăng ký ở menu bên trái (hoặc bấm vào mũi tên `>` góc trên bên trái trên điện thoại) để mở khóa ứng dụng.")
    st.stop()
else:
    st.sidebar.success(f"Xin chào: **{mask_email(user_email)}**")
    st.sidebar.markdown("---")
    menu = st.sidebar.selectbox("📂 Chọn phân hệ chức năng:", [
        "📊 Phần 1: Dashboard Vĩ Mô & Market Timing", 
        "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score)", 
        "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)"
    ])

# =====================================================================
# PHẦN 1: DASHBOARD VĨ MÔ & MARKET TIMING
# =====================================================================
if menu == "📊 Phần 1: Dashboard Vĩ Mô & Market Timing":
    st.title("📊 Bảng Kiểm Vĩ Mô & Market Timing")
    st.markdown("Đánh giá chu kỳ dòng tiền vĩ mô thực tế để đưa ra quyết định hành động chiến lược.")
    
    with st.container(border=True):
        st.subheader("📋 Lựa chọn trạng thái vĩ mô hiện tại")
        laisuat = st.selectbox("1. Xu hướng Lãi suất & OMO:", ["-- Chọn trạng thái --", "Giảm / Nới lỏng (Tốt)", "Đi ngang (Bình thường)", "Tăng / Thắt chặt (Xấu)"])
        tygia = st.selectbox("2. Biến động Tỷ giá USD/VND (So với biên độ NHNN):", ["-- Chọn trạng thái --", "Trượt giá chậm, trong biên độ kiểm soát (Tốt)", "Tăng sốc, áp sát trần biên độ / Chợ đen biến động mạnh (Xấu)"])
        dxy = st.selectbox("3. Chỉ số Sức mạnh Đồng Đô la (DXY):", ["-- Chọn trạng thái --", "Xu hướng giảm / Dưới trung bình dài hạn (Tốt)", "Đi ngang / Vùng trung tính (Bình thường)", "Bứt phá vượt kháng cự mạnh / Đỉnh dài hạn (Xấu)"])
        nhnn = st.selectbox("4. Động thái của NHNN:", ["-- Chọn trạng thái --", "Bơm tiền / Mua lại ngoại tệ tăng dự trữ (Tốt)", "Không can thiệp (Bình thường)", "Hút Tín phiếu / Bán ngoại tệ can thiệp mạnh (Xấu)"])
        
    if st.button("🔍 ĐÁNH GIÁ THỊ TRƯỜNG NGAY"):
        if "-- Chọn trạng thái --" in [laisuat, tygia, dxy, nhnn]:
            st.warning("⚠️ Vui lòng chọn đầy đủ 4 thông số vĩ mô trước khi đánh giá!")
        else:
            if "Xấu" in laisuat or "Xấu" in tygia or "Xấu" in dxy or "Hút Tín phiếu" in nhnn:
                st.session_state['macro_result'] = "🔴 ĐÈN ĐỎ (Defense / Retreat)"
                st.error(f"### {st.session_state['macro_result']}\n**Cảnh báo rủi ro vĩ mô!**\n\n**Hành động:** PHÒNG THỦ TUYỆT ĐỐI. Bán cổ phiếu đầu cơ. Tỷ lệ tiền mặt 80-100%. Không bắt đáy.")
            elif "Giảm" in laisuat and "Trượt giá chậm" in tygia and "Xu hướng giảm" in dxy and "Bơm tiền" in nhnn:
                st.session_state['macro_result'] = "🟢 ĐÈN XANH (All-in / Attack)"
                st.success(f"### {st.session_state['macro_result']}\n**Vĩ mô ủng hộ tuyệt đối!**\n\n**Hành động:** TẤN CÔNG TỔNG LỰC. Tận dụng tối đa chu kỳ nới lỏng tiền tệ.")
            else:
                st.session_state['macro_result'] = "🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)"
                st.warning(f"### {st.session_state['macro_result']}\n**Vĩ mô hỗn hợp, biến động biên độ.**\n\n**Hành động:** ĐÁNH DU KÍCH. Tỷ trọng linh hoạt, đánh ngắn T+.")

    if 'macro_result' in st.session_state:
        st.markdown("---")
        if st.button("💾 Lưu kết quả vĩ mô vào Kho Cộng Đồng"):
            macro_record_id = f"{user_email}_MACRO"
            existing_macro_idx = next((i for i, item in enumerate(st.session_state['community_db']) if item['ID'] == macro_record_id), None)
            
            macro_record = {
                "ID": macro_record_id,
                "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Email Thật (Quản lý nội bộ)": user_email,
                "Loại": "Nhận định Vĩ mô",
                "Mã CK / Nội dung": "VĨ MÔ TOÀN CẢNH", 
                "Nhóm ngành": "Market Timing", 
                "Kết quả / Đánh giá": st.session_state['macro_result']
            }
            
            if existing_macro_idx is not None:
                st.session_state['community_db'][existing_macro_idx] = macro_record
                st.success("✅ Đã cập nhật nhận định vĩ mô thành công!")
            else:
                st.session_state['community_db'].insert(0, macro_record)
                st.success("✅ Đã lưu mới nhận định vĩ mô vào kho cộng đồng!")

# =====================================================================
# PHẦN 2: CHẤM ĐIỂM BCTC (F-SCORE & M-SCORE)
# =====================================================================
elif menu == "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score)":
    st.title("🔍 Chấm Điểm BCTC Doanh Nghiệp")
    st.markdown(f"Thành viên: **{mask_email(user_email)}** | Tích hợp **Piotroski F-Score** & **Beneish M-Score**")
    
    ticker_symbol = st.text_input("Mã Cổ Phiếu (VD: HPG, VNM):", "HPG").upper()
    
    with st.container(border=True):
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

    with st.container(border=True):
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
        ta_t1 = st.number_input("Tổng tài sản t-1", value=11000.0)
        shares_t1 = st.number_input("Số lượng cổ phiếu t-1", value=1000.0)

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

    st.markdown("---")
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Beneish M-Score", f"{m_score:.2f}", "Ngưỡng: -1.78")
    col_res2.metric("Piotroski F-Score", f"{f_score} / 9")

    record_id = f"{user_email}_{ticker_symbol}"
    if st.button("💾 Lưu kết quả phân tích BCTC"):
        result_text = f"F-Score: {f_score}/9 | M-Score: {m_score:.2f}"
        existing_idx = next((i for i, item in enumerate(st.session_state['community_db']) if item['ID'] == record_id), None)
        
        new_record = {
            "ID": record_id,
            "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Email Thật (Quản lý nội bộ)": user_email,
            "Loại": "Phân tích BCTC",
            "Mã CK / Nội dung": ticker_symbol,
            "Nhóm ngành": "Doanh nghiệp Thường",
            "Kết quả / Đánh giá": result_text
        }
        
        if existing_idx is not None:
            st.session_state['community_db'][existing_idx] = new_record
            st.success(f"✅ Đã cập nhật bài phân tích mã **{ticker_symbol}** thành công!")
        else:
            st.session_state['community_db'].insert(0, new_record)
            st.success(f"✅ Đã lưu mới mã **{ticker_symbol}** vào kho cộng đồng!")

# =====================================================================
# PHẦN 3: KHO DỮ LIỆU CỘNG ĐỒNG (BẢO MẬT ẨN DANH)
# =====================================================================
elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)":
    st.title("📚 Kho Dữ liệu & Tra cứu Cộng Đồng")
    st.markdown("Tổng hợp báo cáo tài chính và nhận định vĩ mô từ các thành viên (Đã bảo mật ẩn danh).")
    
    df_show = pd.DataFrame(st.session_state['community_db'])
    if not df_show.empty:
        df_display = df_show.copy()
        df_display['Thành viên'] = df_display['Email Thật (Quản lý nội bộ)'].apply(mask_email)
        df_final = df_display[['Thời gian', 'Thành viên', 'Loại', 'Mã CK / Nội dung', 'Nhóm ngành', 'Kết quả / Đánh giá']]
        st.dataframe(df_final, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu trong kho.")
