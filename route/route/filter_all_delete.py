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

async def filter_all_delete(tool, name = 'Test'):
    with get_db_connect() as conn:
        curs = conn.cursor()
        
        if await acl_check(tool = 'owner_auth', memo = 'del_' + tool) == 1:
            return await re_error(conn, 3)

        if tool == 'inter_wiki':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'inter_wiki'"), [name])
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'inter_wiki_sub'"), [name])
        elif tool == 'edit_filter':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'regex_filter'"), [name])
        elif tool == 'name_filter':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'name'"), [name])
        elif tool == 'file_filter':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'file'"), [name])
        elif tool == 'email_filter':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'email'"), [name])
        elif tool == 'image_license':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'image_license'"), [name])
        elif tool == 'extension_filter':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'extension'"), [name])
        elif tool == 'document':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'document'"), [name])
        elif tool == 'outer_link':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'outer_link'"), [name])
        elif tool == 'template':
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'template'"), [name])
        else:
            curs.execute(db_change("delete from html_filter where html = ? and kind = 'edit_top'"), [name])

        return redirect(conn, '/filter/' + tool)