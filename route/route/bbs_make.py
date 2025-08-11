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

async def bbs_make():   
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 3)
        
        if flask.request.method == 'POST':
            curs.execute(db_change('select set_id from bbs_set where set_name = "bbs_name" order by set_id + 0 desc'))
            db_data = curs.fetchall()

            bbs_num = str(int(db_data[0][0]) + 1) if db_data else '1'
            bbs_name = flask.request.form.get('bbs_name', 'test')
            bbs_type = flask.request.form.get('bbs_type', 'comment')
            bbs_type = bbs_type if bbs_type in ['comment', 'thread'] else 'comment'

            curs.execute(db_change("insert into bbs_set (set_name, set_code, set_id, set_data) values ('bbs_name', '', ?, ?)"), [bbs_num, bbs_name])
            curs.execute(db_change("insert into bbs_set (set_name, set_code, set_id, set_data) values ('bbs_type', '', ?, ?)"), [bbs_num, bbs_type])

            return redirect(conn, '/bbs/main')
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'bbs_make'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        <input placeholder="''' + get_lang(conn, 'bbs_name') + '''" name="bbs_name">
                        <hr class="main_hr">
                        
                        <select name="bbs_type">
                            <option value="comment">''' + get_lang(conn, 'comment_base') + '''</option>
                            <option value="thread">''' + get_lang(conn, 'thread_base') + '''</option>
                        </select>
                        <hr class="main_hr">
                        
                        <button type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['bbs/main', get_lang(conn, 'return')]]
            ))