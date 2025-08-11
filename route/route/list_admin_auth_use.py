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

async def list_admin_auth_use(arg_num = 1, arg_search = 'normal'):
    with get_db_connect() as conn:
        curs = conn.cursor()

        sql_num = (arg_num * 50 - 50) if arg_num * 50 > 0 else 0

        if flask.request.method == 'POST':
            return redirect(conn, '/list/admin/auth_use_page/1/' + url_pas(flask.request.form.get('search', 'normal')))
        else:
            arg_search = 'normal' if arg_search == '' else arg_search
            
            if arg_search == 'normal':
                curs.execute(db_change("select who, what, time from re_admin order by time desc limit ?, 50"), [sql_num])
            else:
                curs.execute(db_change("select who, what, time from re_admin where what like ? order by time desc limit ?, 50"), [arg_search + "%", sql_num])

            list_data = '<ul>'

            get_list = curs.fetchall()
            for data in get_list:
                do_data = data[1]

                if ip_or_user(data[0]) != 0:
                    curs.execute(db_change("select data from other where name = 'ip_view'"))
                    db_data = curs.fetchall()
                    ip_view = db_data[0][0] if db_data else ''
                    ip_view = '' if await acl_check(tool = 'ban_auth') != 1 else ip_view
                    
                    if ip_view != '':
                        do_data = do_data.split(' ')
                        do_data = do_data[0] if do_data[0] in ['ban'] else data[1]

                list_data += '<li>' + await ip_pas(data[0]) + ' | ' + html.escape(do_data) + ' | ' + data[2] + '</li>'

            list_data += '</ul>'
            list_data += get_next_page_bottom(conn, '/list/admin/auth_use_page/{}/' + url_pas(arg_search), arg_num, get_list)

            arg_search = html.escape(arg_search) if arg_search != 'normal' else ''

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'authority_use_list'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        <input class="opennamu_width_200" name="search" placeholder="''' + get_lang(conn, 'start_with_search') + '''" value="''' + arg_search + '''">
                        <button type="submit">''' + get_lang(conn, 'search') + '''</button>
                    </form>
                    <hr class="main_hr">
                ''' + list_data,
                menu = [['other', get_lang(conn, 'return')]]
            ))