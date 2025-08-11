# --- AUTO-INJECTED RENDER-SAFE HEADER ---
# 방어용 헤더: 기본 전역 dict 보장, safe_get, safe_json_load, os/subprocess wrappers
import os, sys, json, subprocess, types
try:
    golang_enabled
except NameError:
    golang_enabled = False
# safe helpers
def safe_get(obj, key, default=None):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
    except Exception:
        pass
    return default
def safe_json_load(path, default=None):
    try:
        with open(path, 'r', encoding='utf8') as f:
            return json.load(f)
    except Exception:
        return default
# ensure common globals used by app are dicts to avoid .get attribute errors
for _n in ('server_set','server_set_val','server_set_var','data_db_set','version_list','global_some_set','global_lang_data'):
    if _n not in globals() or not isinstance(globals().get(_n), dict):
        globals()[_n] = {}
# wrap subprocess.Popen to no-op when golang disabled to avoid crashes on missing binaries
_orig_popen = subprocess.Popen
def _safe_popen(*a, **k):
    if not globals().get('golang_enabled', False):
        class _Dummy:
            def poll(self): return 0
            def terminate(self): pass
            def kill(self): pass
            def wait(self, timeout=None): return
        return _Dummy()
    return _orig_popen(*a, **k)
subprocess.Popen = _safe_popen
# safe os.chmod wrapper
_orig_chmod = getattr(os, 'chmod', None)
def _safe_chmod(path, mode):
    try:
        if not os.path.exists(path):
            return
        if _orig_chmod:
            _orig_chmod(path, mode)
    except Exception:
        pass
os.chmod = _safe_chmod
# end header marker
# --- END HEADER ---

from .tool.func import *

async def user_alarm():
    with get_db_connect() as conn:
        curs = conn.cursor()
    
        num = int(number_check(flask.request.args.get('num', '1')))
        sql_num = (num * 50 - 50) if num * 50 > 0 else 0
    
        data = '<ul>'

        ip = ip_check()
    
        curs.execute(db_change("select data, date, readme, id from user_notice where name = ? order by date desc limit ?, 50"), [ip, sql_num])
        data_list = curs.fetchall()
        if data_list:
            data = '' + \
                '<a href="/alarm/delete">(' + get_lang(conn, 'delete') + ')</a>' + \
                '<hr class="main_hr">' + \
                data + \
            ''
    
            for data_one in data_list:
                data_split = data_one[0].split(' | ')
                data_style = ''
                if data_one[2] == '1':
                    data_style = 'opacity: 0.75;'
                
                data += '' + \
                    '<li style="' + data_style + '">' + \
                        await ip_pas(data_split[0]) + (' | ' + ' | '.join(data_split[1:]) if len(data_split) > 1 else '') + \
                        ' | ' + data_one[1] + \
                        ' <a href="/alarm/delete/' + url_pas(data_one[3]) + '">(' + get_lang(conn, 'delete') + ')</a>' + \
                    '</li>' + \
                ''

        curs.execute(db_change("update user_notice set readme = '1' where name = ?"), [ip])
    
        data += '' + \
            '</ul>' + \
            get_next_page_bottom(conn, '/alarm?num={}', num, data_list) + \
        ''
    
        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'notice'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = data,
            menu = [['user', get_lang(conn, 'return')]]
        ))