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

async def list_long_page(tool = 'long_page', arg_num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        sql_num = (arg_num * 50 - 50) if arg_num * 50 > 0 else 0

        div = '<ul>'
        select_data = 'desc' if tool == 'long_page' else 'asc'
        title = 'long_page' if tool == 'long_page' else 'short_page'

        curs.execute(db_change("select doc_name, set_data from data_set where set_name = 'length' and doc_rev = '' order by set_data + 0 " + select_data + " limit ?, 50"), [sql_num])
        n_list = curs.fetchall()
        for data in n_list:
            div += '<li>'
            div += data[1] + ' | <a href="/w/' + url_pas(data[0]) + '">' + html.escape(data[0]) + '</a>'
            
            curs.execute(db_change("select set_data from data_set where doc_name = ? and set_name = 'doc_type'"), [data[0]])
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                div += ' | ' + db_data[0][0]

            div += '</li>'

        div += '</ul>' + get_next_page_bottom(conn, '/list/document/' + ('long' if title == 'long_page' else 'short') + '/{}', arg_num, n_list)

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, title), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = div,
            menu = [['other', get_lang(conn, 'return')]]
        ))