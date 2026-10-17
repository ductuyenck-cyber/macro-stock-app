# Kiểm thử bản 1.0

- 15 kiểm thử tính điểm và nhập/xuất Excel: đã qua.
- Streamlit AppTest: khởi động bản trống, nạp minh họa, F=4/9 và M=-2.57358, sửa mẫu số thành 0, chuyển chức năng, cập nhật nhận định vĩ mô, mở hướng dẫn, tạo lại bản trống: đã qua.
- Mẫu Excel trống: đã xem bản render hai sheet và kiểm tra nhập vào ứng dụng thành công.
- Cú pháp các mô-đun Python: đã qua.

Chạy lại từ thư mục dự án: python -m unittest discover -s tests -v
Môi trường kiểm thử dùng Streamlit 1.66.0. Requirements cho phép từ 1.50 đến trước 2.0; không khẳng định đã thử mọi phiên bản trong khoảng này.
Chưa chạy tệp BAT trên máy Windows của người dùng hoặc triển khai lên tài khoản Streamlit Cloud của người dùng. AppTest không thay thế kiểm tra bố cục trên từng kích thước màn hình.
Không đối chiếu với một BCTC thực trong phiên bản kiểm thử này; dữ liệu minh họa được thiết kế để tự tính lại bằng tay.
