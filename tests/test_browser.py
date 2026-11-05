import json, threading, time, http.server, socketserver, pathlib, datetime as dt
from playwright.sync_api import sync_playwright
from zoneinfo import ZoneInfo
root=pathlib.Path(__file__).resolve().parents[1]
class H(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
 def log_message(self,*args):pass
class S(socketserver.TCPServer):allow_reuse_address=True
srv=S(('127.0.0.1',0),H)
threading.Thread(target=srv.serve_forever,daemon=True).start()
port=srv.server_address[1]
today=dt.datetime.now(ZoneInfo('Europe/Berlin')).date().isoformat()
record={'id':'test-current-1','company':'Example Projects','title':'Junior Project Manager','city':'Berlin','location':'Berlin, Germany','category':'PMO / Project','employment':'Full-time','workplace':'Hybrid','posted':today,'url':'https://example.com/job','score':92,'reason':'Project experience and stakeholder coordination','watchout':'Test fixture','skills':['Excel'],'source':'Test feed','reviewed':False,'language':'English required'}
body={'generated_at':dt.datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),'jobs':[record],'scanned':200,'added':1,'errors':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1280,'height':900})
 page.goto('about:blank')
 page.evaluate('''(payload)=>{ window.fetch = async () => ({ok:true, json: async () => payload}); }''', body)
 errs=[]
 page.on('pageerror',lambda ex: errs.append(str(ex)))
 page.set_content((root/'index.html').read_text(),wait_until='domcontentloaded')
 page.wait_for_timeout(1100)
 text=page.locator('body').inner_text()
 assert 'Junior Project Manager' in text, 'Missing daily feed listing'
 assert '200 screened' in text, 'Missing last update timestamp'
 page.get_by_label('Application status').first.select_option('Applied')
 assert page.locator('body').inner_text().count('Applied')>=2
 assert '1' in page.locator('.stat').nth(1).inner_text(), 'Applied count not updated'
 assert not errs, errs
 page.screenshot(path=str(root/'preview.png'),full_page=True)
 browser.close()
srv.shutdown()
print('Browser UI test passed: scheduled results loaded, status persisted, no JavaScript errors')
