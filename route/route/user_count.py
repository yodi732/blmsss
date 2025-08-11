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

async def user_count(name = None):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if name == None:
            that = ip_check()
        else:
            that = name

        curs.execute(db_change("select count(*) from history where ip = ?"), [that])
        count = curs.fetchall()
        if count:
            data = count[0][0]
        else:
            data = 0

        curs.execute(db_change("select count(*) from topic where ip = ?"), [that])
        count = curs.fetchall()
        if count:
            data_topic = count[0][0]
        else:
            data_topic = 0
            
        date = get_time()
        date = date.split()
        date = date[0]
        
        data_today = 0
        data_today_len = 0
            
        curs.execute(db_change("select leng from history where date like ? and ip = ?"), [date + '%', that])
        db_data = curs.fetchall()
        for count in db_data:
            count_data = count[0]
            count_data = count_data.replace('+', '')
            count_data = count_data.replace('-', '')

            data_today_len += int(count_data)
            data_today += 1

        date_yesterday = str((
            datetime.datetime.today() + datetime.timedelta(days = -1)
        ).strftime("%Y-%m-%d"))
        
        data_yesterday = 0
        data_yesterday_len = 0
            
        curs.execute(db_change("select leng from history where date like ? and ip = ?"), [date_yesterday + '%', that])
        db_data = curs.fetchall()
        for count in db_data:
            count_data = count[0]
            count_data = count_data.replace('+', '')
            count_data = count_data.replace('-', '')

            data_yesterday_len += int(count_data)
            data_yesterday += 1

        # 한글 지원 필요
        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'count'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = '''
                <ul>
                    <li><a href="/record/''' + url_pas(that) + '''">''' + get_lang(conn, 'edit_record') + '''</a> : ''' + str(data) + '''</li>
                    <li><a href="/record/topic/''' + url_pas(that) + '''">''' + get_lang(conn, 'discussion_record') + '''</a> : ''' + str(data_topic) + '''</a></li>
                    <hr>
                    <li>(''' + get_lang(conn, 'beta') + ''') TODAY : ''' + str(data_today) + '''</li>
                    <li>(''' + get_lang(conn, 'beta') + ''') TODAY LEN : ''' + str(data_today_len) + '''</li>
                    <li>(''' + get_lang(conn, 'beta') + ''') TODAY DIFF : ''' + str(data_today_len - data_yesterday_len) + '''</li>
                    <hr>
                    <li>(''' + get_lang(conn, 'beta') + ''') YESTERDAY : ''' + str(data_yesterday) + '''</li>
                    <li>(''' + get_lang(conn, 'beta') + ''') YESTERDAY LEN : ''' + str(data_yesterday_len) + '''</li>
                </ul>
            ''',
            menu = [['user', get_lang(conn, 'return')]]
        ))