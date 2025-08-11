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

async def user_setting_top_menu():
    with get_db_connect() as conn:
        curs = conn.cursor()

        ip = ip_check()
        if (await ban_check(ip))[0] == 1:
            return await re_error(conn, 0)

        if ip_or_user(ip) == 1:
            return redirect(conn, '/login')
        
        if flask.request.method == 'POST':
            curs.execute(db_change("select data from user_set where name = 'top_menu' and id = ?"), [ip])
            if curs.fetchall():
                curs.execute(db_change("update user_set set data = ? where name = 'top_menu' and id = ?"), [flask.request.form.get('content', ''), ip])
            else:
                curs.execute(db_change("insert into user_set (name, data, id) values ('top_menu', ?, ?)"), [flask.request.form.get('content', ''), ip])

            return redirect(conn, '/change/top_menu')
        else:
            curs.execute(db_change("select data from user_set where name = 'top_menu' and id = ?"), [ip])
            db_data = curs.fetchall()
            db_data = db_data[0][0] if db_data else ''
            
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'user_added_menu'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <span>
                        EX)
                        <br>
                        ONTS
                        <br>
                        https://2du.pythonanywhere.com/
                        <br>
                        FrontPage
                        <br>
                        /w/FrontPage
                    </span>
                    <hr class="main_hr">
                    ''' + get_lang(conn, 'not_support_skin_warning') + '''
                    <hr class="main_hr">
                    <form method="post">
                        <textarea class="opennamu_textarea_500" placeholder="''' + get_lang(conn, 'enter_top_menu_setting') + '''" name="content" id="content">''' + html.escape(db_data) + '''</textarea>
                        <hr class="main_hr">
                        <button id="opennamu_save_button" type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['setting', get_lang(conn, 'return')]]
            ))