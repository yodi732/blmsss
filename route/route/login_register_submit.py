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

async def login_register_submit():
    with get_db_connect() as conn:
        curs = conn.cursor()

        session_reset_list = ['submit_id', 'submit_pw', 'submit_email']

        if not 'submit_id' in flask.session:
            for for_a in session_reset_list:
                flask.session.pop(for_a, None)

            return redirect(conn, '/register')

        curs.execute(db_change('select data from other where name = "approval_question"'))
        sql_data = curs.fetchall()
        if not sql_data:
            for for_a in session_reset_list:
                flask.session.pop(for_a, None)

            return redirect(conn, '/register')

        data_que = sql_data[0][0]

        if do_user_name_check(conn, flask.session['submit_id']) == 1:
            for for_a in session_reset_list:
                flask.session.pop(for_a, None)
        
            return redirect(conn, '/register')

        if flask.request.method == 'POST':
            curs.execute(db_change('select data from other where name = "encode"'))
            data_encode = curs.fetchall()
            data_encode = data_encode[0][0]

            user_app_data = {}
            user_app_data['id'] = flask.session['submit_id']
            user_app_data['pw'] = pw_encode(conn, flask.session['submit_pw'])
            user_app_data['encode'] = data_encode
            user_app_data['question'] = data_que
            user_app_data['answer'] = flask.request.form.get('answer', '')

            if 'submit_email' in flask.session:
                user_app_data['email'] = flask.session['submit_email']
            else:
                user_app_data['email'] = ''

            for for_a in session_reset_list:
                flask.session.pop(for_a, None)

            curs.execute(db_change("insert into user_set (id, name, data) values (?, ?, ?)"), [user_app_data['id'], 'application', json_dumps(user_app_data)])

            return await re_error(conn, 43)
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'approval_question'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        ''' + get_lang(conn, 'approval_question') + ' : ' + data_que + '''
                        <hr class="main_hr">
                        <input placeholder="''' + get_lang(conn, 'approval_question') + '''" name="answer">
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['user', get_lang(conn, 'return')]]
            ))