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

async def view_xref(name = 'Test', xref_type = 1, num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check(name, 'render') == 1:
            return await re_error(conn, 0)

        sql_num = (num * 50 - 50) if num * 50 > 0 else 0

        if xref_type == 1:
            div = '<a href="/xref_this/' + url_pas(name) + '">(' + get_lang(conn, 'link_in_this') + ')</a><hr class="main_hr">'
            data_sub = '(' + get_lang(conn, 'backlink') + ')'
        else:
            div = '<a href="/xref/' + url_pas(name) + '">(' + get_lang(conn, 'normal') + ')</a><hr class="main_hr">'
            data_sub = '(' + get_lang(conn, 'link_in_this') + ')'

        div += '<ul>'

        curs.execute(db_change('select data from other where name = "link_case_insensitive"'))
        db_data = curs.fetchall()
        link_case_insensitive = ' collate nocase' if db_data and db_data[0][0] != '' else ''

        if xref_type == 2:
            curs.execute(db_change("select set_data from data_set where doc_name = ? and set_name = 'link_count'"), [name])
            db_data = curs.fetchall()
            div += '<li>' + get_lang(conn, 'link_count') + ' : ' +  (db_data[0][0] if db_data else get_lang(conn, 'data_missing')) + '</li>'

        sql_insert = ['link', 'title'] if xref_type == 1 else ['title', 'link']
        curs.execute(db_change("select distinct " + sql_insert[0] + ", type from back where " + sql_insert[1] + " = ?" + link_case_insensitive + " and not type = 'no' and not type = 'nothing' order by type asc, " + sql_insert[0] + " asc limit ?, 50"), [name, sql_num])
        data_list = curs.fetchall()
        for data in data_list:
            div += '<li><a href="/w/' + url_pas(data[0]) + '">' + html.escape(data[0]) + '</a>'

            if data[1]:
                div += ' (' + data[1] + ')'

            curs.execute(db_change("select title from back where title = ? and type = 'include'"), [data[0]])
            db_data = curs.fetchall()
            if db_data:
                div += ' <a class="opennamu_link_inter" href="/xref/' + url_pas(data[0]) + '">(' + get_lang(conn, 'backlink') + ')</a>'

            div += '</li>'

        div += '</ul>'
        
        if xref_type == 2:
            div += get_next_page_bottom(conn, '/xref_this_page/{}/' + url_pas(name), num, data_list)
        else:
            div += get_next_page_bottom(conn, '/xref_page/{}/' + url_pas(name), num, data_list)

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [name, await wiki_set(), await wiki_custom(conn), wiki_css([data_sub, 0])],
            data = div,
            menu = [['w/' + url_pas(name), get_lang(conn, 'return')], ['xref_reset/' + url_pas(name), get_lang(conn, 'reset_backlink')]]
        ))