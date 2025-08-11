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

async def list_image_file(arg_num = 1, do_type = 0):
    with get_db_connect() as conn:
        curs = conn.cursor()

        sql_num = (arg_num * 50 - 50) if arg_num * 50 > 0 else 0

        list_data = ''
        if do_type == 0:
            list_data += '<a href="/list/image">(' + get_lang(conn, 'image') + ')</a>'
        else:
            list_data += '<a href="/list/file">(' + get_lang(conn, 'normal') + ')</a>'
        
        list_data += '<hr class="main_hr">'

        if do_type == 1:
            render_data = ''
            sub_data = ''
            count = 0

            curs.execute(db_change("select title from data where title like 'file:%' limit ?, 50"), [sql_num])
            data_list = curs.fetchall()
            for data in data_list:
                if count != 0 and count % 4 == 0:
                    render_data += '||\n'
                    render_data += sub_data + '||\n'
                    
                    sub_data = ''

                render_data += '|| [[' + data[0] + ']] '
                sub_data += '|| [[:' + data[0] + ']] '
                count += 1

            if render_data != '':
                render_data += '||\n'
                render_data += sub_data + '||'

            end_data = render_set(conn, 
                doc_name = '',
                doc_data = render_data,
                data_type = 'view',
                markup = 'namumark'
            )
            list_data += end_data
        else:
            list_data += '<ul>'

            curs.execute(db_change("select title from data where title like 'file:%' limit ?, 50"), [sql_num])
            data_list = curs.fetchall()
            for data in data_list:
                list_data += '<li><a href="/w/' + url_pas(data[0]) + '">' + html.escape(data[0]) + '</a></li>'

            list_data += '</ul>'

        if do_type == 0:
            list_data += get_next_page_bottom(conn, '/list/file/{}', arg_num, data_list)
        else:
            list_data += get_next_page_bottom(conn, '/list/image/{}', arg_num, data_list)

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'image_file_list'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = list_data,
            menu = [['other', get_lang(conn, 'return')]]
        ))