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
