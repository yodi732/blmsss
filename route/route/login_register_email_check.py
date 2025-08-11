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

async def login_register_email_check():
    with get_db_connect() as conn:
        curs = conn.cursor()

        if not 'reg_email' in flask.session:
            return redirect(conn, '/register')

        if  flask.request.method == 'POST':
            input_key = flask.request.form.get('key', '')

            if flask.session['reg_key'] != input_key:
                return redirect(conn, '/register')

            curs.execute(db_change('select data from other where name = "requires_approval"'))
            sql_data = curs.fetchall()
            if sql_data and sql_data[0][0] != '':
                flask.session['submit_id'] = flask.session['reg_id']
                flask.session['submit_pw'] = flask.session['reg_pw']
                flask.session['submit_email'] = flask.session['reg_email']

                return redirect(conn, '/register/submit')

            add_user(conn, 
                flask.session['reg_id'],
                flask.session['reg_pw'],
                flask.session['reg_email']
            )

            return redirect(conn, '/login')
        else:
            curs.execute(db_change('select data from other where name = "check_key_text"'))
            sql_d = curs.fetchall()
            b_text = (sql_d[0][0] + '<hr class="main_hr">') if sql_d and sql_d[0][0] != '' else ''

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'check_key'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        ''' + b_text + '''
                        <input placeholder="''' + get_lang(conn, 'key') + '''" name="key" type="text">
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['user', get_lang(conn, 'return')]]
            ))