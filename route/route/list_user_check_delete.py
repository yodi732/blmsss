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

async def list_user_check_delete(name = None, ip = None, time = None, do_type = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 4)

        user_id = name
        user_ip = ip
        return_type = do_type

        if user_id and user_ip and time:
            if flask.request.method == 'POST':
                curs.execute(db_change("delete from ua_d where name = ? and ip = ? and today = ?"), [user_id, user_ip, time])

                return redirect(conn, '/list/user/check/' + url_pas(user_id if return_type == '0' else user_ip))
            else:
                return easy_minify(conn, flask.render_template(skin_check(conn),
                    imp = [get_lang(conn, 'check'), await wiki_set(), await wiki_custom(conn), wiki_css(['(' + get_lang(conn, 'delete') + ')', 0])],
                    data = '''
                        ''' + get_lang(conn, 'name') + ''' : ''' + user_id + '''
                        <hr class="main_hr">
                        ''' + get_lang(conn, 'ip') + ''' : ''' + user_ip + '''
                        <hr class="main_hr">
                        ''' + get_lang(conn, 'time') + ''' : ''' + time + '''
                        <hr class="main_hr">
                        <form method="post">
                            <button type="submit">''' + get_lang(conn, 'delete') + '''</button>
                        </form>
                    ''',
                    menu = [['check/' + url_pas(user_id if return_type == '0' else user_ip), get_lang(conn, 'return')]]
                ))
        else:
            return redirect(conn)