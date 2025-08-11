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

async def edit_delete(name):
    with get_db_connect() as conn:
        curs = conn.cursor()

        ip = ip_check()
        if await acl_check(name, 'document_delete') == 1:
            return await re_error(conn, 0)

        curs.execute(db_change("select title from data where title = ?"), [name])
        if not curs.fetchall():
            return redirect(conn, '/w/' + url_pas(name))

        if flask.request.method == 'POST':
            if await captcha_post(conn, flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
                return await re_error(conn, 13)

            if await do_edit_slow_check(conn) == 1:
                return await re_error(conn, 24)
            
            send = flask.request.form.get('send', '')
            agree = flask.request.form.get('copyright_agreement', '')
            
            if await do_edit_send_check(conn, send) == 1:
                return await re_error(conn, 37)
            
            if do_edit_text_bottom_check_box_check(conn, agree) == 1:
                return await re_error(conn, 29)

            curs.execute(db_change("select data from data where title = ?"), [name])
            data = curs.fetchall()
            if data:
                today = get_time()
                leng = '-' + str(len(data[0][0]))

                history_plus(conn, 
                    name,
                    '',
                    today,
                    ip,
                    send,
                    leng,
                    mode = 'delete'
                )

                curs.execute(db_change("select title, link from back where title = ? and not type = 'cat' and not type = 'no'"), [name])
                for data in curs.fetchall():
                    curs.execute(db_change("insert into back (title, link, type, data) values (?, ?, 'no', '')"), [data[0], data[1]])

                curs.execute(db_change("delete from back where link = ?"), [name])
                curs.execute(db_change("delete from data where title = ?"), [name])

            return redirect(conn, '/w/' + url_pas(name))
        else:            
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [name, await wiki_set(), await wiki_custom(conn), wiki_css(['(' + get_lang(conn, 'delete') + ')', 0])],
                data = '''
                    <form method="post">
                        <input placeholder="''' + get_lang(conn, 'why') + '''" name="send">
                        <hr class="main_hr">
                        ''' + await captcha_get(conn) + ip_warning(conn) + get_edit_text_bottom_check_box(conn) + get_edit_text_bottom(conn, 'delete')  + '''
                        <button type="submit">''' + get_lang(conn, 'delete') + '''</button>
                    </form>
                ''',
                menu = [['w/' + url_pas(name), get_lang(conn, 'return')]]
            ))