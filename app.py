# StockAI Độc lập 1.1 — all application code in one file.
from datetime import datetime
from pathlib import Path
from copy import deepcopy
import re
import pandas as pd
import streamlit as st
"""Pure calculation engine. Missing input is None, never an implicit zero."""
import math

FIELDS = {
 'sales': ('Doanh thu thuần', 'Báo cáo KQKD: doanh thu thuần, không dùng tổng doanh thu.'),
 'receivables': ('Phải thu khách hàng thuần', 'Chỉ phải thu khách hàng; dùng nhất quán sau dự phòng cho hai năm.'),
 'cogs': ('Giá vốn hàng bán', 'Nhập số dương; không nhập dấu âm theo cách trình bày của BCTC.'),
 'current_assets': ('Tài sản ngắn hạn', 'Bảng cân đối kế toán: tổng tài sản ngắn hạn.'),
 'ppe': ('TSCĐ hữu hình còn lại', 'Nguyên giá trừ hao mòn lũy kế; không cộng BĐS đầu tư, XDCB dở dang, đầu tư tài chính.'),
 'depreciation': ('Khấu hao TSCĐ hữu hình trong năm', 'Đọc thuyết minh, khớp phạm vi PP&E. Không dùng hao mòn lũy kế.'),
 'sga': ('Chi phí bán hàng + quản lý', 'Cộng chi phí bán hàng và chi phí quản lý doanh nghiệp, nhập số dương.'),
 'long_liabilities': ('Tổng nợ phải trả dài hạn', 'Dùng cho LVGI của M-Score, không chỉ vay dài hạn.'),
 'current_liabilities': ('Tổng nợ ngắn hạn', 'Bảng cân đối kế toán: tổng nợ ngắn hạn.'),
 'income': ('LNST dùng cho F-Score', 'Dùng nhất quán lợi nhuận toàn doanh nghiệp. Mô hình gốc dùng lợi nhuận trước khoản bất thường.'),
 'continuing_income': ('Lợi nhuận hoạt động tiếp tục sau thuế', 'Dùng cho TATA. Nếu dùng LNST thay thế, phải đánh dấu xấp xỉ ở thông tin báo cáo.'),
 'cfo': ('Lưu chuyển tiền thuần từ HĐKD', 'Lưu chuyển tiền tệ: dòng tiền thuần từ hoạt động kinh doanh; có thể âm.'),
 'assets': ('Tổng tài sản cuối năm', 'Cần thêm giá trị cuối t-2 để tính ROA/vòng quay đầu kỳ.'),
 'long_debt': ('Vay dài hạn gồm phần đến hạn trả', 'Dùng cho F-Score. Gồm phần vay dài hạn tái phân loại vào nợ ngắn hạn; không dùng toàn bộ nợ phải trả dài hạn.'),
}
YEARS = ('t','t1','t2')
WEIGHTS = {'DSRI': .920, 'GMI': .528, 'AQI': .404, 'SGI': .892, 'DEPI': .115, 'SGAI': -.172, 'LVGI': -.327, 'TATA': 4.679}

def blank():
 return {'meta': {'ticker':'', 'year':2025, 'unit':'Triệu VND', 'scope':'Hợp nhất', 'sector':'Doanh nghiệp phi tài chính', 'source':'', 'issuance':'Chưa xác định', 'f_income_proxy':True, 'm_income_proxy':True, 'demo':False}, 'periods':{y:{k:None for k in FIELDS} for y in YEARS}}

def demo():
 d=blank();d['meta'].update(ticker='DEMO',source='Dữ liệu giả lập để học; không phải số liệu doanh nghiệp.',issuance='Không',demo=True)
 for y in ['t','t1']:
  d['periods'][y].update(sales=100.,receivables=10.,cogs=60.,current_assets=40.,ppe=30.,depreciation=5.,sga=10.,long_liabilities=20.,current_liabilities=20.,income=10.,continuing_income=10.,cfo=12.,assets=100.,long_debt=20.)
 d['periods']['t2']['assets']=100.
 return d

def calculate(data):
 errors=[]; warnings=[]; p=data['periods']; meta=data['meta']
 for y in YEARS:
  for k in FIELDS:
   v=p[y].get(k)
   if v is not None and (isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v)):
    errors.append(f'{y}: {FIELDS[k][0]} phải là số hữu hạn.'); continue
   if v is not None and k not in ('income','continuing_income','cfo') and v<0:
    errors.append(f'{y}: {FIELDS[k][0]} không được âm.')
  for k in ['assets','sales']:
   if p[y].get(k) is not None and p[y][k]<=0: errors.append(f'{y}: {FIELDS[k][0]} phải lớn hơn 0.')
  ca,pp,ta=(p[y].get(k) for k in ['current_assets','ppe','assets'])
  if all(v is not None for v in [ca,pp,ta]) and ca+pp>ta+max(1,abs(ta))*1e-9: errors.append(f'{y}: tài sản ngắn hạn + PP&E vượt tổng tài sản.')
  rec=p[y].get('receivables')
  if rec is not None and ca is not None and rec>ca: warnings.append(f'{y}: phải thu vượt tài sản ngắn hạn; kiểm tra có cộng phải thu dài hạn không.')
  ll,cl=p[y].get('long_liabilities'),p[y].get('current_liabilities')
  if all(v is not None for v in [ll,cl,ta]) and ll+cl>ta: warnings.append(f'{y}: nợ vượt tài sản, có thể vốn chủ âm; cần kiểm tra.')
 if meta.get('demo'): warnings.append('Đang dùng dữ liệu minh họa, không phải số liệu cổ phiếu thực.')
 if not str(meta.get('source','')).strip(): warnings.append('Chưa ghi nguồn BCTC và trang/thuyết minh.')
 if meta.get('f_income_proxy'): warnings.append('F-Score dùng LNST thay lợi nhuận trước khoản bất thường: bản điều chỉnh cần đối chiếu thuyết minh.')
 if meta.get('m_income_proxy'): warnings.append('TATA dùng LNST thay lợi nhuận hoạt động tiếp tục: M-Score xấp xỉ.')
 out={'errors':errors,'warnings':warnings,'f_rows':[],'m_rows':[], 'f_score':None,'m_score':None}
 if errors:return out
 if meta.get('sector') != 'Doanh nghiệp phi tài chính':
  errors.append('Mô hình này không chấm ngân hàng, bảo hiểm, công ty chứng khoán.');return out
 def get(y,k):
  v=p[y].get(k)
  if v is None:raise ValueError(f'Thiếu {FIELDS[k][0]} ({y}).')
  return v
 def div(a,b,label):
  if b==0:raise ValueError(f'{label}: mẫu số bằng 0.')
  return a/b
 def ratio(y,n,d):return div(get(y,n),get(y,d),FIELDS[n][0]+'/'+FIELDS[d][0])
 def margin(y):return div(get(y,'sales')-get(y,'cogs'),get(y,'sales'),'Biên lợi nhuận gộp')
 def avg(y,prev):return (get(y,'assets')+get(prev,'assets'))/2
 def issuance():
  val=meta.get('issuance')
  if val not in ['Có','Không']:raise ValueError('Chưa xác định phát hành cổ phần huy động vốn.')
  return (1 if val=='Không' else 0,1,'Không = đạt; Có = không đạt')
 # Each criterion returns observed current/prior value; no missing -> false conversion.
 criteria=[
  ('LNST dương',lambda:(get('t','income'),0,'LNST > 0'),lambda a,b:a>b),
  ('CFO dương',lambda:(get('t','cfo'),0,'CFO > 0'),lambda a,b:a>b),
  ('ROA tăng',lambda:(div(get('t','income'),get('t1','assets'),'ROA t'),div(get('t1','income'),get('t2','assets'),'ROA t-1'),'LN / tài sản đầu kỳ; t > t-1'),lambda a,b:a>b),
  ('CFO lớn hơn LNST',lambda:(get('t','cfo'),get('t','income'),'CFO > LNST'),lambda a,b:a>b),
  ('Đòn bẩy giảm',lambda:(div(get('t','long_debt'),avg('t','t1'),'Đòn bẩy t'),div(get('t1','long_debt'),avg('t1','t2'),'Đòn bẩy t-1'),'Vay dài hạn / tài sản bình quân; t < t-1'),lambda a,b:a<b),
  ('Thanh toán hiện hành tăng',lambda:(ratio('t','current_assets','current_liabilities'),ratio('t1','current_assets','current_liabilities'),'CA / CL; t > t-1'),lambda a,b:a>b),
  ('Không phát hành huy động vốn',issuance,lambda a,b:a==b),
  ('Biên lợi nhuận gộp tăng',lambda:(margin('t'),margin('t1'),'(Doanh thu − giá vốn)/doanh thu; t > t-1'),lambda a,b:a>b),
  ('Vòng quay tài sản tăng',lambda:(div(get('t','sales'),get('t1','assets'),'Vòng quay t'),div(get('t1','sales'),get('t2','assets'),'Vòng quay t-1'),'Doanh thu / tài sản đầu kỳ; t > t-1'),lambda a,b:a>b)]
 for name,fn,predicate in criteria:
  try:
   a,b,rule=fn(); point=int(predicate(a,b)); row={'Tiêu chí':name,'Điểm':point,'Giá trị t':a,'Đối chiếu':b,'Quy tắc / Lý do':rule}
  except ValueError as exc:row={'Tiêu chí':name,'Điểm':None,'Giá trị t':None,'Đối chiếu':None,'Quy tắc / Lý do':str(exc)}
  out['f_rows'].append(row)
 if all(r['Điểm'] is not None for r in out['f_rows']):out['f_score']=sum(r['Điểm'] for r in out['f_rows'])
 def rel(n,d,label):return div(ratio('t',n,d),ratio('t1',n,d),label)
 def gmi():
  a,b=margin('t1'),margin('t')
  if min(a,b)<=0:raise ValueError('Biên lợi nhuận gộp không dương; không diễn giải GMI theo mô hình thông thường.')
  return div(a,b,'GMI')
 def quality(y):return 1-div(get(y,'current_assets')+get(y,'ppe'),get(y,'assets'),'AQI')
 def dep(y):return div(get(y,'depreciation'),get(y,'ppe')+get(y,'depreciation'),'DEPI')
 def lev(y):return div(get(y,'long_liabilities')+get(y,'current_liabilities'),get(y,'assets'),'LVGI')
 funcs={
  'DSRI':lambda:rel('receivables','sales','DSRI'), 'GMI':gmi,
  'AQI':lambda:div(quality('t'),quality('t1'),'AQI'),
  'SGI':lambda:div(get('t','sales'),get('t1','sales'),'SGI'),
  'DEPI':lambda:div(dep('t1'),dep('t'),'DEPI'),
  'SGAI':lambda:rel('sga','sales','SGAI'),
  'LVGI':lambda:div(lev('t'),lev('t1'),'LVGI'),
  'TATA':lambda:div(get('t','continuing_income')-get('t','cfo'),get('t','assets'),'TATA')}
 for name,fn in funcs.items():
  try:
   val=fn()
   if not math.isfinite(val):raise ValueError('Kết quả không hữu hạn.')
   row={'Biến':name,'Giá trị':val,'Hệ số':WEIGHTS[name],'Đóng góp':val*WEIGHTS[name],'Lý do':''}
  except ValueError as exc:row={'Biến':name,'Giá trị':None,'Hệ số':WEIGHTS[name],'Đóng góp':None,'Lý do':str(exc)}
  out['m_rows'].append(row)
 if all(r['Giá trị'] is not None for r in out['m_rows']):out['m_score']=-4.84+sum(r['Đóng góp'] for r in out['m_rows'])
 return out

"""Workbook interchange used by the application at runtime."""
from io import BytesIO
import math
from zipfile import ZipFile, BadZipFile
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment


BOOL_KEYS={'demo','f_income_proxy','m_income_proxy'}
def safe_text(v):
 return "'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v

def format_sheet(ws):
 ws.freeze_panes='C2';ws.auto_filter.ref=ws.dimensions
 for cell in ws[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='123047')
 for col in ws.columns:
  letter=col[0].column_letter;ws.column_dimensions[letter].width=min(65,max(16,max(len(str(c.value or '')) for c in col)+2))
 for row in ws.iter_rows(min_row=2):
  for cell in row:
   cell.alignment=Alignment(vertical='top',wrap_text=True)
   if isinstance(cell.value,(int,float)):cell.number_format='#,##0.000;[Red](#,##0.000);0'
  ws.row_dimensions[row[0].row].height=32

def export_workbook(data, result=None):
 wb=Workbook();ws=wb.active;ws.title='Du_lieu'
 ws.append(['field','Chỉ tiêu','t','t1','t2','Hướng dẫn'])
 for key,(label,help_) in FIELDS.items():ws.append([key,label,*[data['periods'][y].get(key) for y in YEARS],help_])
 meta=wb.create_sheet('Thong_tin');meta.append(['key','value'])
 for k,v in data['meta'].items():meta.append([k,safe_text(v)])
 if result is not None:
  summary=wb.create_sheet('Ket_qua');summary.append(['Chỉ số','Giá trị / ghi chú'])
  summary.append(['F-Score',result['f_score']]);summary.append(['M-Score',result['m_score']]);summary.append(['Bản tính','Ảnh chụp kết quả; nhập lại vào ứng dụng để tính khi thay số.'])
  for v in result['errors']+result['warnings']:summary.append(['Lưu ý',safe_text(v)])
  for title,key in [('F_Score','f_rows'),('M_Score','m_rows')]:
   sh=wb.create_sheet(title);rows=result[key]
   if rows:
    sh.append(list(rows[0]));
    for row in rows:sh.append([safe_text(v) for v in row.values()])
 for sh in wb:format_sheet(sh)
 out=BytesIO();wb.save(out);return out.getvalue()

def import_workbook(content):
 if len(content)>5*1024*1024:raise ValueError('Tệp vượt 5 MB.')
 try:
  with ZipFile(BytesIO(content)) as z:
   if sum(i.file_size for i in z.infolist())>25*1024*1024:raise ValueError('Nội dung giải nén vượt 25 MB.')
  wb=load_workbook(BytesIO(content),read_only=True,data_only=False)
 except (BadZipFile, OSError, KeyError) as exc:raise ValueError('Không đọc được XLSX. Dùng mẫu tải từ ứng dụng.') from exc
 try:
  if not {'Du_lieu','Thong_tin'}.issubset(wb.sheetnames):raise ValueError('Cần hai sheet Du_lieu và Thong_tin.')
  ws=wb['Du_lieu'];ms=wb['Thong_tin']
  for sheet in (ws,ms):
   if sheet.max_row is None or sheet.max_column is None:sheet.calculate_dimension(force=True)
  if ws.max_row>100 or ws.max_column>10 or ms.max_row>40 or ms.max_column>5:raise ValueError('Cấu trúc tệp quá lớn; dùng mẫu gốc.')
  rows=list(ws.values)
  if list(rows[0][:5]) != ['field','Chỉ tiêu','t','t1','t2']:raise ValueError('Không đổi tên 5 cột đầu trong Du_lieu.')
  d=blank();seen=set()
  for row in rows[1:]:
   key=row[0]
   if not key:continue
   if key not in FIELDS or key in seen:raise ValueError(f'field lạ hoặc trùng: {key}')
   seen.add(key)
   for i,y in enumerate(YEARS,2):
    value=row[i] if i<len(row) else None
    if value in (None,''):value=None
    elif isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError(f'{key}/{y}: nhập số Excel, không nhập công thức hoặc số dạng chữ.')
    d['periods'][y][key]=value
  if seen != set(FIELDS):raise ValueError('Thiếu dòng chỉ tiêu; dùng mẫu đầy đủ.')
  if list(next(ms.values)[:2])!=['key','value']:raise ValueError('Thong_tin cần cột key,value.')
  seen_meta=set()
  for row in list(ms.values)[1:]:
   key,value=row[:2]
   if not key:continue
   if key not in d['meta'] or key in seen_meta:raise ValueError(f'Thông tin lạ hoặc trùng: {key}')
   seen_meta.add(key)
   if key in BOOL_KEYS:
    if value is None:value=d['meta'][key]
    if not isinstance(value,bool):raise ValueError(f'{key}: dùng TRUE hoặc FALSE.')
   elif key=='year':
    if isinstance(value,bool) or not isinstance(value,(int,float)) or int(value)!=value or not 1990<=value<=2100:raise ValueError('Năm báo cáo phải là số nguyên 1990–2100.')
    value=int(value)
   else:
    if value is not None and not isinstance(value,str):raise ValueError(f'{key}: cần văn bản.')
    value=value or ''
    if value.startswith('='):raise ValueError('Không dùng công thức trong Thong_tin.')
   d['meta'][key]=value
  choices={'scope':['Hợp nhất','Riêng lẻ'],'unit':['VND','Nghìn VND','Triệu VND','Tỷ VND'],'sector':['Doanh nghiệp phi tài chính','Ngân hàng / Bảo hiểm / Chứng khoán'],'issuance':['Có','Không','Chưa xác định']}
  for k,values in choices.items():
   if d['meta'][k] not in values:raise ValueError(f'{k}: giá trị không hợp lệ.')
  if len(d['meta']['ticker'])>20 or len(d['meta']['source'])>2000:raise ValueError('Mã hoặc nguồn quá dài.')
  return d
 finally:wb.close()

# Sector-specific financial analysis. Annual data only, no synthetic total score.
FIN_COMMON={
 'assets':('Tổng tài sản cuối năm','Tổng tài sản cùng phạm vi với LNST.'),
 'equity':('Vốn chủ sở hữu cuối năm','Tổng vốn chủ sở hữu, không chỉ vốn của cổ đông mẹ nếu dùng LNST toàn tập đoàn.'),
 'net_income':('LNST toàn doanh nghiệp','Không trộn LNST cổ đông mẹ với tổng vốn/tài sản hợp nhất.'),
 'pretax_income':('Lợi nhuận trước thuế','Báo cáo KQKD năm, có thể âm.'),
 'price':('Giá cổ phiếu (VND/cp)','Giá nhập tay, đơn vị VND/cp dù số liệu BCTC dùng triệu/tỷ. Ghi ngày giá và nguồn.'),
 'eps':('EPS cơ bản năm (VND/cp)','EPS cơ bản đã công bố hoặc đã điều chỉnh nhất quán; không dùng LNST/số cổ phiếu cuối kỳ để thay EPS.'),
 'bvps':('BVPS (VND/cp)','Giá trị sổ sách cổ phần phổ thông sau loại lợi ích không kiểm soát/cổ phần ưu đãi nếu có. Dùng nguồn đã đối chiếu.')}
BANK_FIELDS={**FIN_COMMON,
 'loans':('Cho vay khách hàng gộp cuối năm','Trước dự phòng; cùng phạm vi với nợ nhóm 2 và nợ xấu.'),
 'npl':('Nợ xấu nhóm 3–5','Cộng nhóm 3,4,5 từ thuyết minh phân loại nợ; cùng mẫu số cho vay khách hàng.'),
 'group2':('Nợ cần chú ý nhóm 2','Không gộp vào nợ xấu nhóm 3–5.'),
 'loan_reserves':('Dự phòng rủi ro cho vay khách hàng','Số dư dự phòng cho khoản cho vay khách hàng cuối năm, nhập dương. Không cộng dự phòng chứng khoán/cam kết không cùng phạm vi.'),
 'deposits':('Tiền gửi khách hàng cuối năm','Không gồm tiền gửi/vay tổ chức tín dụng.'),
 'demand_deposits':('Tiền gửi không kỳ hạn khách hàng','Cùng phạm vi tiền gửi khách hàng để tính CASA.'),
 'net_interest':('Thu nhập lãi thuần trong năm','Báo cáo KQKD: thu nhập lãi và các khoản tương tự trừ chi phí lãi.'),
 'earning_assets':('Tài sản sinh lãi cuối năm','Xác định theo thuyết minh/IR, cùng định nghĩa hai năm. Không tự dùng tổng tài sản thay thế.'),
 'operating_income':('Tổng thu nhập hoạt động thuần (TOI)','Thu nhập lãi thuần cộng các khoản thu nhập ngoài lãi thuần; trước chi phí hoạt động và dự phòng.'),
 'operating_cost':('Chi phí hoạt động trong năm','Nhập dương; không cộng chi phí lãi hoặc chi phí dự phòng.'),
 'credit_cost':('Chi phí dự phòng tín dụng cho vay ròng','Chi phí trong kỳ trừ hoàn nhập, có thể âm. Cần cùng phạm vi cho vay khách hàng; không dùng tổng chi phí dự phòng nếu gồm tài sản khác.'),
 'car_reported':('CAR công bố (%)','Nhập 12.5 nếu CAR = 12,5%. Lấy từ công bố an toàn vốn, không suy ra từ vốn chủ/tài sản.'),
 'nim_reported':('NIM công bố (%) — nếu có','Nhập 3.2 nếu NIM = 3,2%. Chỉ đối chiếu khi cùng kỳ và cùng phạm vi; có thể dùng bình quân tháng/ngày khác cách 2 mốc trong công cụ.')}
BROKER_FIELDS={**FIN_COMMON,
 'liabilities':('Tổng nợ phải trả cuối năm','Không đồng nhất với nợ vay chịu lãi; không tự suy ra giới hạn pháp lý.'),
 'borrowings':('Tổng vay chịu lãi cuối năm','Vay ngắn hạn + dài hạn cùng phạm vi; không cộng tiền của nhà đầu tư.'),
 'margin_loans':('Dư nợ cho vay ký quỹ cuối năm','Chỉ cho vay margin, không cộng ứng trước nếu thu nhập margin không gồm ứng trước.'),
 'margin_income':('Thu nhập lãi cho vay ký quỹ năm','Chỉ lãi margin khớp dư nợ; không dùng toàn bộ thu nhập tiền gửi/cho vay.'),
 'operating_revenue':('Doanh thu hoạt động năm','Theo KQKD công ty chứng khoán, cùng cách phân loại hai năm; không nhầm với lợi nhuận thuần hoạt động.'),
 'brokerage_revenue':('Doanh thu môi giới năm','Doanh thu môi giới, không phải lợi nhuận môi giới.'),
 'fvtpl_gains':('Lãi tài sản FVTPL trong năm','Lãi ghi nhận trên KQKD, có thể gồm lãi đánh giá lại. Nhập dương.'),
 'fvtpl_losses':('Lỗ tài sản FVTPL trong năm','Nhập trị tuyệt đối dương, gồm phần lỗ theo cùng phạm vi với lãi FVTPL.'),
 'fvtpl_assets':('Tài sản FVTPL cuối năm','Giá trị ghi sổ cuối kỳ, không đồng nghĩa chỉ cổ phiếu.'),
 'liquid_assets':('Tiền và tiền gửi ngắn hạn của công ty','Chỉ nguồn tiền thuộc công ty, không cộng tiền khách hàng. Không coi FVTPL là tiền.'),
 'current_liabilities':('Tổng nợ ngắn hạn cuối năm','Dùng chỉ báo bao phủ tiền đơn giản, không phải kiểm tra thanh khoản pháp lý.'),
 'capital_ratio_reported':('Tỷ lệ vốn khả dụng công bố (%)','Nhập 250 nếu tỷ lệ = 250%. Lấy Báo cáo tỷ lệ an toàn tài chính; không suy ra từ BCTC hợp nhất.')}
FIN_FIELDS={'bank':BANK_FIELDS,'broker':BROKER_FIELDS}
FIN_NAMES={'bank':'Ngân hàng','broker':'Công ty chứng khoán'}
SIGNED_FIN={'equity','net_income','pretax_income','net_interest','operating_income','credit_cost','eps','bvps','nim_reported','car_reported','capital_ratio_reported'}

def financial_blank(kind):
 return {'kind':kind,'meta':{'ticker':'','year':2025,'unit':'Triệu VND','scope':'Hợp nhất','source':'','capital_source':'','price_source':'','demo':False},
 'periods':{y:{k:None for k in FIN_FIELDS[kind]} for y in YEARS}}

def financial_demo(kind):
 d=financial_blank(kind);d['meta'].update(ticker='DEMO',source='Dữ liệu giả lập, không phải số liệu doanh nghiệp.',demo=True)
 for y in ['t','t1']:
  d['periods'][y].update(assets=1000.,equity=100.,net_income=20.,pretax_income=25.,price=30000.,eps=3000.,bvps=20000.)
 if kind=='bank':
  for y in ['t','t1']:d['periods'][y].update(loans=600.,npl=12.,group2=6.,loan_reserves=18.,deposits=700.,demand_deposits=140.,net_interest=32.,earning_assets=800.,operating_income=50.,operating_cost=20.,credit_cost=6.,car_reported=12.,nim_reported=4.)
 else:
  for y in ['t','t1']:d['periods'][y].update(liabilities=900.,borrowings=700.,margin_loans=150.,margin_income=15.,operating_revenue=100.,brokerage_revenue=30.,fvtpl_gains=40.,fvtpl_losses=10.,fvtpl_assets=200.,liquid_assets=100.,current_liabilities=500.,capital_ratio_reported=250.)
 for k in ['assets','equity']+(['loans','earning_assets'] if kind=='bank' else ['margin_loans']):d['periods']['t2'][k]=d['periods']['t1'][k]
 return d

def financial_calculate(d):
 kind=d['kind'];fields=FIN_FIELDS[kind];p=d['periods'];errors=[];notes=[]
 for y in YEARS:
  for k,v in p[y].items():
   if k not in fields:errors.append(f'{y}: chỉ tiêu không được hỗ trợ.');continue
   if v is None:continue
   if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):errors.append(f'{y}: {fields[k][0]} phải là số hữu hạn.');continue
   if k not in SIGNED_FIN and v<0:errors.append(f'{y}: {fields[k][0]} không được âm.')
   if k=='assets' and v<=0:errors.append(f'{y}: tổng tài sản phải > 0.')
  def compare(part,total,label):
   a,b=p[y].get(part),p[y].get(total)
   if isinstance(a,(int,float)) and isinstance(b,(int,float)) and a>b+max(abs(b),1)*1e-8:errors.append(f'{y}: {label}.')
  if isinstance(p[y].get('equity'),(int,float)) and p[y]['equity']<=0:notes.append(f'{y}: vốn chủ sở hữu không dương; không diễn giải ROE/đòn bẩy như trường hợp vốn chủ dương.')
  if kind=='bank':
   compare('npl','loans','Nợ xấu vượt cho vay khách hàng');compare('group2','loans','Nợ nhóm 2 vượt cho vay khách hàng');compare('demand_deposits','deposits','Tiền gửi không kỳ hạn vượt tiền gửi khách hàng')
   a,b,c=(p[y].get(k) for k in ['npl','group2','loans'])
   if all(isinstance(v,(int,float)) for v in [a,b,c]) and a+b>c:errors.append(f'{y}: nợ nhóm 2 cộng nhóm 3–5 vượt cho vay khách hàng.')
  else:
   compare('borrowings','liabilities','Nợ vay vượt tổng nợ phải trả');compare('margin_loans','assets','Cho vay ký quỹ vượt tổng tài sản');compare('fvtpl_assets','assets','Tài sản FVTPL vượt tổng tài sản');compare('liquid_assets','assets','Tiền và tiền gửi vượt tổng tài sản');compare('current_liabilities','liabilities','Nợ ngắn hạn vượt tổng nợ')
   a,b,c=(p[y].get(k) for k in ['assets','equity','liabilities'])
   if all(isinstance(v,(int,float)) for v in [a,b,c]) and abs(a-b-c)>max(abs(a),1)*.005:notes.append(f'{y}: tổng tài sản không khớp vốn chủ + nợ (chênh > 0,5%); kiểm tra phạm vi/đơn vị.')
 if d['meta'].get('demo'):notes.append('Dữ liệu minh họa — không đại diện cho cổ phiếu thực tế.')
 if not d['meta'].get('source','').strip():notes.append('Chưa ghi nguồn BCTC, trang và thuyết minh.')
 if not d['meta'].get('price_source','').strip():notes.append('Chưa có ngày giá/nguồn EPS/BVPS. P/E, P/B nếu tính được vẫn cần đối chiếu thời điểm và điều chỉnh cổ phiếu.')
 notes.append('Chỉ dùng dữ liệu cả năm; ROA/ROE và lợi suất dùng bình quân hai mốc đầu/cuối năm, có thể khác chỉ số công bố bình quân nhiều mốc. Không tự xếp hạng tốt/xấu hoặc gán điểm F/M-Score cho nhóm tài chính.')
 out={'errors':errors,'notes':notes,'rows':[]}
 if errors:return out
 def get(y,k):
  v=p[y].get(k)
  if v is None:raise ValueError(f'Thiếu {fields[k][0]} ({y})')
  return v
 def div(a,b,label):
  if not math.isfinite(b) or b<=0:raise ValueError(f'{label}: mẫu số phải dương và hữu hạn')
  val=a/b
  if not math.isfinite(val):raise ValueError(f'{label}: kết quả vượt phạm vi số')
  return val
 def avg(y,k):return (get(y,k)+get('t1' if y=='t' else 't2',k))/2
 def ratio(y,n,den):return div(get(y,n),get(y,den),fields[den][0])
 def add(name,fn,unit,formula,note):
  vals=[];reasons=[]
  for y in ['t','t1']:
   try:vals.append(fn(y));reasons.append('')
   except ValueError as exc:vals.append(None);reasons.append(str(exc))
  diff=vals[0]-vals[1] if all(v is not None for v in vals) else None
  out['rows'].append({'Chỉ tiêu':name,'t':vals[0],'t1':vals[1],'Thay đổi':diff,'Đơn vị':unit,'Công thức':formula,'Ý nghĩa / Giới hạn':note,'Thiếu / Không xác định':'; '.join(f'{y}: {r}' for y,r in zip(['t','t1'],reasons) if r)})
 add('ROA',lambda y:div(get(y,'net_income'),avg(y,'assets'),'Tài sản bình quân'),'%', 'LNST / tài sản bình quân','Tổng LNST khớp tổng tài sản. Tăng không tự chứng minh chất lượng lợi nhuận tốt.')
 add('ROE',lambda y:div(get(y,'net_income'),avg(y,'equity'),'Vốn chủ bình quân'),'%', 'LNST / vốn chủ bình quân','Vốn chủ âm/không dương: không diễn giải. Đòn bẩy cao cũng có thể làm ROE cao.')
 add('P/E cơ bản',lambda y:div(get(y,'price'),get(y,'eps'),'EPS'),'lần','Giá VND/cp / EPS cơ bản VND/cp','EPS <= 0: không tính. Giá và EPS cần đồng nhất điều chỉnh; không kết luận rẻ chỉ từ P/E thấp.')
 add('P/B',lambda y:div(get(y,'price'),get(y,'bvps'),'BVPS'),'lần','Giá VND/cp / BVPS VND/cp','BVPS của cổ phần phổ thông, cùng cách điều chỉnh với giá. Không thay bằng tổng vốn hợp nhất nếu có lợi ích không kiểm soát.')
 def growth(k):return div(get('t',k)-get('t1',k),get('t1',k),'Giá trị năm trước')
 # Growth is current/prior; prior growth requires t-2 flow, not requested.
 def growth_row(name,k):
  try:v=growth(k);reason=''
  except ValueError as exc:v=None;reason=str(exc)
  out['rows'].append({'Chỉ tiêu':name,'t':v,'t1':None,'Thay đổi':None,'Đơn vị':'%','Công thức':'(t − t−1)/t−1, chỉ khi gốc > 0','Ý nghĩa / Giới hạn':'Không tính tăng trưởng năm trước vì không thu thập đầy đủ dòng tiền/lợi nhuận t−2. Gốc âm/0 không chuyển thành tăng trưởng phần trăm.','Thiếu / Không xác định':reason})
 growth_row('Tăng trưởng LNST','net_income')
 if kind=='bank':
  add('NPL cho vay khách hàng',lambda y:ratio(y,'npl','loans'),'%', 'Nợ nhóm 3–5 / cho vay khách hàng gộp','Cần đọc nợ tái cơ cấu, ngoại bảng, nợ đã xử lý; không chỉ nhìn tỷ lệ cuối kỳ.')
  add('Nợ nhóm 2 / cho vay',lambda y:ratio(y,'group2','loans'),'%', 'Nợ nhóm 2 / cho vay khách hàng gộp','Theo dõi nợ có thể chuyển nhóm; không gộp nhóm 2 vào NPL.')
  add('Bao phủ nợ xấu (LLR)',lambda y:ratio(y,'loan_reserves','npl'),'%', 'Dự phòng cho vay cuối kỳ / nợ xấu','NPL = 0 không tính tỷ lệ. Cần khớp phạm vi dự phòng với cho vay; tỷ lệ không chứng minh đủ dự phòng cho mọi tài sản.')
  add('CASA khách hàng',lambda y:ratio(y,'demand_deposits','deposits'),'%', 'Tiền gửi KKH khách hàng / tiền gửi khách hàng','Định nghĩa chỉ tiền gửi khách hàng, có thể khác CASA do ngân hàng công bố nếu phạm vi khác.')
  add('Cho vay / tiền gửi khách hàng',lambda y:ratio(y,'loans','deposits'),'%', 'Cho vay khách hàng gộp / tiền gửi khách hàng','Chỉ báo cơ cấu nguồn vốn; KHÔNG phải LDR pháp lý và không kiểm tra tuân thủ.')
  add('NIM tính bình quân hai mốc',lambda y:div(get(y,'net_interest'),avg(y,'earning_assets'),'Tài sản sinh lãi bình quân'),'%', 'Thu nhập lãi thuần năm / TS sinh lãi bình quân','Chỉ là cách tính hai mốc; có thể khác NIM bình quân ngày/tháng/quý công bố.')
  add('NIM công bố',lambda y:get(y,'nim_reported')/100,'%', 'Nhập từ tài liệu IR / công bố ngân hàng','Không tự thay NIM tính toán; đối chiếu phạm vi/kỳ/bình quân trước khi so sánh.')
  add('CIR',lambda y:ratio(y,'operating_cost','operating_income'),'%', 'Chi phí hoạt động / tổng thu nhập hoạt động thuần','Không gồm chi phí lãi hoặc dự phòng. CIR thấp hơn cần xem có khoản thu nhập bất thường không.')
  add('Chi phí tín dụng (xấp xỉ)',lambda y:div(get(y,'credit_cost'),avg(y,'loans'),'Cho vay bình quân'),'%', 'Chi phí dự phòng cho vay ròng / cho vay gộp bình quân','Chi phí trong kỳ, không phải số dư dự phòng. Hoàn nhập có thể làm âm.')
  add('CAR công bố',lambda y:get(y,'car_reported')/100,'%', 'Nhập từ công bố an toàn vốn','Không tính CAR bằng vốn chủ/tài sản. Không kiểm tra ngưỡng pháp lý; ghi nguồn/phạm vi và chuẩn áp dụng.')
  growth_row('Tăng trưởng cho vay khách hàng','loans');growth_row('Tăng trưởng tiền gửi khách hàng','deposits')
 else:
  add('Nợ vay / vốn chủ',lambda y:ratio(y,'borrowings','equity'),'lần','Vay chịu lãi / vốn chủ cuối kỳ','Không đồng nhất với tổng nợ phải trả; không tự kết luận vi phạm giới hạn pháp lý.')
  add('Tổng tài sản / vốn chủ',lambda y:ratio(y,'assets','equity'),'lần','Tổng tài sản / vốn chủ cuối kỳ','Chỉ báo đòn bẩy; không dùng thay tỷ lệ vốn khả dụng.')
  add('Dư nợ margin / vốn chủ',lambda y:ratio(y,'margin_loans','equity'),'lần','Cho vay ký quỹ / vốn chủ cuối kỳ','Cần đọc tập trung mã/tài sản bảo đảm, dự phòng và khả năng thu hồi. Không tự kiểm tra tuân thủ hạn mức.')
  add('Lợi suất cho vay margin (xấp xỉ)',lambda y:div(get(y,'margin_income'),avg(y,'margin_loans'),'Margin bình quân'),'%', 'Lãi margin năm / dư nợ margin bình quân hai mốc','Không cộng lãi tiền gửi/ứng trước nếu mẫu số chỉ là margin; không phải lãi suất hợp đồng.')
  add('Doanh thu môi giới / DT hoạt động',lambda y:ratio(y,'brokerage_revenue','operating_revenue'),'%', 'Doanh thu môi giới / doanh thu hoạt động','Là tỷ trọng doanh thu, không phải tỷ trọng lợi nhuận môi giới.')
  add('Lãi margin / DT hoạt động',lambda y:ratio(y,'margin_income','operating_revenue'),'%', 'Thu nhập lãi margin / doanh thu hoạt động','Không coi toàn bộ doanh thu cho vay/tiền gửi là lãi margin.')
  add('FVTPL ròng / DT hoạt động',lambda y:div(get(y,'fvtpl_gains')-get(y,'fvtpl_losses'),get(y,'operating_revenue'),'Doanh thu hoạt động'),'%', '(Lãi FVTPL − lỗ FVTPL) / doanh thu hoạt động','Có thể gồm đánh giá lại chưa thực hiện; không phải toàn bộ lợi nhuận tự doanh và các tỷ trọng không bắt buộc cộng bằng 100%.')
  add('Tài sản FVTPL / vốn chủ',lambda y:ratio(y,'fvtpl_assets','equity'),'lần','Giá trị FVTPL / vốn chủ cuối kỳ','FVTPL có thể gồm cổ phiếu, trái phiếu, chứng chỉ tiền gửi; cần xem cơ cấu và mức tập trung.')
  add('Bao phủ nợ ngắn hạn bằng tiền',lambda y:ratio(y,'liquid_assets','current_liabilities'),'lần','Tiền và tiền gửi NH thuộc công ty / nợ ngắn hạn','Không gồm tiền khách hàng; là chỉ báo đơn giản, không phải kết luận an toàn thanh khoản pháp lý.')
  add('Biên lợi nhuận trước thuế',lambda y:ratio(y,'pretax_income','operating_revenue'),'%', 'LNTT / doanh thu hoạt động','Phân loại doanh thu/lãi FVTPL cần nhất quán, không so ngang máy móc giữa các công ty.')
  add('Tỷ lệ vốn khả dụng công bố',lambda y:get(y,'capital_ratio_reported')/100,'%', 'Nhập từ Báo cáo tỷ lệ an toàn tài chính','Không suy ra từ vốn chủ. Ghi ngày, phạm vi riêng lẻ và căn cứ tính của báo cáo; không gắn ngưỡng tự động.')
  growth_row('Tăng trưởng dư nợ margin','margin_loans');growth_row('Tăng trưởng doanh thu hoạt động','operating_revenue')
 return out


def financial_export(data,result=None):
 wb=Workbook();ws=wb.active;ws.title='Tai_chinh';ws.append(['field','Chỉ tiêu','t','t1','t2','Hướng dẫn'])
 for k,(label,help_) in FIN_FIELDS[data['kind']].items():ws.append([k,label,*[data['periods'][y].get(k) for y in YEARS],help_])
 ms=wb.create_sheet('Thong_tin_TC');ms.append(['key','value']);ms.append(['kind',data['kind']])
 for k,v in data['meta'].items():ms.append([k,safe_text(v)])
 if result:
  sh=wb.create_sheet('Chi_tieu');rows=result['rows']
  if rows:
   sh.append(list(rows[0]))
   for row in rows:sh.append([safe_text(v) for v in row.values()])
   for i,row in enumerate(rows,2):
    if row['Đơn vị']=='%':
     for j in [2,3,4]:sh.cell(i,j).number_format='0.00%'
  note=wb.create_sheet('Luu_y');note.append(['Nội dung']);note.append(['Kết quả là ảnh chụp; nhập lại vào ứng dụng để tính sau khi sửa số. Thay đổi tỷ lệ là chênh điểm phần trăm khi hiển thị %.'])
  for n in result['errors']+result['notes']:note.append([safe_text(n)])
 for sh in wb:format_sheet(sh)
 if result and result['rows']:
  sh=wb['Chi_tieu']
  for i,row in enumerate(result['rows'],2):
   if row['Đơn vị']=='%':
    for j in [2,3,4]:sh.cell(i,j).number_format='0.00%'
 out=BytesIO();wb.save(out);return out.getvalue()


def financial_import(content,kind):
 if len(content)>5*1024*1024:raise ValueError('Tệp vượt 5 MB.')
 with ZipFile(BytesIO(content)) as z:
  if sum(i.file_size for i in z.infolist())>25*1024*1024:raise ValueError('Tệp giải nén quá lớn.')
 wb=load_workbook(BytesIO(content),read_only=True,data_only=False)
 try:
  if not {'Tai_chinh','Thong_tin_TC'}.issubset(wb.sheetnames):raise ValueError('Dùng mẫu Excel tài chính đúng nhóm, không dùng mẫu F/M-Score.')
  for sh in [wb['Tai_chinh'],wb['Thong_tin_TC']]:
   if sh.max_row is None or sh.max_column is None:sh.calculate_dimension(force=True)
   if sh.max_row>100 or sh.max_column>10:raise ValueError('Tệp không đúng kích thước mẫu.')
  rows=list(wb['Tai_chinh'].values);meta=list(wb['Thong_tin_TC'].values)
  if list(rows[0][:5])!=['field','Chỉ tiêu','t','t1','t2'] or list(meta[0][:2])!=['key','value']:raise ValueError('Không đổi tên cột trong mẫu.')
  md={};
  for row in meta[1:]:
   k,v=row[:2]
   if not k:continue
   if k in md:raise ValueError('Trùng thông tin: '+str(k))
   md[k]=v
  if md.pop('kind',None)!=kind:raise ValueError('Sai nhóm: tải và dùng mẫu của '+FIN_NAMES[kind])
  data=financial_blank(kind)
  if set(md)!=set(data['meta']):raise ValueError('Thiếu hoặc thừa trường thông tin.')
  for k,v in md.items():
   if k=='year':
    if isinstance(v,bool) or not isinstance(v,(int,float)) or int(v)!=v or not 1990<=v<=2100:raise ValueError('Năm phải là số nguyên 1990–2100.')
    v=int(v)
   elif k=='demo':
    if not isinstance(v,bool):raise ValueError('demo dùng TRUE/FALSE.')
   else:
    if v is None:v=''
    if not isinstance(v,str) or len(v)>3000 or v.startswith('='):raise ValueError('Thông tin phải là văn bản, không dùng công thức.')
   data['meta'][k]=v
  if data['meta']['unit'] not in ['VND','Nghìn VND','Triệu VND','Tỷ VND'] or data['meta']['scope'] not in ['Hợp nhất','Riêng lẻ']:raise ValueError('Đơn vị/phạm vi không hợp lệ.')
  seen=set()
  for row in rows[1:]:
   k=row[0]
   if not k:continue
   if k not in FIN_FIELDS[kind] or k in seen:raise ValueError('Chỉ tiêu lạ/trùng: '+str(k))
   seen.add(k)
   for i,y in enumerate(YEARS,2):
    v=row[i] if i<len(row) else None
    if v in (None,''):v=None
    elif isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError(f'{k}/{y}: dùng số, không dùng công thức hoặc số dạng chữ.')
    data['periods'][y][k]=v
  if seen!=set(FIN_FIELDS[kind]):raise ValueError('Thiếu dòng chỉ tiêu.')
  return data
 finally:wb.close()


def financial_page(kind):
 storage='finance_'+kind
 if storage not in st.session_state:st.session_state[storage]=financial_blank(kind)
 revkey=storage+'_revision'
 if revkey not in st.session_state:st.session_state[revkey]=0
 def load(d):st.session_state[storage]=deepcopy(d);st.session_state[revkey]+=1
 st.title('Phân tích '+FIN_NAMES[kind].lower())
 st.caption('Chỉ tiêu đặc thù ngành • Dữ liệu năm nhập tay/Excel • Không áp dụng F-Score/M-Score cho nhóm này')
 with st.expander('Tạo mới / minh họa / nhập Excel',expanded=True):
  a,b,c=st.columns(3)
  if a.button('Tạo bản mới',key=storage+'_new',width='stretch'):load(financial_blank(kind));st.rerun()
  if b.button('Nạp minh họa',key=storage+'_demo',width='stretch'):load(financial_demo(kind));st.rerun()
  c.download_button('Tải mẫu Excel',financial_export(financial_blank(kind)),f'Mau_{kind}.xlsx',key=storage+'_template',width='stretch')
  up=st.file_uploader('Chọn mẫu Excel đúng nhóm (tối đa 5 MB)',type=['xlsx'],key=storage+'_upload')
  if st.button('Áp dụng Excel',disabled=up is None,key=storage+'_apply'):
   try:load(financial_import(up.getvalue(),kind));st.rerun()
   except Exception as exc:st.error('Không nhập được: '+str(exc))
 data=st.session_state[storage];m=data['meta'];rev=st.session_state[revkey]
 def key(k):return f'{storage}_{rev}_{k}'
 a,b,c=st.columns(3)
 m['ticker']=a.text_input('Mã cổ phiếu',value=m['ticker'],max_chars=20,key=key('ticker')).strip().upper()
 m['year']=b.number_input('Năm báo cáo t',1990,2100,m['year'],key=key('year'))
 units=['VND','Nghìn VND','Triệu VND','Tỷ VND'];m['unit']=c.selectbox('Đơn vị số liệu BCTC',units,index=units.index(m['unit']),key=key('unit'))
 scopes=['Hợp nhất','Riêng lẻ'];m['scope']=st.selectbox('Phạm vi số liệu BCTC',scopes,index=scopes.index(m['scope']),key=key('scope'))
 m['source']=st.text_area('Nguồn BCTC, link và trang/thuyết minh',m['source'],max_chars=3000,key=key('source'))
 m['capital_source']=st.text_input('Nguồn, kỳ, phạm vi riêng lẻ/hợp nhất và chuẩn của CAR / tỷ lệ vốn khả dụng công bố',m['capital_source'],max_chars=3000,key=key('capital_source'))
 m['price_source']=st.text_input('Ngày giá t, ngày giá t−1; nguồn giá/EPS/BVPS và điều chỉnh cổ phiếu',m['price_source'],max_chars=3000,key=key('price_source'))
 m['demo']=st.checkbox('Đây là dữ liệu minh họa',m['demo'],key=key('demo'))
 st.info('Chỉ nhập BCTC cả năm. Ô trống là chưa biết; 0 là đã xác minh bằng 0. Giá/EPS/BVPS luôn VND/cp; CAR/NIM/vốn khả dụng công bố nhập theo %, ví dụ 12.5 = 12,5%. Đổi nhãn đơn vị không tự chuyển số.')
 tabs=st.tabs([f'Năm {m["year"]}',f'Năm {m["year"]-1}',f'Số đầu kỳ từ cuối {m["year"]-2}'])
 for i,y in enumerate(YEARS):
  with tabs[i]:
   keys=list(FIN_FIELDS[kind]) if y!='t2' else ['assets','equity']+(['loans','earning_assets'] if kind=='bank' else ['margin_loans'])
   cols=st.columns(2)
   for n,k in enumerate(keys):
    old=data['periods'][y][k]
    data['periods'][y][k]=cols[n%2].number_input(FIN_FIELDS[kind][k][0],value=float(old) if old is not None else None,format='%.4f',help=FIN_FIELDS[kind][k][1],key=key(y+'_'+k))
 result=financial_calculate(data)
 st.subheader('Bảng chỉ tiêu và so sánh hai năm')
 for n in result['errors']:st.error(n)
 for n in result['notes']:st.warning(n)
 if not m['capital_source'].strip():st.caption('Chưa ghi nguồn/phạm vi cho CAR hoặc vốn khả dụng; giá trị nhập tay chưa được xác minh.')
 if result['rows']:
  rows=[]
  def fmt(v,unit):return 'Chưa tính được' if v is None else f'{v*100:.2f}%' if unit=='%' else f'{v:.3f}'
  for r in result['rows']:
   row=dict(r);unit=r['Đơn vị'];row['t']=fmt(r['t'],unit);row['t1']=fmt(r['t1'],unit)
   row['Thay đổi']='—' if r['Thay đổi'] is None else (f'{r["Thay đổi"]*100:+.2f} điểm %' if unit=='%' else f'{r["Thay đổi"]:+.3f} lần');rows.append(row)
  st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')
  st.caption('Tăng/giảm chỉ mô tả số liệu. Cần đọc nguyên nhân, cơ cấu tài sản và chất lượng lợi nhuận; chưa có chấm điểm tổng, dự báo hay kết luận tuân thủ pháp luật.')
 name=re.sub(r'[^A-Z0-9_-]','',m['ticker']) or 'CHUA_DAT_MA'
 st.download_button('Tải dữ liệu và phân tích Excel',financial_export(data,result),f'{name}_{m["year"]}_{kind}.xlsx',type='primary',key=storage+'_export')
 st.caption('Excel giữ số liệu và kết quả tại thời điểm tải; nhập lại tệp đúng nhóm để dùng tiếp. Bản độc lập không tự lưu dữ liệu lâu dài trên máy chủ.')

def replace(data):
 st.session_state.data=deepcopy(data)
 st.session_state.revision+=1

USER_GUIDE='## StockAI Độc lập 1.1 — ngân hàng và chứng khoán\n\nBản này mở rộng StockAI_DocLap_v1. Vẫn có phân tích F/M-Score cho doanh nghiệp phi tài chính, nhập tay/Excel và bảng vĩ mô. Thêm hai phân hệ ngân hàng, công ty chứng khoán. Đây là bản độc lập, không có tài khoản, Supabase hoặc kho cộng đồng.\n\n### Cập nhật web Streamlit đã có\n\n1. Giải nén gói, thay **app.py** và **requirements.txt** trong repository GitHub đang nối với app (ví dụ macro-stock-app). Đặt app.py đúng vị trí file chạy đã cấu hình, không đặt lồng thêm một thư mục.\n2. Commit và chờ Streamlit cài lại thư viện. Nếu chưa cập nhật, vào Manage app → Reboot app.\n3. Không cần engine.py/file_io.py, mẫu Excel có sẵn hoặc Secrets: app.py đã chứa toàn bộ mã và tự tạo mẫu để tải. Tệp cũ có thể để nguyên vì app mới không import chúng.\n4. Chọn Ngân hàng hoặc Công ty chứng khoán ở thanh bên; nạp minh họa để thử. Không cần cài Python trên máy người xem web.\n\nNếu chạy máy cá nhân: cài Python 3.11/3.12, chạy `python -m pip install -r requirements.txt`, sau đó `python -m streamlit run app.py`.\n\n### Quy trình phân tích\n\n1. Chọn đúng nhóm doanh nghiệp. Chỉ dùng BCTC **cả năm** của hai năm liền nhau. Nhập năm t, mã, đơn vị, hợp nhất/riêng lẻ.\n2. Nguồn BCTC: ghi link và trang/thuyết minh. CAR ngân hàng/vốn khả dụng CTCK có thể theo báo cáo riêng lẻ, khác BCTC hợp nhất: ghi đúng phạm vi và kỳ trong ô nguồn an toàn vốn.\n3. Tải mẫu Excel đúng nhóm hoặc nhập ngay trên web. Các mẫu ngân hàng, chứng khoán và F/M-Score không hoán đổi cho nhau.\n4. Ô trống = chưa biết; số 0 = đã xác minh bằng 0. Không nhập 0 để xóa thông báo thiếu dữ liệu. Chi phí/lỗ FVTPL nhập trị dương; LNST, LNTT và khoản dự phòng ròng hoàn nhập có thể âm.\n5. Tab t−2 chỉ cần số dư đầu kỳ phục vụ bình quân. Ngân hàng: tài sản, vốn chủ, cho vay và tài sản sinh lãi. Chứng khoán: tài sản, vốn chủ và dư nợ margin.\n6. Xem bảng công thức, giới hạn và lý do chỉ tiêu chưa tính được. Mỗi chỉ tiêu tính độc lập; thiếu một chỉ tiêu không tự biến thành 0 hoặc một điểm số tổng.\n7. Tải dữ liệu và kết quả Excel trước khi đóng tab. Có thể nhập lại tệp này ở đúng nhóm để dùng tiếp. Các sheet kết quả là ảnh chụp tại thời điểm tải, không phải bảng Excel tự tính lại.\n\n### Đơn vị quan trọng\n\n- Các khoản BCTC dùng cùng một đơn vị cho mọi năm. Chọn Triệu VND thì nhập số theo triệu. Đổi nhãn đơn vị không chuyển đổi số đã nhập.\n- Giá, EPS, BVPS luôn là **VND/cổ phiếu**, không đổi sang triệu/tỷ theo số liệu BCTC.\n- CAR/NIM/vốn khả dụng công bố nhập theo **phần trăm**: 12.5 nghĩa 12,5%; 250 nghĩa 250%, không nhập 0.125 thay cho 12,5%.\n- Cột thay đổi của tỷ lệ là chênh **điểm phần trăm**; của bội số là chênh số lần. Không phải tăng trưởng phần trăm của tỷ lệ.\n\n### Ngân hàng\n\n| Chỉ tiêu | Cách lấy và công thức |\n|---|---|\n| ROA, ROE | Tổng LNST / tổng tài sản hoặc vốn chủ bình quân hai mốc. Không trộn LNST cổ đông mẹ với vốn chủ có lợi ích không kiểm soát. |\n| NPL | Nợ nhóm 3–5 / cho vay khách hàng gộp trước dự phòng, cùng phạm vi. |\n| Nợ nhóm 2 | Nợ nhóm 2 / cho vay khách hàng gộp. |\n| LLR | Số dư dự phòng cho vay khách hàng / nợ nhóm 3–5. Không dùng dự phòng chứng khoán/cam kết khác. Nợ xấu bằng 0 không có tỷ lệ này. |\n| CASA | Tiền gửi khách hàng không kỳ hạn / tổng tiền gửi khách hàng. Có thể khác định nghĩa CASA công bố nếu ngân hàng dùng phạm vi khác. |\n| Cho vay / tiền gửi | Cho vay khách hàng / tiền gửi khách hàng. Đây là chỉ báo cơ cấu, **không phải LDR pháp lý**. |\n| NIM tính hai mốc | Thu nhập lãi thuần cả năm / tài sản sinh lãi bình quân đầu-cuối năm. Không dùng tổng tài sản thay tài sản sinh lãi. |\n| NIM công bố | Nhập thêm từ IR để đối chiếu, không tự thay thế NIM tính hai mốc. Bình quân ngày/tháng/quý có thể khác hai mốc. |\n| CIR | Chi phí hoạt động / tổng thu nhập hoạt động thuần (TOI), trước dự phòng. Không cộng chi phí lãi/dự phòng vào chi phí hoạt động. |\n| Chi phí tín dụng xấp xỉ | Chi phí dự phòng cho vay ròng trong năm / cho vay bình quân hai mốc; không lấy số dư dự phòng cuối kỳ. Hoàn nhập ròng có thể âm. |\n| CAR | Nhập chỉ số công bố và nguồn/chuẩn/phạm vi; không tính vốn chủ/tổng tài sản để gọi là CAR. |\n\nTheo dõi thêm tăng trưởng LNST, cho vay khách hàng và tiền gửi. Chỉ tính tăng trưởng phần trăm nếu giá trị năm gốc dương. Năm gốc âm/0 cần đọc số tuyệt đối, không đưa ra tốc độ tăng gây hiểu nhầm.\n\n### Công ty chứng khoán\n\n| Chỉ tiêu | Cách lấy và công thức |\n|---|---|\n| ROA, ROE | Tổng LNST / tài sản hoặc vốn chủ bình quân hai mốc. |\n| Nợ vay / vốn chủ | Vay chịu lãi / vốn chủ cuối kỳ; khác tổng nợ phải trả. |\n| Tài sản / vốn chủ | Chỉ báo đòn bẩy tổng thể. |\n| Margin / vốn chủ | Dư nợ cho vay ký quỹ / vốn chủ. Không gộp ứng trước nếu đang phân tích riêng margin. |\n| Lợi suất margin xấp xỉ | Lãi margin cả năm / dư nợ margin bình quân hai mốc. Không dùng cả lãi tiền gửi/ứng trước. |\n| Tỷ trọng môi giới/margin | Doanh thu môi giới hoặc lãi margin / doanh thu hoạt động, không phải tỷ trọng lợi nhuận. |\n| FVTPL ròng / doanh thu | (Lãi FVTPL − lỗ FVTPL) / doanh thu hoạt động. Có thể gồm đánh giá lại chưa thực hiện; không phải toàn bộ lợi nhuận tự doanh. Các tỷ trọng không bắt buộc cộng bằng 100%. |\n| FVTPL / vốn chủ | Giá trị ghi sổ FVTPL / vốn chủ; cần xem cơ cấu cổ phiếu, trái phiếu, chứng chỉ tiền gửi... |\n| Bao phủ nợ NH bằng tiền | Tiền và tiền gửi ngắn hạn thuộc công ty / nợ ngắn hạn. Không cộng tiền nhà đầu tư; đây là chỉ báo đơn giản. |\n| Biên LNTT | LNTT / doanh thu hoạt động, cùng cách phân loại hai năm. |\n| Tỷ lệ vốn khả dụng | Nhập từ Báo cáo tỷ lệ an toàn tài chính, ghi ngày/phạm vi riêng lẻ và căn cứ tính. Không suy ra từ vốn chủ BCTC hợp nhất. |\n\nTheo dõi tăng trưởng LNST, doanh thu hoạt động và dư nợ margin. Không tự coi margin tăng hoặc FVTPL tăng là tốt: cần xem nguồn vốn, tập trung tài sản và thị trường.\n\n### P/E và P/B cho cả hai nhóm\n\nGiá và EPS/BVPS nhập tay, không có dữ liệu giá tự động. Ghi riêng ngày giá t, ngày giá t−1, nguồn và cách điều chỉnh cổ phiếu. P/E = giá/EPS cơ bản công bố; P/B = giá/BVPS của cổ phần phổ thông. Không dùng tổng LNST chia số cổ phiếu cuối kỳ để thay EPS bình quân gia quyền. EPS hoặc BVPS không dương thì chỉ số tương ứng không tính. Thiếu giá không chặn phân tích sức khỏe tài chính.\n\n### Excel\n\n- Sheet Tai_chinh: giữ nguyên field, tiêu đề, số dòng; điền t, t1 và các số dư t2 cần thiết.\n- Sheet Thong_tin_TC: kind là bank hoặc broker, không đổi sang nhóm khác; year là năm t; demo là TRUE/FALSE; ghi nguồn ở source, capital_source, price_source.\n- Giá trị số phải là số thật trong Excel, không dùng công thức hoặc số dạng chữ. Không đổi tiêu đề/cột. Tệp tối đa 5 MB.\n- Không thể nhập mẫu tài chính vào chức năng F/M-Score và ngược lại.\n\n### Giới hạn\n\nBản độc lập chỉ tính và xuất file; không lưu bài của thành viên chung trên máy chủ. Bản này giữ đúng phạm vi yêu cầu nâng cấp StockAI_DocLap_v1, không mang tính năng Supabase của bản cộng đồng 2.0 vào.\n\nĐây là bộ chỉ tiêu mô tả, không có thang điểm ngân hàng/chứng khoán tự đặt. Không áp dụng F-Score/M-Score cho hai nhóm này. Không kiểm tra tuân thủ các ngưỡng an toàn vốn/margin/LDR; không coi các tỷ lệ đơn giản là tỷ lệ pháp lý. Không kết luận mua/bán, xác suất gian lận hoặc chất lượng khoản vay chỉ từ một chỉ số. Chưa đọc PDF/cào dữ liệu tự động và chưa đối chiếu nguồn gốc của dữ liệu nhập tay.\n\n### Nguồn tham khảo định nghĩa và nơi lấy dữ liệu\n\n- Techcombank — định nghĩa chỉ số IR và phạm vi: https://techcombank.com/en/investors/financial-information/highlights\n- SSI — BCTC và Báo cáo tỷ lệ an toàn tài chính: https://www.ssi.com.vn/quan-he-nha-dau-tu/bao-cao-tai-chinh\n- SSI — Báo cáo thường niên và cơ cấu hoạt động: https://www.ssi.com.vn/quan-he-nha-dau-tu/bao-cao-thuong-nien\n\nCác số minh họa hoàn toàn giả lập, không trích từ những doanh nghiệp này. Khi dùng thật, cần báo cáo của chính doanh nghiệp và năm đang phân tích.\n'

def main():
 st.set_page_config(page_title='StockAI | Phân tích BCTC',page_icon='📊',layout='wide')
 st.markdown('''<style>.block-container{max-width:1200px;padding-top:2rem}h1,h2,h3{color:#123047}div[data-testid="stMetric"]{background:#eef5f7;padding:16px;border-radius:12px}.stButton>button{border-radius:8px} </style>''',unsafe_allow_html=True)
 if 'data' not in st.session_state:st.session_state.data=blank()
 if 'revision' not in st.session_state:st.session_state.revision=0
 
 st.sidebar.title('NHÀ ĐẦU TƯ\nTHÔNG THÁI')
 st.sidebar.caption('Công cụ đọc hiểu BCTC • Phiên bản độc lập 1.1')
 page=st.sidebar.radio('Chức năng',['Phân tích BCTC','Ngân hàng','Công ty chứng khoán','Vĩ mô thủ công','Hướng dẫn'])
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
 elif page in ['Ngân hàng','Công ty chứng khoán']:
  financial_page('bank' if page=='Ngân hàng' else 'broker')
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
  st.markdown(USER_GUIDE)
 st.divider();st.caption('StockAI Độc lập 1.1 • Công cụ hỗ trợ đọc BCTC. Dữ liệu do người dùng cung cấp, chưa được đối chiếu tự động với báo cáo gốc.')

if __name__=="__main__":
 main()
