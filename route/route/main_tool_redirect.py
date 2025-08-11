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

async def main_tool_redirect(num = 1, add_2 = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        title_list = {
            0 : [get_lang(conn, 'document_name'), '/acl', get_lang(conn, 'document_setting')],
            1 : [0, '/list/user/check', get_lang(conn, 'check')],
            2 : [get_lang(conn, 'file_name'), '/filter/file_filter/add', get_lang(conn, 'file_filter_add')],
            3 : [0, '/auth/give', get_lang(conn, 'authorize')],
            4 : [0, '/user', get_lang(conn, 'user_tool')],
            6 : [get_lang(conn, 'name'), '/auth/list/add', get_lang(conn, 'add_admin_group')],
            7 : [get_lang(conn, 'name'), '/filter/edit_filter/add', get_lang(conn, 'edit_filter_add')],
            8 : [get_lang(conn, 'document_name'), '/search', get_lang(conn, 'search')],
            9 : [0, '/recent_block/user', get_lang(conn, 'blocked_user')],
            10 : [0, '/recent_block/admin', get_lang(conn, 'blocked_admin')],
            11 : [get_lang(conn, 'document_name'), '/watch_list', get_lang(conn, 'add_watchlist')],
            12 : [get_lang(conn, 'compare_target'), '/list/user/check', get_lang(conn, 'compare_target')],
            13 : [get_lang(conn, 'document_name'), '/edit', get_lang(conn, 'load')],
            14 : [get_lang(conn, 'document_name'), '/star_doc', get_lang(conn, 'add_star_doc')],
            16 : [0, '/auth/give/fix', get_lang(conn, 'user_fix')],
            17 : [get_lang(conn, 'search'), '/recent_block/all/1', get_lang(conn, 'search')],
        }
        
        if num == 1:
            return redirect(conn, '/manager')
        
        # 이전 버전 잔재로 -2부터 시작
        num -= 2
        if not num in title_list:
            return redirect(conn)

        add_1 = flask.request.form.get('name', 'test')
        if flask.request.method == 'POST':
            if add_2 != '':
                if num != 12:
                    flask.session['edit_load_document'] = add_1
                    return redirect(conn, '/edit_from/' + url_pas(add_2))
                else:
                    return redirect(conn, title_list[num][1] + '/' + url_pas(add_2) + '/normal/1/' + url_pas(add_1))
            else:
                return redirect(conn, title_list[num][1] + '/' + url_pas(add_1))
        else:
            if title_list[num][0] == 0:
                placeholder = get_lang(conn, 'user_name')
            else:
                placeholder = title_list[num][0]

            top_plus = ''
            if num == 13:
                curs.execute(db_change("select html, plus from html_filter where kind = 'template'"))
                db_data = curs.fetchall()
                for for_a in db_data:
                    top_plus += '' + \
                        '<a href="javascript:opennamu_insert_v(\'data_field\', \'' + get_tool_js_safe(for_a[0]) + '\')">' + html.escape(for_a[0]) + '</a> : ' + html.escape(for_a[1]) + \
                        '<hr class="main_hr">' + \
                    ''

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [title_list[num][2], await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        ''' + top_plus + '''
                        <input placeholder="''' + placeholder + '''" id="data_field" name="name" type="text">
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'go') + '''</button>
                    </form>
                ''',
                menu = [['manager', get_lang(conn, 'return')]]
            ))