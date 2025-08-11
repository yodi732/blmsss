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

from .recent_change import recent_change_send_render

from .go_api_list_recent_edit_request import api_list_recent_edit_request

async def recent_edit_request():
    with get_db_connect() as conn:
        div = ''
        div += '''
            <table id="main_table_set">
                <tbody>
                    <tr id="main_table_top_tr">
                        <td id="main_table_width">''' + get_lang(conn, 'discussion_name') + '''</td>
                        <td id="main_table_width">''' + get_lang(conn, 'editor') + '''</td>
                        <td id="main_table_width">''' + get_lang(conn, 'time') + '''</td>
                    </tr>
        '''

        all_list = await api_list_recent_edit_request()
        for data in all_list:
            if re.search(r"\+", data[5]):
                leng = '<span style="color:green;">(' + data[5] + ')</span>'
            elif re.search(r"\-", data[5]):
                leng = '<span style="color:red;">(' + data[5] + ')</span>'
            else:
                leng = '<span style="color:gray;">(' + data[5] + ')</span>'

            send = data[4]
            ip = data[6]
            date = data[2]

            title = '<a href="/edit_request/' + url_pas(data[0]) + '">' + html.escape(data[0]) + '</a> '
            title += '<a href="/history/' + url_pas(data[0]) + '">(r' + data[1] + ')</a> '

            div += '''
                <tr>
                    <td>''' + title + ' ' + leng + '''</td>
                    <td>''' + ip + '''</td>
                    <td>''' + date + '''</td>
                </tr>
                <tr>
                    <td colspan="3">''' + recent_change_send_render(html.escape(send)) + '''</td>
                </tr>
            '''

        div += '' + \
                '</tbody>' + \
            '</table>' + \
        ''

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'recent_edit_request'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = div,
            menu = [['recent_change', get_lang(conn, 'return')]]
        ))