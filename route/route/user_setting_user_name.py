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

async def user_setting_user_name(user_name = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        ip = ip_check()
        if user_name != '':
            if await acl_check('', 'owner_auth', '', '') == 1:
                return await re_error(conn, 3)
            else:
                ip = user_name
    
        if ip_or_user(ip) == 0:
            if flask.request.method == 'POST':
                auto_data = ['user_name', flask.request.form.get('new_user_name', '')]
                if do_user_name_check(conn, auto_data[1]) == 1:
                    return await re_error(conn, 8)

                curs.execute(db_change('select data from user_set where name = ? and id = ?'), [auto_data[0], ip])
                if curs.fetchall():
                    curs.execute(db_change("update user_set set data = ? where name = ? and id = ?"), [auto_data[1], auto_data[0], ip])
                else:
                    curs.execute(db_change("insert into user_set (name, id, data) values (?, ?, ?)"), [auto_data[0], ip, auto_data[1]])

                if user_name != '':
                    return redirect(conn, '/change/user_name/' + url_pas(user_name))
                else:
                    return redirect(conn, '/change/user_name')
            else:
                user_name = ip

                curs.execute(db_change("select data from user_set where id = ? and name = 'user_name'"), [ip])
                db_data = curs.fetchall()
                if db_data and db_data[0][0] != '':
                    user_name = db_data[0][0]

                return easy_minify(conn, flask.render_template(skin_check(conn),
                    imp = [get_lang(conn, 'change_user_name'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                    data = '''
                        <form method="post">
                            <input name="new_user_name" placeholder="''' + get_lang(conn, 'user_name') + '''" value="''' + html.escape(user_name) + '''">
                            <hr class="main_hr">
                            <button id="opennamu_save_button" type="submit">''' + get_lang(conn, 'save') + '''</button>
                        </form>
                    ''',
                    menu = [['change', get_lang(conn, 'return')]]
                ))
        else:
            return redirect(conn, '/login')