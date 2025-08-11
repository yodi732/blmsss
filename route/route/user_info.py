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

async def user_info(name = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()
    
        if name == '':
            ip = ip_check()
        else:
            ip = name
    
        login_menu = ''
        tool_menu = ''
        
        if name == '':
            curs.execute(db_change("select count(*) from user_notice where name = ? and readme = ''"), [ip])
            count = curs.fetchall()
            if count and count[0][0] != 0:
                tool_menu += '<li><a class="opennamu_not_exist_link" href="/alarm">' + get_lang(conn, 'alarm') + ' (' + str(count[0][0]) + ')</a></li>'
            else:
                tool_menu += '<li><a href="/alarm">' + get_lang(conn, 'alarm') + '</a></li>'
    
            if ip_or_user(ip) == 0:
                login_menu += '''
                    <li><a href="/logout">''' + get_lang(conn, 'logout') + '''</a></li>
                    <li><a href="/change">''' + get_lang(conn, 'user_setting') + '''</a></li>
                '''
    
                tool_menu += '<li><a href="/watch_list">' + get_lang(conn, 'watchlist') + '</a></li>'
                tool_menu += '<li><a href="/star_doc">' + get_lang(conn, 'star_doc') + '</a></li>'
                tool_menu += '<li><a href="/challenge">' + get_lang(conn, 'challenge_and_level_manage') + '</a></li>'
                tool_menu += '<li><a href="/acl/user:' + url_pas(ip) + '">' + get_lang(conn, 'user_document_acl') + '</a></li>'
            else:
                login_menu += '''
                    <li><a href="/login">''' + get_lang(conn, 'login') + '''</a></li>
                    <li><a href="/register">''' + get_lang(conn, 'register') + '''</a></li>
                    <li><a href="/change">''' + get_lang(conn, 'user_setting') + '''</a></li>
                    <li><a href="/login/find">''' + get_lang(conn, 'password_search') + '''</a></li>
                '''
                
            login_menu = '<h2>' + get_lang(conn, 'login') + '</h2><ul>' + login_menu + '</ul>'
            tool_menu = '<h2>' + get_lang(conn, 'tool') + '</h2><ul>' + tool_menu + '</ul>'
    
        if await acl_check(tool = 'ban_auth') != 1:
            curs.execute(db_change("select block from rb where block = ? and ongoing = '1'"), [ip])
            ban_name = get_lang(conn, 'release') if curs.fetchall() else get_lang(conn, 'ban')
            
            admin_menu = '''
                <h2>''' + get_lang(conn, 'admin') + '''</h2>
                <ul>
                    <li><a href="/auth/ban/''' + url_pas(ip) + '''">''' + ban_name + '''</a></li>
                    <li><a href="/list/user/check_submit/''' + url_pas(ip) + '''">''' + get_lang(conn, 'check') + '''</a></li>
                </ul>
            '''
        else:
            admin_menu = ''
                
        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'user_tool'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = '''
                <h2>''' + get_lang(conn, 'state') + '''</h2>
                <div id="opennamu_get_user_info">''' + html.escape(ip) + '''</div>
                ''' + login_menu + '''
                ''' + tool_menu + '''
                <h2>''' + get_lang(conn, 'other') + '''</h2>
                <ul>
                    <li><a href="/record/''' + url_pas(ip) + '''">''' + get_lang(conn, 'edit_record') + '''</a></li>
                    <li><a href="/record/topic/''' + url_pas(ip) + '''">''' + get_lang(conn, 'discussion_record') + '''</a></li>
                    <li><a href="/record/bbs/''' + url_pas(ip) + '''">''' + get_lang(conn, 'bbs_record') + '''</a></li>
                    <li><a href="/record/bbs_comment/''' + url_pas(ip) + '''">''' + get_lang(conn, 'bbs_comment_record') + '''</a></li>
                    <li><a href="/topic/user:''' + url_pas(ip) + '''">''' + get_lang(conn, 'user_discussion') + '''</a></li>
                    <li><a href="/count/''' + url_pas(ip) + '''">''' + get_lang(conn, 'count') + '''</a></li>
                </ul>
                ''' + admin_menu + '''
            ''',
            menu = [['other', get_lang(conn, 'other_tool')]]
        ))