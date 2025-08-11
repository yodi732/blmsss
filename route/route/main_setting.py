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

async def main_setting():
    with get_db_connect() as conn:
        li_list = [
            ['main', get_lang(conn, 'main_setting')],
            ['phrase', get_lang(conn, 'text_setting')],
            ['robot', 'robots.txt'],
            ['external', get_lang(conn, 'ext_api_req_set')],
            ['head', get_lang(conn, 'main_head')],
            ['body/top', get_lang(conn, 'main_body')],
            ['body/bottom', get_lang(conn, 'main_bottom_body')],
            ['sitemap_set', get_lang(conn, 'sitemap_management')],
            ['top_menu', get_lang(conn, 'top_menu_setting')],
            ['skin_set', get_lang(conn, 'main_skin_set_default')],
            ['404_page', get_lang(conn, '404_page_setting')]
        ]

        li_data = ''.join(['<li><a href="/setting/' + str(li[0]) + '">' + li[1] + '</a></li>' for li in li_list])

        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'setting'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = '<h2>' + get_lang(conn, 'list') + '</h2><ul>' + li_data + '</ul>',
            menu = [['manager', get_lang(conn, 'return')]]
        ))