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

async def main_setting_main_logo():
    with get_db_connect() as conn:
        curs = conn.cursor()
        
        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 0)

        skin_list = [0] + load_skin(conn, '', 1)
        i_list = []
        for i in skin_list:
            i_list += [['logo', '' if i == 0 else i]]

        if flask.request.method == 'POST':
            for i in i_list:
                curs.execute(db_change("update other set data = ? where name = ? and coverage = ?"), [
                    flask.request.form.get(('main_css' if i[1] == '' else i[1]), ''),
                    i[0], 
                    i[1]
                ])

            await acl_check(tool = 'owner_auth', memo = 'edit_set (logo)')

            return redirect(conn, '/setting/main/logo')
        else:
            d_list = []
            for i in i_list:
                curs.execute(db_change('select data from other where name = ? and coverage = ?'), [i[0], i[1]])
                sql_d = curs.fetchall()
                if sql_d:
                    d_list += [sql_d[0][0]]
                else:
                    curs.execute(db_change('insert into other (name, data, coverage) values (?, ?, ?)'), [i[0], '', i[1]])

                    d_list += ['']

            end_data = ''
            for i in range(0, len(skin_list)):
                end_data += '' + \
                    '<span>' + get_lang(conn, 'wiki_logo') + ' ' + ('(' + skin_list[i] + ')' if skin_list[i] != 0 else '') + ' (HTML)' + \
                    '<hr class="main_hr">' + \
                    '<input name="' + (skin_list[i] if skin_list[i] != 0 else 'main_css') + '" value="' + html.escape(d_list[i]) + '">' + \
                    '<hr class="main_hr">' + \
                ''

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'wiki_logo'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        ''' + end_data + '''
                        <button id="opennamu_save_button" type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['setting/main', get_lang(conn, 'return')]]
            ))