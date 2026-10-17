## Cài đặt trên máy Windows

1. Cài **Python 3.11 hoặc 3.12** từ https://www.python.org/downloads/. Khi cài, chọn **Add python.exe to PATH**.
2. Giải nén toàn bộ gói StockAI vào một thư mục, ví dụ `D:\StockAI`. Không mở chương trình bên trong tệp ZIP.
3. Nhấp đúp **CHAY_WINDOWS.bat**. Lần đầu cần Internet để tải thư viện. Cửa sổ dòng lệnh sẽ mở; giữ cửa sổ đó trong lúc dùng.
4. Trình duyệt mở địa chỉ `http://localhost:8501`. Nếu không tự mở, nhập địa chỉ này vào Chrome.
5. Dừng ứng dụng bằng **Ctrl+C** trong cửa sổ dòng lệnh. Lần sau mở lại cùng tệp BAT.

Không phải đăng ký Gmail, điền Form, bật API hay nhập Secrets.
Nếu Windows không nhận lệnh `py`, mở Terminal trong thư mục và chạy:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Mac/Linux: mở Terminal trong thư mục, chạy `bash CHAY_MAC_LINUX.sh`. Cần Python 3.11/3.12 và hỗ trợ venv.

## Thử ứng dụng trong hai phút

1. Chọn **Phân tích BCTC**.
2. Bấm **Nạp dữ liệu minh họa**. Nguồn ghi rõ đây là dữ liệu giả lập.
3. Kéo xuống kết quả: **F-Score = 4/9**, **M-Score = −2,57358** (giao diện làm tròn −2,574).
4. Xem từng tiêu chí: LNST dương, CFO dương, CFO > LNST, không phát hành huy động vốn đạt điểm. Các tỷ số không tăng/giảm nên năm tiêu chí còn lại 0 điểm.
5. Xóa phải thu năm t−1: DSRI sẽ báo thiếu dữ liệu và M-Score không còn kết quả. Nhập 0: DSRI báo mẫu số bằng 0. Hai trường hợp được phân biệt.
6. Bấm **Tải dữ liệu + kết quả Excel**. Giữ tệp để lưu lại hoặc nhập tiếp lần sau.

## Phân tích doanh nghiệp thật

1. Bấm **Tạo bản mới**. Chọn mã, năm t, đơn vị và hợp nhất/riêng lẻ.
2. Lấy BCTC năm của doanh nghiệp; ưu tiên bản kiểm toán. Dùng cùng kỳ kế toán và cùng phạm vi báo cáo cho t và t−1. Nếu có điều chỉnh hồi tố, dùng số so sánh đã điều chỉnh nhất quán.
3. Ghi link BCTC, số trang và thuyết minh vào ô nguồn. Bỏ chọn dấu minh họa khi bạn đã thay toàn bộ bằng dữ liệu thật.
4. Nhập số hai năm. Tab thứ ba chỉ cần **tổng tài sản cuối năm t−2**, tức tổng tài sản đầu năm t−1.
5. Kiểm tra phát hành vốn trong thuyết minh. Chọn Có/Không; không suy luận chỉ từ số cổ phiếu.
6. Kiểm tra hai dấu xấp xỉ lợi nhuận. Giữ dấu nếu dùng chỉ tiêu thay thế; chỉ bỏ khi đã đối chiếu đúng phạm vi mô hình. Nút sao chép LNST sang lợi nhuận hoạt động tiếp tục chỉ tạo bản xấp xỉ, không chứng minh hai khoản bằng nhau.
7. Xem các lỗi, lưu ý và bảng chi tiết trước khi dùng kết quả. Ô trống không tính là 0. Bạn vẫn tải được dữ liệu chưa hoàn chỉnh để làm tiếp.
8. Tải Excel trước khi đóng tab. Ứng dụng không có cơ sở dữ liệu tự lưu lâu dài; nếu phiên máy chủ mất, dữ liệu chưa tải có thể mất.

### Lấy số liệu ở đâu?

| Chỉ tiêu | Cách lấy |
|---|---|
| Doanh thu, giá vốn | Báo cáo KQKD: doanh thu thuần và giá vốn. Giá vốn nhập dương. |
| Phải thu | Phải thu khách hàng thuần; không cộng tất cả phải thu khác. Dùng nhất quán hai năm. Nếu số có cả phần dài hạn, cần ghi rõ và kiểm tra phạm vi. |
| CA, CL, tổng tài sản | Bảng cân đối: tài sản ngắn hạn, nợ ngắn hạn, tổng tài sản. |
| PP&E | Giá trị còn lại TSCĐ hữu hình. Không cộng BĐS đầu tư, XDCB dở dang, đầu tư tài chính. |
| Khấu hao | Khấu hao trong năm tương ứng PP&E; không phải hao mòn lũy kế, không mặc nhiên dùng cả khấu hao vô hình. |
| SG&A | Chi phí bán hàng cộng quản lý doanh nghiệp; nhập dương. |
| Tổng nợ phải trả dài hạn | Chỉ tiêu tổng nợ dài hạn trên bảng cân đối, dùng LVGI của M-Score. |
| Vay dài hạn gồm phần đến hạn | Đọc thuyết minh vay; gồm phần vay dài hạn được chuyển sang nợ ngắn hạn. Dùng F-Score. Không cộng toàn bộ vay ngắn hạn. |
| LNST cho F-Score | Lợi nhuận toàn doanh nghiệp, nhất quán với tài sản/CFO. Mô hình gốc dùng lợi nhuận trước khoản bất thường; nếu dùng LNST thay thế, giữ nhãn điều chỉnh. |
| Lợi nhuận hoạt động tiếp tục | Lợi nhuận sau thuế từ hoạt động tiếp tục dùng TATA; nếu lấy LNST thay thế, đánh dấu xấp xỉ. |
| CFO | Lưu chuyển tiền thuần từ HĐKD, có thể âm. |

Cùng một đơn vị tiền cho mọi khoản, mọi năm. Đổi nhãn đơn vị trong ứng dụng **không tự chuyển đổi số**. Ví dụ tổng tài sản 12.000 triệu đồng phải nhập `12000`, không nhập 12 nếu vẫn chọn Triệu VND.

## Nhập và dùng lại Excel

- Dùng **Tải mẫu Excel trống** trong ứng dụng hoặc `Mau_nhap_BCTC.xlsx` trong gói.
- Sheet **Du_lieu**: giữ nguyên field và tên cột. Nhập số ở cột t, t1; chỉ cần assets ở t2. Ô không biết để trống. Không nhập dấu gạch ngang thay số 0.
- Sheet **Thong_tin**: year là năm t; ticker là mã; unit và scope theo các giá trị mẫu. source ghi nguồn. issuance là Có/Không/Chưa xác định. Các dấu `f_income_proxy`, `m_income_proxy`, `demo` dùng giá trị Excel TRUE/FALSE.
- Không nhập công thức trong mẫu: chương trình yêu cầu số thực, không dùng kết quả công thức đã lưu đệm. Điều này tránh đọc số cũ khi Excel chưa tính lại.
- Chọn tệp rồi bấm **Áp dụng tệp Excel**. Dữ liệu hiện có bị thay bằng tệp được chọn, không tự trộn.
- Tệp kết quả cũng nhập lại được. Hai sheet đầu là dữ liệu; các sheet kết quả là ảnh chụp kết quả tại thời điểm tải, không chứa công thức tính động. Sau khi sửa Excel, nhập lại ứng dụng để tính lại.
- Tệp tối đa 5 MB. Bản này phân tích một doanh nghiệp, một cặp năm mỗi lần, không nhập hàng loạt.

## Hiểu kết quả đúng phạm vi

**F-Score:** tổng chín tín hiệu nhị phân. ROA và vòng quay dùng tài sản đầu kỳ; đòn bẩy dùng vay dài hạn/tài sản bình quân; thanh toán dùng CA/CL cuối kỳ. Bất kỳ tiêu chí thiếu dữ liệu nào đều khiến tổng F-Score chưa hoàn chỉnh. Điểm cao hơn biểu thị nhiều tiêu chí đạt hơn, không phải khuyến nghị mua.

**M-Score:** mô hình 8 biến với hằng số −4,84; các biến và đóng góp đều hiển thị. Nếu một biến không xác định, ứng dụng không trả tổng. Với biên gộp không dương, ứng dụng dừng diễn giải GMI theo thông lệ để tránh một chỉ số dễ hiểu sai. Khấu hao/SG&A/phải thu bằng 0 có thể làm mô hình không tính được; không thay tỷ số đó bằng 0 hay 1.

Không tự gắn ngưỡng −1,78 hay −2,22: các ngưỡng phụ thuộc phiên bản/tiêu chí phân loại và dữ liệu. Bản này chưa hiệu chuẩn cho thị trường Việt Nam. Không chuyển M-Score thành xác suất gian lận. Việc nhập đủ không chứng minh số liệu đúng.

Không áp dụng trực tiếp cho ngân hàng, bảo hiểm, công ty chứng khoán. Mô hình không thay thế đọc thuyết minh, kiểm toán, định giá và kiểm tra đặc thù ngành. Chưa có OCR PDF, cào BCTC, dữ liệu giá tự động, tài khoản hoặc kho cộng đồng trong phiên bản này.

## Theo dõi vĩ mô

Chọn bốn yếu tố thuận lợi/trung tính/bất lợi, ghi ngày và nguồn. Kết quả cập nhật trực tiếp, tải được ghi chú TXT. Đây là bảng quy tắc thủ công, không phải mô hình dự báo. Không dùng để tự động xác định tỷ trọng tiền mặt hay all-in.

## Đưa lên Streamlit Community Cloud

1. Tạo một repository GitHub riêng cho ứng dụng. Đưa các tệp app.py, engine.py, file_io.py, requirements.txt, HUONG_DAN.md, Mau_nhap_BCTC.xlsx và thư mục .streamlit vào repository. Không tải dữ liệu cá nhân/BCTC nội bộ lên GitHub công khai.
2. Đăng nhập https://share.streamlit.io/, tạo app từ repository; chọn file chạy **app.py**, Python 3.11 hoặc 3.12 nếu có lựa chọn.
3. Không cấu hình Secrets cho bản này. Nếu app cũ đang chạy Apps Script, thay toàn bộ mã ứng dụng tương ứng, không ghép các hàm cũ vào.
4. Chạy thử dữ liệu minh họa, nhập/xuất Excel và mở trên điện thoại trước khi chia sẻ link.
5. Mỗi phiên trình duyệt có dữ liệu riêng trong session_state. Khi triển khai trên Cloud, tệp nhập được xử lý trên máy chủ Cloud, không phải chỉ trên máy người dùng. Ứng dụng không tự ghi tệp nhập vào cơ sở dữ liệu hay gửi sang API khác.

## Nếu gặp lỗi

- **ModuleNotFoundError:** chạy BAT hoặc cài `python -m pip install -r requirements.txt` bằng cùng Python chạy ứng dụng.
- **Cổng 8501 đang dùng:** đóng cửa sổ app cũ hoặc chạy `python -m streamlit run app.py --server.port 8502`.
- **Excel không đúng mẫu:** tải mẫu mới, không đổi field, không thêm dòng, không nhập số dạng chữ hoặc công thức.
- **Chưa đủ dữ liệu:** xem dòng lý do trong F-Score/M-Score. Đừng điền 0 để xóa cảnh báo.
- **Ứng dụng mở nhưng chưa có số:** bản mới cố ý để trống. Bấm minh họa để thử.
- **Lưu xong không thấy tệp:** kiểm tra thư mục Downloads của trình duyệt. Ứng dụng không tự lưu vào thư mục cài đặt.

## Tài liệu mô hình và công nghệ

- Piotroski (2000), *Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers*: https://www.ivey.uwo.ca/media/3775523/value_investing_the_use_of_historical_financial_statement_information.pdf
- Beneish (1999), *The Detection of Earnings Manipulation*: https://rpc.cfainstitute.org/research/financial-analysts-journal/1999/the-detection-of-earnings-manipulation
- Streamlit: https://docs.streamlit.io/ — hướng dẫn chạy, triển khai và kiểm thử ứng dụng.
