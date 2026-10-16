import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- CẤU HÌNH GIAO DIỆN TRANG ---
st.set_page_config(
    page_title="Hệ thống Bảng kiểm Vĩ mô & Market Timing Cộng Đồng",
    page_icon="🚦",
    layout="wide"
)

# --- NHÚNG GOOGLE FORM TRỰC TIẾP TRÊN THANH BÊN (SIDEBAR) ---
st.sidebar.markdown("---")
with st.sidebar.expander("📝 Chưa có tài khoản? Đăng ký ngay"):
    st.markdown("Điền thông tin bên dưới để cấp quyền truy cập:")
    form_embed_url = "https://docs.google.com/forms/d/e/1FAIpQLSeGyXK_-dnAq4IjHsKaJjKp9O89ziolpuQyvr7sXWCL7fELoA/viewform?embedded=true"
    components.iframe(form_embed_url, height=420, scrolling=True)

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
        sheet_url = "https://docs.google.com/spreadsheets/d/1K_lTOPWDKqipNWNRSX2IFtm5YF8oILVsfPrluqhhXI4/gviz/tq?tqx=out:csv"
        df = pd.read_csv(sheet_url)
        return df
    except Exception:
        return pd.DataFrame()

# --- KHỞI TẠO KHO LƯU TRỮ TẠM KẾT QUẢ VĨ MÔ CỘNG ĐỒNG ---
if 'macro_community_db' not in st.session_state:
    st.session_state['macro_community_db'] = [
        {
            "ID": "tuyen.duc@gmail.com_macro",
            "Thời gian": "2026-10-15 09:30", 
            "Email Thật (Quản lý nội bộ)": "tuyen.duc@gmail.com", 
            "Trạng thái Vĩ mô": "🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)", 
            "Chi tiết đánh giá": "Lãi suất: Đi ngang | Tỷ giá: Ổn định | DXY: Trung tính | NHNN: Không can thiệp"
        }
    ]

# --- THANH ĐĂNG NHẬP (XÁC THỰC QUA GOOGLE SHEETS) ---
st.sidebar.markdown("---")
st.sidebar.title("🔐 Đăng nhập hệ thống")
user_email = st.sidebar.text_input("Nhập Gmail chính chủ của bạn:").strip().lower()

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
    st.warning("⚠️ Vui lòng nhập Gmail chính chủ đã đăng ký ở thanh bên trái để mở khóa ứng dụng.")
    st.stop()
else:
    st.sidebar.success(f"Xin chào: **{mask_email(user_email)}**")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Chọn phân hệ:", [
        "🚦 Phần 1: Bảng Kiểm Vĩ Mô & Market Timing", 
        "📚 Phần 2: Kho Dữ liệu Vĩ Mô Cộng Đồng (Ẩn danh)"
    ])

# =====================================================================
# PHẦN 1: BẢNG KIỂM VĨ MÔ & MARKET TIMING (TRƯỜNG TỒN)
# =====================================================================
if menu == "🚦 Phần 1: Bảng Kiểm Vĩ Mô & Market Timing":
    st.title("🚦 Bảng Kiểm Vĩ Mô & Market Timing (Trường tồn)")
    st.markdown("Đánh giá xu hướng dòng tiền vĩ mô thực tế để đưa ra quyết định hành động chiến lược.")
    
    with st.expander("⚙️ Thông số vĩ mô tham khảo hiện tại", expanded=True):
        c_i1, c_i2, c_i3, c_i4 = st.columns(4)
        with c_i1:
            st.metric("Tỷ giá Trung tâm (SBV)", "Biến động theo biên độ")
        with c_i2:
            st.metric("Lãi suất Liên ngân hàng (ON)", "4.25%")
        with c_i3:
            st.metric("Chỉ số DXY", "Vùng trung tính")
        with c_i4:
            st.metric("Thanh khoản HOSE", "18,500 Tỷ")

    st.markdown("---")
    st.subheader("📋 LỰA CHỌN TRẠNG THÁI VĨ MÔ 📋")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        laisuat = st.selectbox("1. Xu hướng Lãi suất & OMO:", ["-- Chọn trạng thái --", "Giảm / Nới lỏng (Tốt)", "Đi ngang (Bình thường)", "Tăng / Thắt chặt (Xấu)"])
        tygia = st.selectbox("2. Biến động Tỷ giá USD/VND (So với biên độ NHNN):", ["-- Chọn trạng thái --", "Trượt giá chậm, trong biên độ kiểm soát (Tốt)", "Tăng sốc, áp sát trần biên độ / Chợ đen biến động mạnh (Xấu)"])
    with col_v2:
        dxy = st.selectbox("3. Chỉ số Sức mạnh Đồng Đô la (DXY):", ["-- Chọn trạng thái --", "Xu hướng giảm / Dưới trung bình dài hạn (Tốt)", "Đi ngang / Vùng trung tính (Bình thường)", "Bứt phá vượt kháng cự mạnh / Đỉnh dài hạn (Xấu)"])
        nhnn = st.selectbox("4. Động thái của NHNN:", ["-- Chọn trạng thái --", "Bơm tiền / Mua lại ngoại tệ tăng dự trữ (Tốt)", "Không can thiệp (Bình thường)", "Hút Tín phiếu / Bán ngoại tệ can thiệp mạnh (Xấu)"])
        
    # Xử lý logic đánh giá tín hiệu
    if st.button("🔍 ĐÁNH GIÁ THỊ TRƯỜNG", type="primary", use_container_width=True):
        if "-- Chọn trạng thái --" in [laisuat, tygia, dxy, nhnn]:
            st.warning("⚠️ Vui lòng chọn đầy đủ 4 thông số vĩ mô trước khi đánh giá!")
        else:
            if "Xấu" in laisuat or "Xấu" in tygia or "Xấu" in dxy or "Hút Tín phiếu" in nhnn:
                st.session_state['current_macro_result'] = "🔴 ĐÈN ĐỎ (Defense / Retreat)"
                st.session_state['current_macro_detail'] = f"Lãi suất: {laisuat} | Tỷ giá: {tygia} | DXY: {dxy} | NHNN: {nhnn}"
                st.error(f"### {st.session_state['current_macro_result']}\n**Cảnh báo rủi ro vĩ mô!**\n\n**Hành động:** PHÒNG THỦ TUYỆT ĐỐI. Bán hết cổ phiếu đầu cơ. Đưa tỷ lệ tiền mặt về mức an toàn cao. Tuyệt đối không bắt đáy.")
            elif "Giảm" in laisuat and "Trượt giá chậm" in tygia and "Xu hướng giảm" in dxy and "Bơm tiền" in nhnn:
                st.session_state['current_macro_result'] = "🟢 ĐÈN XANH (All-in / Attack)"
                st.session_state['current_macro_detail'] = f"Lãi suất: {laisuat} | Tỷ giá: {tygia} | DXY: {dxy} | NHNN: {nhnn}"
                st.success(f"### {st.session_state['current_macro_result']}\n**Vĩ mô ủng hộ tuyệt đối!**\n\n**Hành động:** TẤN CÔNG TỔNG LỰC. Đánh tài sản lớn, tận dụng tối đa chu kỳ nới lỏng tiền tệ.")
            else:
                st.session_state['current_macro_result'] = "🟡 ĐÈN VÀNG (Guerrilla / Hit & Run)"
                st.session_state['current_macro_detail'] = f"Lãi suất: {laisuat} | Tỷ giá: {tygia} | DXY: {dxy} | NHNN: {nhnn}"
                st.warning(f"### {st.session_state['current_macro_result']}\n**Vĩ mô hỗn hợp, biến động biên độ.**\n\n**Hành động:** ĐÁNH DU KÍCH. Tỷ trọng linh hoạt, đánh ngắn T+, quản trị rủi ro chặt chẽ.")

    # Nút lưu kết quả vào kho cộng đồng (chỉ hiện khi đã bấm đánh giá)
    if 'current_macro_result' in st.session_state:
        st.markdown("---")
        if st.button("💾 Lưu / Cập nhật kết quả đánh giá này vào Kho Cộng Đồng", type="secondary", use_container_width=True):
            record_id = f"{user_email}_macro"
            existing_idx = next((i for i, item in enumerate(st.session_state['macro_community_db']) if item['ID'] == record_id), None)
            
            new_record = {
                "ID": record_id,
                "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Email Thật (Quản lý nội bộ)": user_email,
                "Trạng thái Vĩ mô": st.session_state['current_macro_result'],
                "Chi tiết đánh giá": st.session_state['current_macro_detail']
            }
            
            if existing_idx is not None:
                st.session_state['macro_community_db'][existing_idx] = new_record
                st.success("✅ Đã cập nhật (Sửa) kết quả nhận định vĩ mô của bạn vào kho cộng đồng thành công!")
            else:
                st.session_state['macro_community_db'].insert(0, new_record)
                st.success("✅ Đã lưu mới kết quả nhận định vĩ mô vào kho cộng đồng thành công!")

# =====================================================================
# PHẦN 2: KHO DỮ LIỆU VĨ MÔ CỘNG ĐỒNG (BẢO MẬT ẨN DANH)
# =====================================================================
elif menu == "📚 Phần 2: Kho Dữ liệu Vĩ Mô Cộng Đồng (Ẩn danh)":
    st.title("📚 Kho Dữ liệu & Nhận định Vĩ mô Cộng Đồng")
    st.markdown("Nơi tổng hợp góc nhìn và kết quả kiểm định vĩ mô từ các thành viên (Đã tự động bảo mật ẩn danh).")
    
    df_show = pd.DataFrame(st.session_state['macro_community_db'])
    if not df_show.empty:
        df_display = df_show.copy()
        df_display['Thành viên'] = df_display['Email Thật (Quản lý nội bộ)'].apply(mask_email)
        df_final = df_display[['Thời gian', 'Thành viên', 'Trạng thái Vĩ mô', 'Chi tiết đánh giá']]
        st.dataframe(df_final, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu nhận định vĩ mô trong kho.")
        
    st.markdown("---")
    st.subheader("🛠️ Quản lý nhận định của riêng bạn")
    
    my_posts = [item for item in st.session_state['macro_community_db'] if item['Email Thật (Quản lý nội bộ)'] == user_email]
    if my_posts:
        st.write(f"Bạn đang sở hữu **{len(my_posts)}** bản ghi nhận định vĩ mô trong kho.")
        if st.button("✏️ Đi đến bảng kiểm để cập nhật lại nhận định"):
            st.success("Hãy chuyển về **Phân hệ 1**, thay đổi thông số và bấm 'Lưu / Cập nhật' để ghi đè phiên bản mới nhất của bạn.")
    else:
        st.info("Bạn chưa lưu kết quả nhận định vĩ mô nào trong hệ thống với email này.")
