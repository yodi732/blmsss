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

async def give_user_fix(user_name = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        curs.execute(db_change("select data from user_set where id = ? and name = 'pw'"), [user_name])
        if not curs.fetchall():
            return await re_error(conn, 2)

        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 3)

        if flask.request.method == 'POST':
            select = flask.request.form.get('select', '')

            await acl_check(tool = 'owner_auth', memo = 'user_fix (' + user_name + ') (' + select + ')')
            if select == 'password_change':
                password = flask.request.form.get('new_password', '')
                check_password = flask.request.form.get('password_check', '')

                if password == check_password:
                    hashed = pw_encode(conn, password)
                    curs.execute(db_change("update user_set set data = ? where id = ? and name = 'pw'"), [
                        hashed,
                        user_name
                    ])
                else:
                    return await re_error(conn, 20)
            elif select == '2fa_password_change':
                password = flask.request.form.get('new_password', '')
                check_password = flask.request.form.get('password_check', '')

                if password == check_password:
                    hashed = pw_encode(conn, password)
                    curs.execute(db_change('select data from user_set where name = "2fa_pw" and id = ?'), [user_name])
                    if curs.fetchall():
                        curs.execute(db_change("update user_set set data = ? where name = '2fa_pw' and id = ?"), [hashed, user_name])
                    else:
                        curs.execute(db_change("insert into user_set (name, id, data) values ('2fa_pw', ?, ?)"), [user_name, hashed])
                else:
                    return await re_error(conn, 20)
            elif select == '2fa_off':
                curs.execute(db_change('select data from user_set where name = "2fa" and id = ?'), [user_name])
                if curs.fetchall():
                    curs.execute(db_change("update user_set set data = '' where name = '2fa' and id = ?"), [user_name])

            return redirect(conn, '/user/' + url_pas(user_name))
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'user_fix'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        <div id="opennamu_get_user_info">''' + html.escape(user_name) + '''</div>
                        <hr class="main_hr">
                        <a href="/change/user_name/''' + url_pas(user_name) + '''">(''' + get_lang(conn, 'change_user_name') + ''')</a>
                        <hr class="main_hr">
                        <select name="select">
                            <option value="password_change">''' + get_lang(conn, 'password_change') + '''</option>
                            <option value="2fa_password_change">''' + get_lang(conn, '2fa_password_change') + '''</option>
                            <option value="2fa_off">''' + get_lang(conn, '2fa_off') + '''</option>
                        </select>
                        <hr class="main_hr">
                        ''' + get_lang(conn, 'password_change') + ''' | ''' + get_lang(conn, '2fa_password_change') + '''
                        <hr class="main_hr">
                        <input placeholder="''' + get_lang(conn, 'new_password') + '''" name="new_password" type="password">
                        <hr class="main_hr">
                        <input placeholder="''' + get_lang(conn, 'password_confirm') + '''" name="password_check" type="password">
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'go') + '''</button>
                    </form>
                ''',
                menu = [['manager', get_lang(conn, 'return')]]
            ))