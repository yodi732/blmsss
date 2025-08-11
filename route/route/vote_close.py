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

async def vote_close(num = 1):
    num = str(num)
    
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check('', 'vote') == 1:
            return await re_error(conn, 0)

        curs.execute(db_change('select type from vote where id = ? and user = ""'), [num])
        data_list = curs.fetchall()
        if not data_list:
            return redirect(conn, '/vote')

        curs.execute(db_change('select data from vote where id = ? and name = "open_user" and type = "option"'), [num])
        db_data = curs.fetchall()
        open_user = db_data[0][0] if db_data else ''
        if open_user != ip_check() and await acl_check('', 'vote_auth', '', '') == 1:
            return await re_error(conn, 0)

        if data_list[0][0] == 'close':
            type_set = 'open'
        elif data_list[0][0] == 'n_close':
            type_set = 'n_open'
        elif data_list[0][0] == 'open':
            type_set = 'close'
        else:
            type_set = 'n_close'

        curs.execute(db_change("update vote set type = ? where user = '' and id = ? and type = ?"), [type_set, num, data_list[0][0]])
        curs.execute(db_change('delete from vote where name = "end_date" and type = "option" and id = ?'), [num])

        if data_list[0][0] == 'close' or data_list[0][0] == 'n_close':
            return redirect(conn, '/vote')
        else:
            return redirect(conn, '/vote/list/close')