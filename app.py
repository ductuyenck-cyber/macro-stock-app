import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN TRANG ---
st.set_page_config(
    page_title="Hệ thống Vĩ mô & Phân tích Tài chính Cộng Đồng",
    page_icon="📈",
    layout="wide"
)

# --- KHỞI TẠO KHO LƯU TRỮ TẠM TRONG SESSION (CỘNG ĐỒNG) ---
if 'community_db' not in st.session_state:
    st.session_state['community_db'] = [
        {
            "ID": "REC_01",
            "Thời gian": "2026-10-15 09:30", 
            "Thành viên (Ẩn danh)": "Tuyen_Pro", 
            "Mã CK": "HPG", 
            "Nhóm ngành": "Doanh nghiệp Thường", 
            "Kết quả / Đánh giá": "F-Score: 7/9 | M-Score: -2.15 (An toàn)",
            "Raw_Data": {}
        }
    ]

# --- KẾT NỐI GEMINI AI CLIENT AN TOÀN ---
has_gemini = False
ai_client = None
try:
    from google import genai
    gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
    if gemini_api_key:
        ai_client = genai.Client(api_key=gemini_api_key)
        has_gemini = True
except Exception:
    has_gemini = False

# --- ĐĂNG NHẬP AN TOÀN KHÔNG LỘ EMAIL (DÙNG NICKNAME & MÃ BÍ MẬT) ---
st.sidebar.title("🔐 Đăng nhập Thành viên")
nickname = st.sidebar.text_input("Nhập Biệt hiệu (Nickname) hiển thị công khai:", "NhàĐầuTư01")
member_pin = st.sidebar.text_input("Nhập Mã PIN bảo vệ (để sửa bài sau này):", type="password", value="1234")

if not nickname:
    st.warning("⚠️ Vui lòng nhập Biệt hiệu ở thanh bên trái để tiếp tục.")
    st.stop()
else:
    st.sidebar.success(f"Xin chào thành viên: **{nickname}**")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Chọn phân hệ:", [
        "📊 Phần 1: Dashboard Vĩ Mô & Market Timing", 
        "🔍 Phần 2: Chấm điểm BCTC & Lưu kho", 
        "📚 Phần 3: Kho Dữ liệu Cộng Đồng & Sửa bài"
    ])
    
    if has_gemini:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 Trợ lý AI Gemini")
        ai_prompt = st.sidebar.text_area("Hỏi AI về vĩ mô hoặc cổ phiếu:")
        if st.sidebar.button("💡 Gửi yêu cầu"):
            if ai_prompt:
                with st.spinner("AI đang phân tích..."):
                    try:
                        response = ai_client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=f"Dưới góc độ chuyên gia tài chính Việt Nam: {ai_prompt}"
                        )
                        st.sidebar.info(response.text)
                    except Exception as e:
                        st.sidebar.error(f"Lỗi AI: {e}")

# =====================================================================
# PHẦN 1: DASHBOARD VĨ MÔ & MARKET TIMING
# =====================================================================
if menu == "📊 Phần 1: Dashboard Vĩ Mô & Market Timing":
    st.title("📊 Phần 1: Dashboard Vĩ Mô & Market Timing")
    st.markdown("Hệ thống kiểm định dòng tiền vĩ mô dựa trên thông số chủ động.")
    
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
    st.markdown(f"Thành viên thực hiện: **{nickname}** (Bảo mật danh tính)")
    
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

    # Lưu hoặc Cập nhật bài viết
    record_id = f"{nickname}_{ticker_symbol}"
    if st.button("💾 Lưu / Cập nhật bài phân tích vào Kho Cộng Đồng", type="primary", use_container_width=True):
        result_text = f"F-Score: {f_score}/9 | M-Score: {m_score:.2f}"
        
        # Kiểm tra xem bài của nickname này đã tồn tại chưa để cập nhật (Update) thay vì tạo mới
        existing_idx = next((i for i, item in enumerate(st.session_state['community_db']) if item['ID'] == record_id), None)
        
        new_record = {
            "ID": record_id,
            "Thời gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Thành viên (Ẩn danh)": nickname,
            "Mã CK": ticker_symbol,
            "Nhóm ngành": "Doanh nghiệp Thường",
            "Kết quả / Đánh giá": result_text,
            "PIN": member_pin
        }
        
        if existing_idx is not None:
            st.session_state['community_db'][existing_idx] = new_record
            st.success(f"✅ Đã cập nhật (Sửa) bài phân tích mã **{ticker_symbol}** thành công!")
        else:
            st.session_state['community_db'].insert(0, new_record)
            st.success(f"✅ Đã lưu mới bài phân tích mã **{ticker_symbol}** vào Kho cộng đồng!")

# =====================================================================
# PHẦN 3: KHO DỮ LIỆU CỘNG ĐỒNG & CHỨC NĂNG SỬA BÀI
# =====================================================================
elif menu == "📚 Phần 3: Kho Dữ liệu Cộng Đồng & Sửa bài":
    st.title("📚 Kho Lưu trữ & Tra cứu Kết quả Phân tích Cộng Đồng")
    st.markdown("Xem toàn bộ đóng góp từ các thành viên ẩn danh trong hệ thống.")
    
    # Hiển thị bảng dạng ẩn danh (Không lộ email)
    df_show = pd.DataFrame(st.session_state['community_db'])
    if not df_show.empty:
        df_display = df_show[['Thời gian', 'Thành viên (Ẩn danh)', 'Mã CK', 'Nhóm ngành', 'Kết quả / Đánh giá']]
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu trong kho.")
        
    st.markdown("---")
    st.subheader("✏️ Quản lý & Chỉnh sửa bài viết của bạn")
    st.markdown("Nếu bạn muốn sửa lại bài phân tích đã lưu, hãy nhập Mã PIN xác thực của bạn:")
    
    my_records = [item for item in st.session_state['community_db'] if item['Thành viên (Ẩn danh)'] == nickname]
    if my_records:
        st.write(f"Bạn đang có **{len(my_records)}** bài phân tích trong kho.")
        selected_stock = st.selectbox("Chọn mã cổ phiếu bạn muốn chỉnh sửa lại:", [item['Mã CK'] for item in my_records])
        input_pin_check = st.text_input("Nhập Mã PIN của bạn để mở khóa sửa:", type="password")
        
        if st.button("🔓 Mở khóa & Chỉnh sửa bài"):
            target_item = next((item for item in my_records if item['Mã CK'] == selected_stock), None)
            if target_item and target_item.get('PIN') == input_pin_check:
                st.success(f"🔓 Đã xác thực thành công! Hãy chuyển sang **Phần 2: Chấm điểm BCTC** để thay đổi thông số và bấm 'Lưu / Cập nhật' để ghi đè.")
            else:
                st.error("❌ Sai mã PIN hoặc không khớp quyền sở hữu bài viết!")
    else:
        st.info("Bạn chưa có bài phân tích nào được lưu dưới biệt hiệu này.")
