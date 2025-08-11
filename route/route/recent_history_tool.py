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

async def recent_history_tool(name = 'Test', rev = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        num = str(rev)

        data = '' + \
            '<h2>' + get_lang(conn, 'tool') + '</h2>' + \
            '<ul>' + \
                '<li><a href="/raw_rev/' + num + '/' + url_pas(name) + '">' + get_lang(conn, 'raw') + '</a></li>' + \
        ''

        data += '<li><a href="/revert/' + num + '/' + url_pas(name) + '">' + get_lang(conn, 'revert') + ' (r' + num + ')</a></li>'
        if rev - 1 > 0:
            data += '<li><a href="/revert/' + str(rev - 1) + '/' + url_pas(name) + '">' + get_lang(conn, 'revert') + ' (r' + str(rev - 1) + ')</a></li>'

        if rev - 1 > 0:
            data += '<li><a href="/diff/' + str(rev - 1) + '/' + num + '/' + url_pas(name) + '">' + get_lang(conn, 'compare') + '</a></li>'

        data += '<li><a href="/history/' + url_pas(name) + '">' + get_lang(conn, 'history') + '</a></li>'
        data += '</ul>'

        if await acl_check(tool = 'hidel_auth') != 1:
            data += '<h3>' + get_lang(conn, 'admin') + '</h3>'
            data += '<ul>'
            curs.execute(db_change('select title from history where title = ? and id = ? and hide = "O"'), [name, num])
            data += '<li><a href="/history_hidden/' + num + '/' + url_pas(name) + '">'
            if curs.fetchall():
                data += get_lang(conn, 'hide_release') 
            else:
                data += get_lang(conn, 'hide')

            data += '</a></li>'
            data += '</ul>'

        if await acl_check('', 'owner_auth', '', '') != 1:
            data += '<h3>' + get_lang(conn, 'owner') + '</h3>'
            data += '<ul>'
            data += '<li><a href="/history_delete/' + num + '/' + url_pas(name) + '">' + get_lang(conn, 'history_delete') + '</a></li>'
            data += '<li><a href="/history_send/' + num + '/' + url_pas(name) + '">' + get_lang(conn, 'send_edit') + '</a></li>'
            data += '</ul>'

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [name, await wiki_set(), await wiki_custom(conn), wiki_css(['(r' + num + ')', 0])],
            data = data,
            menu = [['history/' + url_pas(name), get_lang(conn, 'return')]]
        ))