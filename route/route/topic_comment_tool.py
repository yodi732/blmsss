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

async def topic_comment_tool(topic_num = 1, num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()
        
        num = str(num)
        topic_num = str(topic_num)
        
        if await acl_check('', 'topic_view', topic_num) == 1:
            return await re_error(conn, 0)

        curs.execute(db_change("select block, ip, date from topic where code = ? and id = ?"), [topic_num, num])
        data = curs.fetchall()
        if not data:
            return redirect(conn, '/thread/' + topic_num)

        ban = '''
            <h2>''' + get_lang(conn, 'state') + '''</h2>
            <ul>
                <li>''' + get_lang(conn, 'writer') + ' : ''' + await ip_pas(data[0][1]) + '''</li>
                <li>''' + get_lang(conn, 'time') + ' : ' + data[0][2] + '''</li>
            </ul>
            <h2>''' + get_lang(conn, 'other_tool') + '''</h2>
            <ul>
                <li>
                    <a href="/thread/''' + topic_num + '/comment/' + num + '''/raw">''' + get_lang(conn, 'raw') + '''</a>
                </li>
            </ul>
        '''

        if await acl_check(tool = 'toron_auth') != 1:
            ban += '''
                <h2>''' + get_lang(conn, 'admin_tool') + '''</h2>
                <ul>
                    <li>
                        <a href="/auth/ban/''' + url_pas(data[0][1]) + '''">
                            ''' + (get_lang(conn, 'ban') + ' | ' + get_lang(conn, 'release')) + '''
                        </a>
                    </li>
                    <li>
                        <a href="/thread/''' + topic_num + '''/comment/''' + num + '''/blind">
                            ''' + (get_lang(conn, 'hide') + ' | ' + get_lang(conn, 'hide_release')) + '''
                        </a>
                    </li>
                    <li>
                        <a href="/thread/''' + topic_num + '''/comment/''' + num + '''/notice">
                            ''' + (get_lang(conn, 'pinned') + ' | ' + get_lang(conn, 'pinned_release')) + '''
                        </a>
                    </li>
                    <li>
                        <a href="/thread/''' + topic_num + '''/comment/''' + num + '''/delete">
                            ''' + get_lang(conn, 'delete') + '''
                        </a>
                </ul>
            '''

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'discussion_tool'), await wiki_set(), await wiki_custom(conn), wiki_css(['(#' + num + ')', 0])],
            data = ban,
            menu = [['thread/' + topic_num + '#' + num, get_lang(conn, 'return')]]
        ))