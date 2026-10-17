from datetime import datetime
from pathlib import Path
from copy import deepcopy
import re
import pandas as pd
import streamlit as st
from engine import FIELDS, blank, demo, calculate
from file_io import export_workbook, import_workbook

st.set_page_config(page_title='StockAI | Phân tích BCTC',page_icon='📊',layout='wide')
st.markdown('''<style>.block-container{max-width:1200px;padding-top:2rem}h1,h2,h3{color:#123047}div[data-testid="stMetric"]{background:#eef5f7;padding:16px;border-radius:12px}.stButton>button{border-radius:8px} </style>''',unsafe_allow_html=True)
if 'data' not in st.session_state:st.session_state.data=blank()
if 'revision' not in st.session_state:st.session_state.revision=0

def replace(data):
 st.session_state.data=deepcopy(data);st.session_state.revision+=1

st.sidebar.title('NHÀ ĐẦU TƯ\nTHÔNG THÁI')
st.sidebar.caption('Công cụ đọc hiểu BCTC • Phiên bản 1.0')
page=st.sidebar.radio('Chức năng',['Phân tích BCTC','Vĩ mô thủ công','Hướng dẫn'])
st.sidebar.info('Dùng ngay, không cần tài khoản. Phiên làm việc không phải nơi lưu lâu dài; hãy tải Excel trước khi thoát.')
if page=='Phân tích BCTC':
 st.title('Phân tích chất lượng tài chính')
 st.caption('Nhập dữ liệu có nguồn • Xem từng phép tính • Tải về để lưu và dùng tiếp')
 with st.expander('Bắt đầu: dữ liệu mới, minh họa hoặc nhập Excel',expanded=True):
  c1,c2,c3=st.columns(3)
  with c1:
   if st.button('Tạo bản mới',width='stretch'):replace(blank());st.rerun()
  with c2:
   if st.button('Nạp dữ liệu minh họa',width='stretch'):replace(demo());st.rerun()
  with c3:
   template=Path(__file__).parent/'Mau_nhap_BCTC.xlsx'
   if template.exists():st.download_button('Tải mẫu Excel trống',template.read_bytes(),'Mau_nhap_BCTC.xlsx',width='stretch')
   else:st.download_button('Tải mẫu Excel trống',export_workbook(blank()),'Mau_nhap_BCTC.xlsx',width='stretch')
  uploaded=st.file_uploader('Nhập mẫu Excel hoặc bản đã tải trước đó (.xlsx, tối đa 5 MB)',type=['xlsx'])
  if st.button('Áp dụng tệp Excel',disabled=uploaded is None):
   try:
    replace(import_workbook(uploaded.getvalue()));st.rerun()
   except Exception as exc:st.error(f'Không nhập được tệp: {exc}')
 d=st.session_state.data;m=d['meta'];rev=st.session_state.revision
 def key(name):return f'{rev}_{name}'
 st.subheader('1. Thông tin báo cáo')
 a,b,c=st.columns(3)
 m['ticker']=a.text_input('Mã cổ phiếu / doanh nghiệp',value=m['ticker'],max_chars=20,key=key('ticker')).strip().upper()
 m['year']=b.number_input('Năm báo cáo t',min_value=1990,max_value=2100,value=m['year'],key=key('year'))
 units=['VND','Nghìn VND','Triệu VND','Tỷ VND'];m['unit']=c.selectbox('Đơn vị toàn bộ số tiền',units,index=units.index(m['unit']),key=key('unit'))
 a,b=st.columns(2)
 scopes=['Hợp nhất','Riêng lẻ'];m['scope']=a.selectbox('Phạm vi báo cáo',scopes,index=scopes.index(m['scope']),key=key('scope'))
 sectors=['Doanh nghiệp phi tài chính','Ngân hàng / Bảo hiểm / Chứng khoán'];m['sector']=b.selectbox('Nhóm doanh nghiệp',sectors,index=sectors.index(m['sector']),key=key('sector'))
 m['source']=st.text_area('Nguồn BCTC, link và số trang/thuyết minh',value=m['source'],max_chars=2000,key=key('source'))
 m['demo']=st.checkbox('Bộ dữ liệu minh họa / chưa phải số liệu thực tế',value=m['demo'],key=key('demo'))
 if m['demo']:st.warning('DỮ LIỆU MINHỌA — không phải kết quả phân tích một cổ phiếu thực.')
 st.subheader('2. Số liệu hai năm và tài sản đầu kỳ')
 st.caption('Để trống nếu chưa biết. Số 0 có nghĩa bạn đã kiểm tra và khoản mục bằng 0. Nhập số trực tiếp, không gõ dấu phân cách hàng nghìn. Chi phí nhập dương; LNST và CFO có thể âm.')
 tabs=st.tabs([f'Năm t: {m["year"]}',f'Năm t−1: {m["year"]-1}',f'Tài sản t−2: {m["year"]-2}'])
 for index,y in enumerate(['t','t1','t2']):
  with tabs[index]:
   fields=list(FIELDS) if y!='t2' else ['assets']
   left,right=st.columns(2)
   for i,k in enumerate(fields):
    with (left if i%2==0 else right):
     old=d['periods'][y].get(k)
     d['periods'][y][k]=st.number_input(FIELDS[k][0],value=float(old) if old is not None else None,format='%.4f',help=FIELDS[k][1],key=key(f'{y}_{k}'))
 st.subheader('3. Kiểm tra thuyết minh')
 choices=['Chưa xác định','Không','Có'];m['issuance']=st.selectbox('Có phát hành thêm cổ phần phổ thông để huy động vốn trong năm t?',choices,index=choices.index(m['issuance']),key=key('issuance'),help='Không kết luận chỉ từ thay đổi số cổ phiếu. Chia tách/cổ tức cổ phiếu không đồng nghĩa phát hành huy động vốn.')
 m['f_income_proxy']=st.checkbox('F-Score: đang dùng LNST thay lợi nhuận trước khoản bất thường',value=m['f_income_proxy'],key=key('fp'))
 m['m_income_proxy']=st.checkbox('M-Score: đang dùng LNST thay lợi nhuận hoạt động tiếp tục',value=m['m_income_proxy'],key=key('mp'))
 if st.button('Sao chép LNST năm t sang lợi nhuận hoạt động tiếp tục (bản xấp xỉ)'):
  d['periods']['t']['continuing_income']=d['periods']['t']['income'];m['m_income_proxy']=True;replace(d);st.rerun()
 st.subheader('4. Kết quả cập nhật theo đầu vào')
 result=calculate(d)
 for msg in result['errors']:st.error(msg)
 for msg in result['warnings']:st.warning(msg)
 f=result['f_score'];ms=result['m_score']
 a,b=st.columns(2)
 a.metric('F-Score' + (' (điều chỉnh)' if m['f_income_proxy'] else ''),f'{f}/9' if f is not None else 'Chưa đủ dữ liệu')
 b.metric('M-Score 8 biến' + (' (xấp xỉ)' if m['m_income_proxy'] else ''),f'{ms:.3f}' if ms is not None else 'Chưa tính được')
 if f is not None:
  st.info('F-Score đếm số tín hiệu thuận lợi. Điểm cao hơn có nhiều tiêu chí đạt hơn; không thay thế định giá, triển vọng hay kiểm tra ngành.')
 if result['f_rows']:
  st.markdown('**Chín tiêu chí F-Score**');st.dataframe(pd.DataFrame(result['f_rows']),hide_index=True,width='stretch')
  known=[r['Điểm'] for r in result['f_rows'] if r['Điểm'] is not None]
  if f is None:st.caption(f'Đã tính {len(known)}/9 tiêu chí. Không cộng điểm một phần thành F-Score hoàn chỉnh.')
 if result['m_rows']:
  st.markdown('**Tám biến Beneish M-Score**');st.dataframe(pd.DataFrame(result['m_rows']),hide_index=True,width='stretch')
  st.caption('M = −4,84 + 0,920 DSRI + 0,528 GMI + 0,404 AQI + 0,892 SGI + 0,115 DEPI − 0,172 SGAI − 0,327 LVGI + 4,679 TATA.')
 if ms is not None:
  st.info('M-Score là chỉ báo sàng lọc dấu hiệu thao túng lợi nhuận. Bản này hiển thị số và phép tính, không tự gắn nhãn gian lận hay xác suất; chưa hiệu chuẩn ngưỡng cho dữ liệu Việt Nam.')
 st.subheader('5. Lưu để dùng tiếp')
 st.caption('Tệp Excel gồm dữ liệu nhập, nguồn, thông tin báo cáo và bảng kết quả tại thời điểm tải. Có thể nhập lại tệp để tiếp tục; Excel không tự tính lại khi bạn sửa số trong tệp.')
 safe_name=re.sub(r'[^A-Z0-9_-]','',m['ticker']) or 'CHUA_DAT_MA'
 st.download_button('Tải dữ liệu + kết quả Excel',export_workbook(d,result),f'{safe_name}_{m["year"]}_phan_tich.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',type='primary')
elif page=='Vĩ mô thủ công':
 st.title('Bảng theo dõi vĩ mô thủ công')
 st.caption('Quy tắc tham khảo do người dùng nhập; không tự lấy dữ liệu hoặc dự báo thị trường.')
 source=st.text_area('Nguồn, ngày số liệu và ghi chú',key='macro_source')
 choices=['Chưa chọn','Thuận lợi','Trung tính','Bất lợi']
 labels=['Lãi suất và thanh khoản','Tỷ giá USD/VND','Sức mạnh USD (DXY)','Điều hành tiền tệ']
 values=[st.selectbox(x,choices,key=f'macro_{i}') for i,x in enumerate(labels)]
 if 'Chưa chọn' in values:st.info('Chọn đủ bốn yếu tố để xem tổng hợp.')
 else:
  status='Có yếu tố bất lợi' if 'Bất lợi' in values else 'Các yếu tố cùng thuận lợi' if all(v=='Thuận lợi' for v in values) else 'Các yếu tố chưa đồng thuận'
  st.info(status+'. Cần kiểm chứng dữ liệu, kết hợp định giá và mức chịu rủi ro; không quy đổi thành khuyến nghị all-in hoặc tỷ lệ tiền mặt cố định.')
  report='ĐÁNH GIÁ VĨ MÔ THỦ CÔNG\n'+ '\n'.join(f'{k}: {v}' for k,v in zip(labels,values))+'\nTổng hợp: '+status+'\nNguồn/ghi chú: '+source
  st.download_button('Tải ghi chú vĩ mô',report.encode('utf-8-sig'),'ghi_chu_vi_mo.txt')
else:
 st.title('Hướng dẫn sử dụng')
 st.markdown((Path(__file__).parent/'HUONG_DAN.md').read_text(encoding='utf-8'))
st.divider();st.caption('StockAI 1.0 • Công cụ hỗ trợ đọc BCTC. Dữ liệu do người dùng cung cấp, chưa được đối chiếu tự động với báo cáo gốc.')
