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

async def login_login_2fa_email():
    with get_db_connect() as conn:
        curs = conn.cursor()

        # email 2fa
        # pw 2fa
        # q_a 2fa
        if not (flask.session and 'login_id' in flask.session):
            return redirect(conn, '/user')

        ip = ip_check()
        if ip_or_user(ip) == 0:
            return redirect(conn, '/user')

        if (await ban_check(None, 'login'))[0] == 1:
            return await re_error(conn, 0)

        if flask.request.method == 'POST':
            if await captcha_post(conn, flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
                return await re_error(conn, 13)

            user_agent = flask.request.headers.get('User-Agent', '')
            user_id = flask.session['b_id']
            user_pw = flask.request.form.get('pw', '')

            curs.execute(db_change('select data from user_set where name = "2fa_pw" and id = ?'), [user_id])
            user_1 = curs.fetchall()
            if user_1:
                curs.execute(db_change('select data from user_set where name = "2fa_pw_encode" and id = ?'), [user_id])
                user_1 = user_1[0][0]
                user_2 = curs.fetchall()[0][0]

                pw_check_d = pw_check(conn, user_pw, user_1, user_2, user_id)
                if pw_check_d != 1:
                    return await re_error(conn, 10)

            flask.session['id'] = user_id

            ua_plus(conn, user_id, ip, user_agent, get_time())

            flask.session.pop('b_id', None)

            return redirect(conn, '/user')
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'login'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data =  '''
                        <form method="post">
                            <input placeholder="''' + get_lang(conn, '2fa_password') + '''" name="pw" type="password">
                            <hr class=\"main_hr\">
                            ''' + await captcha_get(conn) + '''
                            <button type="submit">''' + get_lang(conn, 'login') + '''</button>
                            ''' + http_warning(conn) + '''
                        </form>
                        ''',
                menu = [['user', get_lang(conn, 'return')]]
            ))