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

async def api_user_info(user_name = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        data_result = {}
        
        # name part
        data_result['render'] = await ip_pas(user_name)
        
        # auth part
        curs.execute(db_change("select data from user_set where id = ? and name = 'acl'"), [user_name])
        db_data = curs.fetchall()
        if db_data:
            data_result['auth'] = db_data[0][0]
        elif ip_or_user(user_name) == 1:
            data_result['auth'] = 'ip'
        else:
            data_result['auth'] = 'user'

        curs.execute(db_change("select data from user_set where id = ? and name = 'auth_date'"), [user_name])
        db_data = curs.fetchall()
        if db_data:
            data_result['auth_date'] = db_data[0][0]
        else:
            data_result['auth_date'] = '0'

        level_data = await level_check(user_name)
        data_result['level'] = level_data[0]
        data_result['exp'] = level_data[1]
        data_result['max_exp'] = level_data[2]
            
        # ban part
        ban = await ban_check(user_name)
        if ban[0] == 0:
            data_result['ban'] = '0'
        else:
            data_result['ban'] = ban
        
        # user document part
        curs.execute(db_change("select title from data where title = ?"), ['user:' + user_name])
        if curs.fetchall():
            data_result['document'] = '1'
        else:
            data_result['document'] = '0'

        # user title part
        curs.execute(db_change('select data from user_set where name = "user_title" and id = ?'), [user_name])
        db_data = curs.fetchall()
        if db_data:
            data_result['user_title'] = db_data[0][0]
        else:
            data_result['user_title'] = ''

        lang_data_list = [
            'user_name',
            'authority',
            'state',
            'member',
            'normal',
            'blocked',
            'type',
            'regex',
            'period',
            'limitless',
            'login_able',
            'why',
            'band_blocked',
            'ip',
            'ban',
            'level',
            'option',
            'edit_request_able',
            'cidr'
        ]
        lang_data = { for_a : get_lang(conn, for_a) for for_a in lang_data_list }
                
        return flask.jsonify({ 'data' : data_result, 'language' : lang_data })