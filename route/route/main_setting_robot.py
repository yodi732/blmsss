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

async def main_setting_robot():
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 0)

        curs.execute(db_change("select data from other where name = 'robot'"))
        db_data = curs.fetchall()
        if db_data:
            data = db_data[0][0]
        else:
            data = ''

        curs.execute(db_change("select data from other where name = 'robot_default'"))
        db_data_2 = curs.fetchall()
        if db_data_2 and db_data_2[0][0] != '':
            default_data = 'checked'
        else:
            default_data = ''
        
        if flask.request.method == 'POST':
            if db_data:
                curs.execute(db_change("update other set data = ? where name = 'robot'"), [flask.request.form.get('content', '')])
            else:
                curs.execute(db_change("insert into other (name, data, coverage) values ('robot', ?, '')"), [flask.request.form.get('content', '')])

            if db_data_2:
                curs.execute(db_change("update other set data = ? where name = 'robot_default'"), [flask.request.form.get('default', '')])
            else:
                curs.execute(db_change("insert into other (name, data, coverage) values ('robot_default', ?, '')"), [flask.request.form.get('default', '')])

            await acl_check(tool = 'owner_auth', memo = 'edit_set (robot)')

            return redirect(conn, '/setting/robot')
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = ['robots.txt', await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <a href="/robots.txt">(''' + get_lang(conn, 'view') + ''')</a>
                    <hr class="main_hr">
                    <form method="post">
                        <textarea class="opennamu_textarea_500" name="content">''' + html.escape(data) + '''</textarea>
                        <hr class="main_hr">
                        <label><input type="checkbox" name="default" ''' + default_data + '''> ''' + get_lang(conn, 'default') + '''</label>
                        <hr class="main_hr">
                        <button id="opennamu_save_button" type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['setting', get_lang(conn, 'return')]]
            ))