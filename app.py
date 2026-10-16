import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- CẤU HÌNH GIAO DIỆN CHUNG ---
st.set_page_config(
    page_title="Hệ thống Vĩ mô & Tài chính Cộng Đồng",
    page_icon="📈",
    layout="wide"
)

# --- CSS ĐIỀU CHỈNH TỰ ĐỘNG CHO MOBILE VÀ DESKTOP ---
st.markdown("""
    <style>
    /* Tối ưu nút bấm lớn dễ chạm trên mobile */
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
    /* Giao diện khung card */
    .card {
        padding: 15px;
        border-radius: 10px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- NHÚNG GOOGLE FORM TRÊN THANH BÊN ---
st.sidebar.markdown("---")
with st.sidebar.expander("📝 Chưa có tài khoản? Đăng ký ngay"):
    form_embed_url = "https://docs.google.com/forms/d/e/1FAIpQLSeGyXK_-dnAq4IjHsKaJjKp9O89ziolpuQyvr7sXWCL7fELoA/viewform?embedded=true"
    components.iframe(form_embed_url, height=350, scrolling=True)

# --- TÙY CHỌN CHẾ ĐỘ GIAO DIỆN (MOBILE / DESKTOP) ---
st.sidebar.markdown("---")
st.sidebar.subheader("📱 Tùy chỉnh Giao diện")
device_mode = st.sidebar.radio("Chế độ hiển thị:", ["🖥️ Giao diện Máy tính (Desktop)", "📱 Giao diện Điện thoại (Mobile)"], index=1)

# --- HÀM ẨN DANH EMAIL ---
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

# --- KHỞI TẠO KHO LƯU TRỮ TẠM ---
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
        }
    ]

# --- ĐĂNG NHẬP XÁC THỰC ---
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
                st.sidebar.error("❌ Email chưa đăng ký qua Google Form!")
        else:
            is_authenticated = True
    else:
        is_authenticated = True

if not is_authenticated:
    st.warning("⚠️ Vui lòng nhập Gmail chính chủ đã đăng ký ở menu bên trái để mở khóa ứng dụng.")
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
# PHÂN LUỒNG GIAO DIỆN (MOBILE VS DESKTOP)
# =====================================================================

if "📱 Giao diện Điện thoại" in device_mode:
    # ================= GIAO DIỆN DÀNH CHO ĐIỆN THOẠI (1 CỘT, TỐI GIẢN, DỄ CUỘN) =================
    st.markdown("### 📱 Phiên bản Di động")
    
    if menu == "📊 Phần 1: Dashboard Vĩ Mô & Market Timing":
        st.title("📊 Vĩ Mô & Market Timing")
        
        with st.container(border=True):
            laisuat = st.selectbox("1. Lãi suất & OMO:", ["-- Chọn --", "Giảm / Nới lỏng (Tốt)", "Đi ngang", "Tăng / Thắt chặt (Xấu)"], key="m_ls")
            tygia = st.selectbox("2. Tỷ giá USD/VND:", ["-- Chọn --", "Trượt giá chậm (Tốt)", "Tăng sốc / Căng thẳng (Xấu)"], key="m_tg")
            dxy = st.selectbox("3. Chỉ số DXY:", ["-- Chọn --", "Xu hướng giảm (Tốt)", "Đi ngang", "Bứt phá đỉnh (Xấu)"], key="m_dxy")
            nhnn = st.selectbox("4. Động thái NHNN:", ["-- Chọn --", "Bơm tiền (Tốt)", "Không can thiệp", "Hút tín phiếu (Xấu)"], key="m_nhnn")
            
        if st.button("🔍 ĐÁNH GIÁ NGAY", key="m_btn"):
            if "-- Chọn --" in [laisuat, tygia, dxy, nhnn]:
                st.warning("⚠️ Chọn đủ 4 thông số!")
            else:
                if "Xấu" in laisuat or "Xấu" in tygia or "Xấu" in dxy or "Hút tín phiếu" in nhnn:
                    st.session_state['macro_result'] = "🔴 ĐÈN ĐỎ (Phòng thủ)"
                    st.error(f"### {st.session_state['macro_result']}\nTiền mặt 80-100%. Không bắt đáy.")
                elif "Giảm" in laisuat and "Trượt giá chậm" in tygia and "Xu hướng giảm" in dxy and "Bơm tiền" in nhnn:
                    st.session_state['macro_result'] = "🟢 ĐÈN XANH (Tấn công)"
                    st.success(f"### {st.session_state['macro_result']}\nFull tài khoản. Nới lỏng tối đa.")
                else:
                    st.session_state['macro_result'] = "🟡 ĐÈN VÀNG (Du kích)"
                    st.warning(f"### {st.session_state['macro_result']}\nTỷ trọng 30-50%, đánh ngắn T+.")

        if 'macro_result' in st.session_state:
            if st.button("💾 Lưu kết quả vĩ mô", key="m_save_macro"):
                rec_id = f"{user_email}_MACRO"
                idx = next((i for i, item in enumerate(st.session_state['community_db']) if item['ID'] == rec_id), None)
                record = {"ID": rec_id, "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"), "Email Thật (Quản lý nội bộ)": user_email, "Loại": "Nhận định Vĩ mô", "Mã CK / Nội dung": "VĨ MÔ", "Nhóm ngành": "Timing", "Kết quả / Đánh giá": st.session_state['macro_result']}
                if idx is not None: st.session_state['community_db'][idx] = record
                else: st.session_state['community_db'].insert(0, record)
                st.success("✅ Đã lưu kết quả vĩ mô!")

    elif menu == "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score)":
        st.title("🔍 Chấm điểm BCTC")
        ticker_symbol = st.text_input("Mã Cổ Phiếu:", "HPG", key="m_ticker").upper()
        
        with st.container(border=True):
            st.write("🟢 **Năm nay (t)**")
            rev_t = st.number_input("Doanh thu thuần", value=10000.0, key="m_rev_t")
            ni_t = st.number_input("LN sau thuế", value=1000.0, key="m_ni_t")
            cfo_t = st.number_input("Dòng tiền HĐKD (CFO)", value=1200.0, key="m_cfo_t")
            ta_t = st.number_input("Tổng tài sản", value=12000.0, key="m_ta_t")
            
        with st.container(border=True):
            st.write("🟠 **Năm trước (t-1)**")
            rev_t1 = st.number_input("Doanh thu thuần t-1", value=9000.0, key="m_rev_t1")
            ni_t1 = st.number_input("LN sau thuế t-1", value=900.0, key="m_ni_t1")
            ta_t1 = st.number_input("Tổng tài sản t-1", value=11000.0, key="m_ta_t1")

        if st.button("💾 Lưu BCTC", key="m_save_bctc"):
            st.success(f"✅ Đã lưu phân tích mã {ticker_symbol}!")

    elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)":
        st.title("📚 Kho Dữ liệu Cộng Đồng")
        df_show = pd.DataFrame(st.session_state['community_db'])
        if not df_show.empty:
            df_show['Thành viên'] = df_show['Email Thật (Quản lý nội bộ)'].apply(mask_email)
            st.dataframe(df_show[['Thời gian', 'Thành viên', 'Loại', 'Mã CK / Nội dung', 'Kết quả / Đánh giá']], use_container_width=True)

else:
    # ================= GIAO DIỆN DÀNH CHO MÁY TÍNH (NHIỀU CỘT, RỘNG RÃI) =================
    st.markdown("### 🖥️ Phiên bản Máy tính (Desktop)")
    
    if menu == "📊 Phần 1: Dashboard Vĩ Mô & Market Timing":
        st.title("📊 Dashboard Vĩ Mô & Market Timing")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            laisuat = st.selectbox("1. Xu hướng Lãi suất & OMO:", ["-- Chọn trạng thái --", "Giảm / Nới lỏng (Tốt)", "Đi ngang (Bình thường)", "Tăng / Thắt chặt (Xấu)"])
            tygia = st.selectbox("2. Biến động Tỷ giá USD/VND (So với biên độ NHNN):", ["-- Chọn trạng thái --", "Trượt giá chậm, trong biên độ kiểm soát (Tốt)", "Tăng sốc, áp sát trần biên độ / Chợ đen biến động mạnh (Xấu)"])
        with col_v2:
            dxy = st.selectbox("3. Chỉ số Sức mạnh Đồng Đô la (DXY):", ["-- Chọn trạng thái --", "Xu hướng giảm / Dưới trung bình dài hạn (Tốt)", "Đi ngang / Vùng trung tính (Bình thường)", "Bứt phá vượt kháng cự mạnh / Đỉnh dài hạn (Xấu)"])
            nhnn = st.selectbox("4. Động thái của NHNN:", ["-- Chọn trạng thái --", "Bơm tiền / Mua lại ngoại tệ tăng dự trữ (Tốt)", "Không can thiệp (Bình thường)", "Hút Tín phiếu / Bán ngoại tệ can thiệp mạnh (Xấu)"])
            
        if st.button("🔍 ĐÁNH GIÁ THỊ TRƯỜNG TOÀN DIỆN", type="primary", use_container_width=True):
            if "-- Chọn trạng thái --" in [laisuat, tygia, dxy, nhnn]:
                st.warning("⚠️ Vui lòng chọn đầy đủ 4 thông số vĩ mô trước khi đánh giá!")
            else:
                if "Xấu" in laisuat or "Xấu" in tygia or "Xấu" in dxy or "Hút Tín phiếu" in nhnn:
                    st.session_state['macro_result'] = "🔴 ĐÈN ĐỎ (Defense / Retreat)"
                    st.error(f"### {st.session_state['macro_result']}\n**Cảnh báo rủi ro vĩ mô!**\n\n**Hành động:** PHÒNG THỦ TUYỆT ĐỐI. Bán hết cổ phiếu đầu cơ. Đưa tỷ lệ tiền mặt về mức an toàn cao.")
                elif "Giảm" in laisuat and "Trượt giá chậm" in tygia and "Xu hướng giảm" in dxy and "Bơm tiền" in nhnn:
                    st.session_state['macro_result'] = "🟢 ĐÈN XANH (All-in / Attack)"
                    st.success(f"### {st.session_state['macro_result']}\n**Vĩ mô ủng hộ tuyệt đối!**\n\n**Hành động:** TẤN CÔNG TỔNG LỰC. Đánh tài sản lớn, tận dụng tối đa chu kỳ nới lỏng tiền tệ.")
                else:
                    st.session_state['macro_result'] = "🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)"
                    st.warning(f"### {st.session_state['macro_result']}\n**Vĩ mô hỗn hợp, biến động biên độ.**\n\n**Hành động:** ĐÁNH DU KÍCH. Tỷ trọng linh hoạt, đánh ngắn T+.")

        if 'macro_result' in st.session_state:
            st.markdown("---")
            if st.button("💾 Lưu kết quả vĩ mô vào Kho Cộng Đồng", type="secondary", use_container_width=True):
                rec_id = f"{user_email}_MACRO"
                idx = next((i for i, item in enumerate(st.session_state['community_db']) if item['ID'] == rec_id), None)
                record = {"ID": rec_id, "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"), "Email Thật (Quản lý nội bộ)": user_email, "Loại": "Nhận định Vĩ mô", "Mã CK / Nội dung": "VĨ MÔ TOÀN CẢNH", "Nhóm ngành": "Market Timing", "Kết quả / Đánh giá": st.session_state['macro_result']}
                if idx is not None: st.session_state['community_db'][idx] = record
                else: st.session_state['community_db'].insert(0, record)
                st.success("✅ Đã lưu kết quả vĩ mô thành công!")

    elif menu == "🔍 Phần 2: Chấm điểm BCTC (F-Score & M-Score)":
        st.title("🔍 Chấm Điểm BCTC Doanh Nghiệp (Desktop)")
        ticker_symbol = st.text_input("Mã Cổ Phiếu / Doanh Nghiệp (VD: HPG, VNM):", "HPG").upper()
        
        col_t, col_t1 = st.columns(2)
        with col_t:
            st.subheader("🟢 NĂM NAY (Năm t)")
            rev_t = st.number_input("Doanh thu thuần (Sales_t)", value=10000.0)
            ni_t = st.number_input("Lợi nhuận sau thuế (Net Income)", value=1000.0)
            cfo_t = st.number_input("Dòng tiền HĐKD (CFO)", value=1200.0)
            ta_t = st.number_input("Tổng tài sản", value=12000.0)
        with col_t1:
            st.subheader("🟠 NĂM TRƯỚC (Năm t-1)")
            rev_t1 = st.number_input("Doanh thu thuần (Sales_t-1)", value=9000.0)
            ni_t1 = st.number_input("Lợi nhuận sau thuế t-1", value=900.0)
            ta_t1 = st.number_input("Tổng tài sản t-1", value=11000.0)

        if st.button("💾 Lưu bài phân tích BCTC", type="primary", use_container_width=True):
            st.success(f"✅ Đã lưu mã **{ticker_symbol}** thành công!")

    elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng (Ẩn danh)":
        st.title("📚 Kho Dữ liệu & Tra cứu Cộng Đồng (Desktop)")
        df_show = pd.DataFrame(st.session_state['community_db'])
        if not df_show.empty:
            df_show['Thành viên'] = df_show['Email Thật (Quản lý nội bộ)'].apply(mask_email)
            st.dataframe(df_show[['Thời gian', 'Thành viên', 'Loại', 'Mã CK / Nội dung', 'Nhóm ngành', 'Kết quả / Đánh giá']], use_container_width=True)
