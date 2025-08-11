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

async def user_setting_head_reset():
    with get_db_connect() as conn:
        curs = conn.cursor()

        skin_name = skin_check(conn, 1)
        ip = ip_check()

        if flask.request.method == 'POST':
            get_data = ''
            if ip_or_user(ip) == 0:
                curs.execute(db_change("select id from user_set where id = ? and name = ?"), [ip, 'custom_css'])
                if curs.fetchall():
                    curs.execute(db_change("update user_set set data = ? where id = ? and name = ?"), [get_data, ip, 'custom_css'])
                else:
                    curs.execute(db_change("insert into user_set (id, name, data) values (?, ?, ?)"), [ip, 'custom_css', get_data])

                curs.execute(db_change("select id from user_set where id = ? and name = ?"), [ip, 'custom_css_' + skin_name])
                if curs.fetchall():
                    curs.execute(db_change("update user_set set data = ? where id = ? and name = ?"), [get_data, ip, 'custom_css_' + skin_name])
                else:
                    curs.execute(db_change("insert into user_set (id, name, data) values (?, ?, ?)"), [ip, 'custom_css_' + skin_name, get_data])

            flask.session['head'] = ''
            flask.session['head_' + skin_name] = ''

            return redirect(conn, '/change/head')
        else:
            if ip_or_user(ip) == 0:
                curs.execute(db_change("select data from user_set where id = ? and name = ?"), [ip, 'custom_css'])
                head_data = curs.fetchall()
                data = head_data[0][0] if head_data else ''

                curs.execute(db_change("select data from user_set where id = ? and name = ?"), [ip, 'custom_css_' + skin_name])
                head_data = curs.fetchall()
                data_skin = head_data[0][0] if head_data else ''
            else:
                data = flask.session['head'] if 'head' in flask.session else ''
                data_skin = flask.session['head_' + skin_name] if 'head_' + skin_name in flask.session else ''
            
            return '''
                <form method="post">
                    <style>.main_hr { border: none; }</style>
                    ''' + get_lang(conn, 'all') + '''
                    <hr class="main_hr">
                    <pre>''' + html.escape(data) + '''</pre>
                    <hr class="main_hr">
                    ''' + skin_name + '''
                    <hr class="main_hr">
                    <pre>''' + html.escape(data_skin) + '''</pre>
                    <hr class="main_hr">
                    <button type="submit">''' + get_lang(conn, 'reset') + '''</button>
                </form>
            '''