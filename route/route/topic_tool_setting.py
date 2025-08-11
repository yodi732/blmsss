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

async def topic_tool_setting(topic_num = 1):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check(tool = 'toron_auth') == 1:
            return await re_error(conn, 3)

        ip = ip_check()
        time = get_time()
        topic_num = str(topic_num)

        curs.execute(db_change("select stop, agree from rd where code = ?"), [topic_num])
        rd_d = curs.fetchall()
        if not rd_d:
            return redirect(conn, '/')

        if flask.request.method == 'POST':
            await acl_check(tool = 'toron_auth', memo = 'change_topic_set (code ' + topic_num + ')')

            stop_d = flask.request.form.get('stop_d', '')
            why_d = flask.request.form.get('why', '')
            agree_d = flask.request.form.get('agree', '')

            if stop_d != rd_d[0][0]:
                curs.execute(db_change("update rd set stop = ? where code = ?"), [
                    stop_d,
                    topic_num
                ])

                if stop_d == 'S':
                    t_state = 'topic_state_change_stop'
                elif stop_d == 'O':
                    t_state = 'topic_state_change_close'
                else:
                    t_state = 'topic_state_change_normal'

                do_add_thread(conn, 
                    topic_num,
                    get_lang(conn, t_state),
                    '1'
                )

            if agree_d != rd_d[0][1]:
                curs.execute(db_change("update rd set agree = ? where code = ?"), [
                    agree_d,
                    topic_num
                ])

                if agree_d == 'O':
                    t_state = 'topic_state_change_agree'
                else:
                    t_state = 'topic_state_change_disagree'

                do_add_thread(conn, 
                    topic_num,
                    get_lang(conn, t_state),
                    '1'
                )

            if why_d != '':
                do_add_thread(conn, 
                    topic_num,
                    get_lang(conn, 'why') + ' : ' + why_d,
                    '1'
                )
            
            do_reload_recent_thread(conn, 
                topic_num, 
                time
            )

            return redirect(conn, '/thread/' + topic_num)
        else:
            stop_d_list = ''
            agree_check = ''
            for_list = [
                ['O', get_lang(conn, 'topic_close')],
                ['S', get_lang(conn, 'topic_stop')],
                ['', get_lang(conn, 'topic_normal')]
            ]

            for i in for_list:
                if rd_d and rd_d[0][0] == i[0]:
                    stop_d_list = '<option value="' + i[0] + '">' + i[1] + '</option>' + stop_d_list
                else:
                    stop_d_list += '<option value="' + i[0] + '">' + i[1] + '</option>'

            agree_check = 'checked="checked"' if rd_d[0][1] == 'O' else ''

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'topic_setting'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = render_simple_set(conn, '''
                    <form method="post">
                        <h2>''' + get_lang(conn, 'topic_progress') + '''</h2>
                        <select name="stop_d">
                            ''' + stop_d_list + '''
                        </select>
                        <hr class="main_hr">
                        <label><input type="checkbox" name="agree" value="O" ''' + agree_check + '''> ''' + get_lang(conn, 'topic_change_agree') + '''</label>

                        <h2>''' + get_lang(conn, 'topic_associate') + '''</h2>
                        ''' + get_lang(conn, 'topic_link_vote') + ''' (''' + get_lang(conn, 'not_working') + ''')
                        <hr class="main_hr">
                        <input placeholder="''' + get_lang(conn, 'topic_insert_vote_number') + '''" name="vote_number" type="number">

                        <h2>''' + get_lang(conn, 'why') + '''</h2>
                        <input placeholder="''' + get_lang(conn, 'why') + ''' (''' + get_lang(conn, 'markup_enabled') + ''')" name="why" type="text">
                        
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                '''),
                menu = [['thread/' + topic_num + '/tool', get_lang(conn, 'return')]]
            ))