import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import requests

# --- CẤU HÌNH GIAO DIỆN & TỐI ƯU MOBILE ---
st.set_page_config(
    page_title="Hệ thống Vĩ mô & Tài chính Cộng Đồng",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        height: 3.2em;
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
    </style>
""", unsafe_allow_html=True)

# --- CẤU HÌNH GOOGLE SHEETS & WEB APP API CỦA BẠN ---
SHEET_ID = "1zeaMCtBq0gGY_ojKCkGugQATs6DwQgHD3V9aJSTobkE"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzoxnstRuSKCek9TXrqoHGPly-ercYvpSRNDw9E-XLeEKp7U2BhKF0R-avbgdOdC7wU/exec"

# --- ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS (CSV EXPORT) ---
@st.cache_data(ttl=5)
def load_data_from_sheets():
    try:
        # Tab 1: Danh sách thành viên (Tab đầu tiên nhận phản hồi Google Form)
        members_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
        df_members = pd.read_csv(members_url)
    except Exception:
        df_members = pd.DataFrame()
        
    try:
        # Tab 2: Kho dữ liệu cộng đồng (Tab Community_DB)
        community_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Community_DB"
        df_community = pd.read_csv(community_url)
    except Exception:
        df_community = pd.DataFrame(columns=["ID", "Thời gian", "Email Thật", "Loại", "Mã CK / Nội dung", "Nhóm ngành", "Kết quả / Đánh giá"])
        
    return df_members, df_community

# --- HÀM GHI DỮ LIỆU THÔNG QUA GOOGLE APPS SCRIPT WEB APP ---
def save_to_gspreadsheet(new_record):
    try:
        payload = {
            "ID": new_record["ID"],
            "Thờigian": new_record["Thời gian"],
            "EmailThật": new_record["Email Thật"],
            "Loại": new_record["Loại"],
            "MãCKNộiDung": new_record["Mã CK / Nội dung"],
            "Nhómngành": new_record["Nhóm ngành"],
            "KếtquảĐánhgiá": new_record["Kết quả / Đánh giá"]
        }
        response = requests.post(WEB_APP_URL, json=payload, timeout=10)
        if response.status_code == 200:
            st.cache_data.clear() # Xóa cache để cập nhật dữ liệu mới ngay lập tức
            return True
        return False
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return False

# --- NHÚNG GOOGLE FORM TRỰC TIẾP TRÊN THANH BÊN ---
st.sidebar.markdown("---")
with st.sidebar.expander("📝 Chưa có tài khoản? Đăng ký ngay"):
    st.markdown("Điền thông tin bên dưới:")
    # Thay link form nhúng mới của bạn vào đây nếu cần
    form_embed_url = "https://docs.google.com/forms/d/e/1FAIpQLSeGyXK_-dnAq4IjHsKaJjKp9O89ziolpuQyvr7sXWCL7fELoA/viewform?embedded=true"
    components.iframe(form_embed_url, height=350, scrolling=True)

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

df_members, df_community = load_data_from_sheets()

# --- XÁC THỰC THÀNH VIÊN ---
st.sidebar.markdown("---")
st.sidebar.title("🔐 Xác thực Thành viên")
user_email = st.sidebar.text_input("Nhập Gmail chính chủ đã đăng ký:").strip().lower()

is_authenticated = False

if user_email and "@gmail.com" in user_email:
    if not df_members.empty:
        email_col = next((col for col in df_members.columns if 'email' in col.lower() or 'thư' in col.lower()), None)
        if email_col:
            registered_emails = df_members[email_col].dropna().astype(str).str.lower().tolist()
            if user_email in registered_emails:
                is_authenticated = True
            else:
                st.sidebar.error("❌ Email này chưa điền Form đăng ký!")
        else:
            is_authenticated = True
    else:
        # Nếu form chưa có ai điền, tạm thời cho phép truy cập để test hệ thống
        is_authenticated = True

if not is_authenticated:
    st.warning("⚠️ **Bảo mật:** Vui lòng nhập Gmail chính chủ đã đăng ký qua Google Form ở menu bên trái để mở khóa ứng dụng.")
    st.stop()
else:
    st.sidebar.success(f"Xin chào: **{mask_email(user_email)}**")
    st.sidebar.markdown("---")
    menu = st.sidebar.selectbox("📂 Chọn phân hệ:", [
        "📊 Phần 1: Dashboard Vĩ Mô & Market Timing", 
        "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score)", 
        "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)"
    ])

# =====================================================================
# PHẦN 1: DASHBOARD VĨ MÔ & MARKET TIMING
# =====================================================================
if menu == "📊 Phần 1: Dashboard Vĩ Mô & Market Timing":
    st.title("📊 Dashboard Vĩ Mô & Market Timing")
    st.markdown("Đánh giá chu kỳ dòng tiền vĩ mô thực tế để định hướng chiến lược đầu tư.")
    
    with st.container(border=True):
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            laisuat = st.selectbox("1. Xu hướng Lãi suất & OMO:", ["-- Chọn trạng thái --", "Giảm / Nới lỏng (Tốt)", "Đi ngang (Bình thường)", "Tăng / Thắt chặt (Xấu)"])
            tygia = st.selectbox("2. Biến động Tỷ giá USD/VND:", ["-- Chọn trạng thái --", "Trượt giá chậm, trong biên độ kiểm soát (Tốt)", "Tăng sốc, áp sát trần biên độ (Xấu)"])
        with col_v2:
            dxy = st.selectbox("3. Chỉ số Sức mạnh Đồng Đô la (DXY):", ["-- Chọn trạng thái --", "Xu hướng giảm / Dưới trung bình (Tốt)", "Đi ngang / Vùng trung tính (Bình thường)", "Bứt phá vượt kháng cự mạnh (Xấu)"])
            nhnn = st.selectbox("4. Động thái của NHNN:", ["-- Chọn trạng thái --", "Bơm tiền / Mua lại ngoại tệ (Tốt)", "Không can thiệp (Bình thường)", "Hút Tín phiếu / Bán ngoại tệ (Xấu)"])
            
    if st.button("🔍 ĐÁNH GIÁ THỊ TRƯỜNG TOÀN DIỆN", type="primary"):
        if "-- Chọn trạng thái --" in [laisuat, tygia, dxy, nhnn]:
            st.warning("⚠️ Vui lòng chọn đầy đủ 4 thông số vĩ mô!")
        else:
            if "Xấu" in laisuat or "Xấu" in tygia or "Xấu" in dxy or "Hút Tín phiếu" in nhnn:
                st.session_state['macro_result'] = "🔴 ĐÈN ĐỎ (Defense / Retreat)"
                st.error("### 🔴 ĐÈN ĐỎ\n**Hành động:** PHÒNG THỦ TUYỆT ĐỐI. Tỷ lệ tiền mặt 80-100%.")
            elif "Giảm" in laisuat and "Trượt giá chậm" in tygia and "Xu hướng giảm" in dxy and "Bơm tiền" in nhnn:
                st.session_state['macro_result'] = "🟢 ĐÈN XANH (All-in / Attack)"
                st.success("### 🟢 ĐÈN XANH\n**Hành động:** TẤN CÔNG TỔNG LỰC. Tối đa hóa tài sản.")
            else:
                st.session_state['macro_result'] = "🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)"
                st.warning("### 🟡 ĐÈN VÀNG\n**Hành động:** ĐÁNH DU KÍCH. Tỷ trọng linh hoạt, đánh ngắn T+.")

    if 'macro_result' in st.session_state:
        st.markdown("---")
        if st.button("💾 Lưu kết quả vĩ mô thẳng lên Google Sheets", type="secondary"):
            rec_id = f"{user_email}_MACRO"
            record = {
                "ID": rec_id, 
                "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                "Email Thật": user_email, 
                "Loại": "Nhận định Vĩ mô", 
                "Mã CK / Nội dung": "VĨ MÔ TOÀN CẢNH", 
                "Nhóm ngành": "Market Timing", 
                "Kết quả / Đánh giá": st.session_state['macro_result']
            }
            if save_to_gspreadsheet(record):
                st.success("✅ Đã lưu kết quả vĩ mô thành công lên Google Sheets!")
                st.rerun()

# =====================================================================
# PHẦN 2: CHẤM ĐIỂM BCTC (F-SCORE & M-SCORE ĐẦY ĐỦ CÔNG THỨC)
# =====================================================================
elif menu == "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score)":
    st.title("🔍 Chấm Điểm BCTC Doanh Nghiệp")
    st.markdown("Tích hợp chuẩn gốc **Piotroski F-Score (9 Tiêu chí)** & **Beneish M-Score (8 Biến đầy đủ)**")
    
    ticker_symbol = st.text_input("Mã Cổ Phiếu / Doanh Nghiệp (VD: HPG, VNM):", "HPG").upper()
    
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
        1 if ni_t > 0 else 0, 1 if cfo_t > 0 else 0, 1 if roa_t > roa_t1 else 0,
        1 if cfo_t > ni_t else 0, 1 if safe_div(ltd_t, ta_t) < safe_div(ltd_t1, ta_t1) else 0,
        1 if safe_div(ca_t, cl_t) > safe_div(ca_t1, cl_t1) else 0, 1 if shares_t <= shares_t1 else 0,
        1 if (gm_t - gm_t1) > 0 else 0, 1 if (safe_div(rev_t, ta_t) - safe_div(rev_t1, ta_t1)) > 0 else 0
    ])

    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Beneish M-Score", f"{m_score:.2f}", "Ngưỡng: -1.78")
    col_res2.metric("Piotroski F-Score", f"{f_score} / 9")

    record_id = f"{user_email}_{ticker_symbol}"
    if st.button("💾 Lưu phân tích BCTC thẳng lên Google Sheets", type="primary"):
        result_text = f"F-Score: {f_score}/9 | M-Score: {m_score:.2f}"
        record = {
            "ID": record_id,
            "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Email Thật": user_email,
            "Loại": "Phân tích BCTC",
            "Mã CK / Nội dung": ticker_symbol,
            "Nhóm ngành": "Doanh nghiệp Thường",
            "Kết quả / Đánh giá": result_text
        }
        if save_to_gspreadsheet(record):
            st.success(f"✅ Đã lưu phân tích mã **{ticker_symbol}** lên Google Sheets thành công!")
            st.rerun()

# =====================================================================
# PHẦN 3: KHO DỮ LIỆU CỘNG ĐỒNG (BẢO MẬT ẨN DANH)
# =====================================================================
elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)":
    st.title("📚 Kho Dữ liệu & Tra cứu Cộng Đồng")
    st.markdown("Tổng hợp báo cáo tài chính và nhận định vĩ mô từ các thành viên (Đã tự động bảo mật ẩn danh).")
    
    if not df_community.empty:
        df_display = df_community.copy()
        email_field = next((col for col in df_display.columns if 'email' in col.lower() or 'thật' in col.lower()), None)
        if email_field:
            df_display['Thành viên'] = df_display[email_field].apply(mask_email)
            display_cols = [c for c in ['Thời gian', 'Thành viên', 'Loại', 'Mã CK / Nội dung', 'Nhóm ngành', 'Kết quả / Đánh giá'] if c in df_display.columns]
            st.dataframe(df_display[display_cols], use_container_width=True)
        else:
            st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Kho cộng đồng trên Google Sheets hiện chưa có bản ghi nào.")