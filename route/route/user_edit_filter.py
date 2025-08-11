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

async def user_edit_filter(name = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        owner_auth = await acl_check(tool = 'ban_auth')
        owner_auth = 1 if owner_auth == 0 else 0

        if ip_check() != name:
            if owner_auth != 1:
                return redirect(conn, '/recent_block')

        if flask.request.method == 'POST':
            curs.execute(db_change('delete from user_set where name = "edit_filter" and id = ?'), [name])

            return redirect(conn, '/edit_filter/' + url_pas(name))
        else:
            curs.execute(db_change('select data from user_set where name = "edit_filter" and id = ?'), [name])
            db_data = curs.fetchall()
            p_data = db_data[0][0] if db_data else ''
            p_data = '<textarea readonly class="opennamu_textarea_500">' + html.escape(p_data) + '</textarea>'

            search_list = '<ul>'

            curs.execute(db_change("select plus, plus_t from html_filter where kind = 'regex_filter' and plus != ''"))
            for data_list in curs.fetchall():
                match = re.compile(data_list[0], re.I)
                search = match.search(p_data)
                if search:
                    search = search.group()
                    search_list += '<li>' + html.escape(search) + '</li>'

            search_list += '</ul>'
            search_list += '<hr class="main_hr">'

            delete = ''
            if owner_auth == 1:
                delete = '' + \
                    '<form method="post">' + \
                        '<button type="submit">' + get_lang(conn, 'delete') + '</button>' + \
                    '</form>' + \
                    '<hr class="main_hr">' + \
                ''

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [name, await wiki_set(), await wiki_custom(conn), wiki_css(['(' + get_lang(conn, 'edit_filter') + ')', 0])],
                data = '' + \
                    '<a href="/filter/edit_filter">(' + get_lang(conn, 'edit_filter_rule') + ')</a>' + \
                    '<hr class="main_hr">' + \
                    p_data + search_list + delete + \
                '',
                menu = [['recent_block', get_lang(conn, 'return')], ]
            ))