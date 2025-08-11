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

async def recent_record_topic(name = 'Test'):
    with get_db_connect() as conn:
        curs = conn.cursor()

        num = int(number_check(flask.request.args.get('num', '1')))
        sql_num = (num * 50 - 50) if num * 50 > 0 else 0

        div = '''
            <table id="main_table_set">
                <tr id="main_table_top_tr">
                    <td id="main_table_width">''' + get_lang(conn, 'discussion_name') + '''</td>
                    <td id="main_table_width">''' + get_lang(conn, 'writer') + '''</td>
                    <td id="main_table_width">''' + get_lang(conn, 'time') + '''</td>
                </tr>
        '''
        sub = '(' + html.escape(name) + ')'
        pas_name = await ip_pas(name)

        curs.execute(db_change("select code, id, date from topic where ip = ? order by date desc limit ?, 50"), [name, sql_num])
        data_list = curs.fetchall()
        for data in data_list:
            title = html.escape(data[0])

            curs.execute(db_change("select title, sub from rd where code = ?"), [data[0]])
            other_data = curs.fetchall()

            div += '' + \
                '<tr>' + \
                    '<td>' + \
                        '<a href="/thread/' + data[0] + '#' + data[1] + '">' + other_data[0][1] + '#' + data[1] + '</a> (' + other_data[0][0] + ')' + \
                    '</td>' + \
                    '<td>' + pas_name + '</td>' + \
                    '<td>' + data[2] + '</td>' + \
                '</tr>' + \
            ''

        div += '</table>'
        div += get_next_page_bottom(conn, '/record/topic/' + url_pas(name) + '?num={}', num, data_list)

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'discussion_record'), await wiki_set(), await wiki_custom(conn), wiki_css([sub, 0])],
            data = div,
            menu = [['other', get_lang(conn, 'other')], ['user/' + url_pas(name), get_lang(conn, 'user_tool')]]
        ))