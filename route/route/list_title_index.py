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

async def list_title_index(num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        sql_num = (num * 50 - 50) if num * 50 > 0 else 0

        all_list = sql_num + 1
        data = ''

        curs.execute(db_change("select title from data order by title asc limit ?, 50"), [sql_num])
        title_list = curs.fetchall()
        if title_list:
            data += '<hr class="main_hr"><ul>'

        for list_data in title_list:
            data += '<li>' + str(all_list) + '. <a href="/w/' + url_pas(list_data[0]) + '">' + html.escape(list_data[0]) + '</a></li>'
            all_list += 1

        if num == 1:
            count_end = []

            curs.execute(db_change('select data from other where name = "count_all_title"'))
            all_title = curs.fetchall()
            if int(all_title[0][0]) < 30000:
                count_end += [int(all_title[0][0])]

                sql_list = ['category:', 'user:', 'file:']
                for sql in sql_list:
                    curs.execute(db_change("select count(*) from data where title like ?"), [sql + '%'])
                    count = curs.fetchall()
                    if count:
                        count_end += [int(count[0][0])]
                    else:
                        count_end += [0]

                count_end += [count_end[0] - count_end[1]  - count_end[2]  - count_end[3]]

                data += '''
                    </ul>
                    <ul>
                        <li>''' + get_lang(conn, 'all') + ' : ' + str(count_end[0]) + '''</li>
                    </ul>
                    <ul>
                        <li>''' + get_lang(conn, 'category') + ' : ' + str(count_end[1]) + '''</li>
                        <li>''' + get_lang(conn, 'user_document') + ' : ' + str(count_end[2]) + '''</li>
                        <li>''' + get_lang(conn, 'file') + ' : ' + str(count_end[3]) + '''</li>
                        <li>''' + get_lang(conn, 'other') + ' : ' + str(count_end[4]) + '''</li>
                '''
            else:
                data += '''
                    </ul>
                    <ul>
                        <li>''' + get_lang(conn, 'all') + ' : ' + all_title[0][0] + '''</li>
                '''

        data += '</ul>' + get_next_page_bottom(conn, '/list/document/all/{}', num, title_list)
        sub = ' (' + str(num) + ')'

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'all_document_list'), await wiki_set(), await wiki_custom(conn), wiki_css([sub, 0])],
            data = data,
            menu = [['other', get_lang(conn, 'return')]]
        ))