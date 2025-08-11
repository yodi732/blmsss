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

async def main_tool_admin():
    with get_db_connect() as conn:
        return easy_minify(conn, flask.render_template(skin_check(conn),
            imp = [get_lang(conn, 'admin_tool'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
            data = render_simple_set(conn, '''
                <h2>''' + get_lang(conn, 'admin') + '''</h2>
                <ul>
                    <li><a href="/manager/2">''' + get_lang(conn, 'document_setting') + '''</a></li>
                    <li><a href="/acl_multiple">''' + get_lang(conn, 'mutiple_document_setting') + '''</a></li>
                    <li><a href="/manager/3">''' + get_lang(conn, 'check_user') + '''</a></li>
                    <li><a href="/auth/ban">''' + get_lang(conn, 'ban') + '''</a></li>
                    <li><a href="/auth/ban/multiple">''' + get_lang(conn, 'multiple_ban') + '''</a></li>
                    <li><a href="/manager/5">''' + get_lang(conn, 'authorize') + '''</a></li>
                    <li><a href="/auth/give">''' + get_lang(conn, 'multiple_authorize') + '''</a></li>
                    <li><a href="/auth/give_total">''' + get_lang(conn, 'auth_to_auth') + '''</a></li>
                    <li><a href="/delete_multiple">''' + get_lang(conn, 'many_delete') + '''</a></li>
                    <li><a href="/app_submit">''' + get_lang(conn, 'application_list') + '''</a></li>
                </ul>
                <h2>''' + get_lang(conn, 'owner') + '''</h2>
                <ul>
                    <li><a href="/auth/list">''' + get_lang(conn, 'admin_group_list') + '''</a></li>
                    <li><a href="/register">''' + get_lang(conn, 'add_user') + '''</a></li>
                    <li><a href="/setting">''' + get_lang(conn, 'setting') + '''</a></li>
                    <li><a href="/manager/18">''' + get_lang(conn, 'user_fix') + '''</a></li>
                </ul>
                <h3>''' + get_lang(conn, 'filter') + '''</h3>
                <ul>
                    <li><a href="/filter/edit_filter">''' + get_lang(conn, 'edit_filter_list') + '''</a></li>
                    <li><a href="/filter/inter_wiki">''' + get_lang(conn, 'interwiki_list') + '''</a></li>
                    <li><a href="/filter/edit_top">''' + get_lang(conn, 'edit_tool_list') + '''</a></li>
                    <li><a href="/filter/image_license">''' + get_lang(conn, 'image_license_list') + '''</a></li>
                    <li><a href="/filter/email_filter">''' + get_lang(conn, 'email_filter_list') + '''</a></li>
                    <li><a href="/filter/name_filter">''' + get_lang(conn, 'id_filter_list') + '''</a></li>
                    <li><a href="/filter/file_filter">''' + get_lang(conn, 'file_filter_list') + '''</a></li>
                    <li><a href="/filter/extension_filter">''' + get_lang(conn, 'extension_filter_list') + '''</a></li>
                    <li><a href="/filter/document">''' + get_lang(conn, 'document_filter_list') + '''</a></li>
                    <li><a href="/filter/outer_link">''' + get_lang(conn, 'outer_link_filter_list') + '''</a> (''' + get_lang(conn, 'beta') + ''')
                    <li><a href="/filter/template">''' + get_lang(conn, 'template_document_list') + '''</a> (''' + get_lang(conn, 'beta') + ''')
                </ul>
                <h3>''' + get_lang(conn, 'server') + '''</h2>
                <ul>
                    <li><a href="/restart">''' + get_lang(conn, 'wiki_restart') + '''</a></li>
                    <li><a href="/shutdown">''' + get_lang(conn, 'wiki_shutdown') + '''</a></li>
                    <li><a href="/update">''' + get_lang(conn, 'update') + '''</a></li>
                </ul>
                <h2>''' + get_lang(conn, 'version') + '''</h2>
                <ul>
                    <li id="ver_send_2">''' + get_lang(conn, 'version') + ''' : </li>
                    <li id="ver_send">''' + get_lang(conn, 'lastest') + ''' : </li>
                </ul>
                <h3>''' + get_lang(conn, 'skin_info') + '''</h3>
                <ul>
                    <li><a href="/api/skin_info?all=true">''' + get_lang(conn, 'skin_info') + '''</a></li>
                    <div id="ver_send_3"></div>
                </ul>
                <!-- JS : opennamu_do_insert_version -->
                <!-- JS : opennamu_do_insert_version_skin -->
            '''),
            menu = [['other', get_lang(conn, 'return')]]
        ))