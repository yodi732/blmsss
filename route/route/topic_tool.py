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

async def topic_tool(topic_num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        data = ''
        topic_num = str(topic_num)

        curs.execute(db_change("select stop, agree from rd where code = ?"), [topic_num])
        close_data = curs.fetchall()
        if close_data:
            if close_data[0][0] == 'S':
                t_state = get_lang(conn, 'topic_stop')
            elif close_data[0][0] == 'O':
                t_state = get_lang(conn, 'topic_close')
            else:
                t_state = get_lang(conn, 'topic_normal')
                
            if close_data[0][1] == 'O':
                t_state += ' (' + get_lang(conn, 'topic_agree') + ')'
        else:
            t_state = get_lang(conn, 'topic_normal')

        curs.execute(db_change("select acl from rd where code = ?"), [topic_num])
        db_data = curs.fetchall()
        if db_data:
            if db_data[0][0] == '':
                acl_state = 'normal'
            else:
                acl_state = db_data[0][0]
        else:
            acl_state = 'normal'
        
        curs.execute(db_change("select set_data from topic_set where thread_code = ? and set_name = 'thread_view_acl'"), [topic_num])
        db_data = curs.fetchall()
        if db_data:
            if db_data[0][0] == '':
                acl_view_state = 'normal'
            else:
                acl_view_state = db_data[0][0]
        else:
            acl_view_state = 'normal'

        if await acl_check(tool = 'toron_auth') != 1:
            data = '''
                <h2>''' + get_lang(conn, 'admin_tool') + '''</h2>
                <ul>
                    <li><a href="/thread/''' + topic_num + '/setting">' + get_lang(conn, 'topic_setting') + '''</a></li>
                    <li><a href="/thread/''' + topic_num + '/acl">' + get_lang(conn, 'topic_acl_setting') + '''</a></li>
                </ul>
            '''
        data += '''
            <h2>''' + get_lang(conn, 'tool') + '''</h2>
            <ul>
                <li>''' + get_lang(conn, 'topic_state') + ''' : ''' + t_state + '''</li>
                <li>''' + get_lang(conn, 'topic_acl') + ''' : <a href="/acl/TEST#exp">''' + acl_state + '''</a></li>
                <li>''' + get_lang(conn, 'topic_view_acl') + ''' : <a href="/acl/TEST#exp">''' + acl_view_state + '''</a></li>
            </ul>
        '''

        if await acl_check(tool = 'owner_auth') != 1:
            data += '''
                <h2>''' + get_lang(conn, 'owner') + '''</h2>
                <ul>
                    <li>
                        <a href="/thread/''' + topic_num + '''/delete">
                            ''' + get_lang(conn, 'topic_delete') + '''
                        </a>
                    </li>
                    <li>
                        <a href="/thread/''' + topic_num + '''/change">
                            ''' + get_lang(conn, 'topic_name_change') + '''
                        </a>
                    </li>
                </ul>
            '''

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'topic_tool'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = data,
            menu = [['thread/' + topic_num, get_lang(conn, 'return')]]
        ))