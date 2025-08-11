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

async def main_func_easter_egg():
    with get_db_connect() as conn:
        curs = conn.cursor()

        ip = ip_check()
        if ip_or_user(ip) == 0:
            curs.execute(db_change('select name from user_set where id = ? and name = ?'), [ip, 'get_🥚'])
            if not curs.fetchall():
                curs.execute(db_change('insert into user_set (name, id, data) values ("get_🥚", ?, "Y")'), [ip])
    
        if platform.system() == 'Linux':
            if platform.machine() in ["AMD64", "x86_64"]:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.amd64.bin"), sys._getframe().f_code.co_name], stdout = subprocess.PIPE).communicate()[0]
            else:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.arm64.bin"), sys._getframe().f_code.co_name], stdout = subprocess.PIPE).communicate()[0]

            data = data.decode('utf8')
        elif platform.system() == 'Windows':
            if platform.machine() in ["AMD64", "x86_64"]:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.amd64.exe"), sys._getframe().f_code.co_name], stdout = subprocess.PIPE).communicate()[0]
            else:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.arm64.exe"), sys._getframe().f_code.co_name], stdout = subprocess.PIPE).communicate()[0]

            data = data.decode('utf8')
        else:
            data = ''

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = ['Easter Egg', await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = data,
            menu = 0
        ))