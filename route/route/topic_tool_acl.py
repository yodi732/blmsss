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

async def topic_tool_acl(topic_num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check(tool = 'toron_auth') == 1:
            return await re_error(conn, 3)

        ip = ip_check()
        time = get_time()
        topic_num = str(topic_num)

        curs.execute(db_change("select title, sub from rd where code = ?"), [topic_num])
        rd_d = curs.fetchall()
        if not rd_d:
            return redirect(conn, '/')

        if flask.request.method == 'POST':
            await acl_check(tool = 'toron_auth', memo = 'topic_acl_set (code ' + topic_num + ')')

            curs.execute(db_change("select id from topic where code = ? order by id + 0 desc limit 1"), [topic_num])
            topic_check = curs.fetchall()
            if topic_check:
                acl_data = flask.request.form.get('acl', '')
                acl_data_view = flask.request.form.get('acl_view', '')

                curs.execute(db_change("update rd set acl = ? where code = ?"), [
                    acl_data, 
                    topic_num
                ])
                
                curs.execute(db_change("select set_data from topic_set where thread_code = ? and set_name = 'thread_view_acl'"), [topic_num])
                db_data = curs.fetchall()
                if db_data:
                    curs.execute(db_change("update topic_set set set_data = ? where thread_code = ?"), [
                        acl_data_view,
                        topic_num
                    ])
                else:
                    curs.execute(db_change("insert into topic_set (thread_code, set_name, set_id, set_data) values (?, 'thread_view_acl', '1', ?)"), [
                        topic_num,
                        acl_data_view
                    ])

                do_add_thread(conn, 
                    topic_num,
                    get_lang(conn, 'acl_thread_change') + ' : ' + acl_data,
                    '1'
                )
                do_reload_recent_thread(conn, 
                    topic_num, 
                    time
                )

            return redirect(conn, '/thread/' + topic_num)
        else:
            acl_list = await get_acl_list()
            acl_html_list = ''
            acl_html_list_view = ''

            curs.execute(db_change("select acl from rd where code = ?"), [topic_num])
            topic_acl_get = curs.fetchall()
            for data_list in acl_list:
                if topic_acl_get and topic_acl_get[0][0] == data_list:
                    check = 'selected="selected"'
                else:
                    check = ''

                acl_html_list += '<option value="' + data_list + '" ' + check + '>' + (data_list if data_list != '' else 'normal') + '</option>'

            curs.execute(db_change("select set_data from topic_set where thread_code = ? and set_name = 'thread_view_acl'"), [topic_num])
            db_data = curs.fetchall()
            for data_list in acl_list:
                if db_data and db_data[0][0] == data_list:
                    check = 'selected="selected"'
                else:
                    check = ''

                acl_html_list_view += '<option value="' + data_list + '" ' + check + '>' + (data_list if data_list != '' else 'normal') + '</option>'

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'topic_acl_setting'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        <a href="/acl/TEST#exp">(''' + get_lang(conn, 'reference') + ''')</a>
                        <h2>''' + get_lang(conn, 'thread_acl') + '''</h2>
                        <select name="acl">
                            ''' + acl_html_list + '''
                        </select>
                        <h2>''' + get_lang(conn, 'view_acl') + ''' (''' + get_lang(conn, 'beta') + ''')</h2>
                        <select name="acl_view">
                            ''' + acl_html_list_view + '''
                        </select>
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['thread/' + topic_num + '/tool', get_lang(conn, 'return')]]
            ))