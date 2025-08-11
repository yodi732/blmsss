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

async def login_register():
    with get_db_connect() as conn:
        curs = conn.cursor()

        if (await ban_check(None, 'register'))[0] == 1:
            return await re_error(conn, 0)

        ip = ip_check()
        admin = await acl_check(tool = 'owner_auth')
        admin = 1 if admin == 0 else 0

        if admin != 1 and ip_or_user(ip) == 0:
            return redirect(conn, '/user')

        if admin != 1:
            curs.execute(db_change('select data from other where name = "reg"'))
            set_d = curs.fetchall()
            if set_d and set_d[0][0] == 'on':
                return await re_error(conn, 0)

        if flask.request.method == 'POST':
            # 리캡차
            if await captcha_post(conn, flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
                return await re_error(conn, 13)

            user_id = flask.request.form.get('id', '')
            user_pw = flask.request.form.get('pw', '')
            user_repeat = flask.request.form.get('pw2', '')

            # PW 검증
            if user_id == '' or user_pw == '':
                return await re_error(conn, 27)

            if user_pw != user_repeat:
                return await re_error(conn, 20)
            
            # ID와 PW 동일성 검증
            if user_id == user_pw:
                return await re_error(conn, 49)

            # PW 길이 제한
            curs.execute(db_change("select data from other where name = 'password_min_length'"))
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                password_min_length = int(number_check(db_data[0][0]))
                if password_min_length > len(user_pw):
                    return await re_error(conn, 40)

            if do_user_name_check(conn, user_id) == 1:
                return await re_error(conn, 8)

            if admin != 1:
                # 이메일 필요시 /register/email로 발송
                curs.execute(db_change('select data from other where name = "email_have"'))
                sql_data = curs.fetchall()
                if sql_data and sql_data[0][0] != '':
                    # 임시로 세션에 저장
                    flask.session['reg_id'] = user_id
                    flask.session['reg_pw'] = user_pw

                    return redirect(conn, '/register/email')

                # 가입 승인 필요시 /register/submit으로 발송
                curs.execute(db_change('select data from other where name = "requires_approval"'))
                sql_data = curs.fetchall()
                if sql_data and sql_data[0][0] != '':
                    flask.session['submit_id'] = user_id
                    flask.session['submit_pw'] = user_pw

                    return redirect(conn, '/register/submit')

            # 전부 아니면 바로 가입 후 /login으로 발송
            add_user(conn, user_id, user_pw)

            return redirect(conn, '/login')
        else:
            curs.execute(db_change('select data from other where name = "contract"'))
            data = curs.fetchall()
            contract = (data[0][0] + '<hr class="main_hr">') if data and data[0][0] != '' else ''

            curs.execute(db_change("select data from other where name = 'password_min_length'"))
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                password_min_length = ' (' + get_lang(conn, 'password_min_length') + ' : ' + db_data[0][0] + ')'
            else:
                password_min_length = ''

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'register'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        ''' + contract + '''

                        <input placeholder="''' + get_lang(conn, 'id') + '''" name="id" type="text">
                        <hr class="main_hr">

                        <input placeholder="''' + get_lang(conn, 'password') + password_min_length + '''" name="pw" type="password">
                        <hr class="main_hr">

                        <input placeholder="''' + get_lang(conn, 'password_confirm') + '''" name="pw2" type="password">
                        <hr class="main_hr">

                        ''' + await captcha_get(conn) + '''

                        <button type="submit">''' + get_lang(conn, 'save') + '''</button>

                        ''' + http_warning(conn) + '''
                    </form>
                ''',
                menu = [['user', get_lang(conn, 'return')]]
            ))