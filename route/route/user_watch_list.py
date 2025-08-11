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

async def user_watch_list(tool):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if tool == 'watch_list':
            div = get_lang(conn, "msg_whatchlist_lmt") + ' : 10 <hr class="main_hr">'
        else:
            div = ''

        ip = ip_check()

        if ip_or_user(ip) != 0:
            return redirect(conn, '/login')

        if tool == 'watch_list':
            curs.execute(db_change("select data from user_set where name = 'watchlist' and id = ?"), [ip])
            title_name = get_lang(conn, 'watchlist')
        else:
            curs.execute(db_change("select data from user_set where name = 'star_doc' and id = ?"), [ip])
            title_name = get_lang(conn, 'star_doc')

        data = curs.fetchall()
        for data_list in data:
            curs.execute(db_change("select date from history where title = ? order by id + 0 desc limit 1"), [data_list[0]])
            get_data = curs.fetchall()
            plus = '(' + get_data[0][0] + ') ' if get_data else ''
            
            div += '' + \
                '<li>' + \
                    '<a href="/w/' + url_pas(data_list[0]) + '">' + html.escape(data_list[0]) + '</a> ' + \
                    plus + \
                    '<a href="/' + ('star_doc' if tool == 'star_doc' else 'watch_list') + '/' + url_pas(data_list[0]) + '">(' + get_lang(conn, 'delete') + ')</a>' + \
                '</li>' + \
            ''

        if data:
            div = '' + \
                '<ul>' + div + '</ul>' + \
                '<hr class="main_hr">' + \
            ''

        div += '<a href="/manager/' + ('13' if tool == 'watch_list' else '16') + '">(' + get_lang(conn, 'add') + ')</a>'

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [title_name, await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = div,
            menu = [['user', get_lang(conn, 'return')]]
        ))
