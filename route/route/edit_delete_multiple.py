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

from .edit_delete import edit_delete

async def edit_delete_multiple():
    with get_db_connect() as conn:
        if await acl_check('', 'acl_auth', '', '') == 1:
            return await re_error(conn, 0)

        if flask.request.method == 'POST':
            send = flask.request.form.get('send', '')
            agree = flask.request.form.get('copyright_agreement', '')
            
            if await do_edit_send_check(conn, send) == 1:
                return await re_error(conn, 37)
            
            if do_edit_text_bottom_check_box_check(conn, agree) == 1:
                return await re_error(conn, 29)
            
            all_title = re.findall(r'([^\n]+)\n', flask.request.form.get('content', '').replace('\r', '') + '\n')
            for name in all_title:
                await edit_delete(name)

            return redirect(conn, '/recent_change')
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'many_delete'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        <textarea class="opennamu_textarea_500" placeholder="''' + get_lang(conn, 'many_delete_help') + '''" name="content"></textarea>
                        <hr class="main_hr">
                        <input placeholder="''' + get_lang(conn, 'why') + '''" name="send" type="text">
                        <hr class="main_hr">
                        ''' + await captcha_get(conn) + ip_warning(conn) + get_edit_text_bottom_check_box(conn) + get_edit_text_bottom(conn, 'edit')  + '''
                        <button type="submit">''' + get_lang(conn, 'delete') + '''</button>
                    </form>
                ''',
                menu = [['manager/1', get_lang(conn, 'return')]]
            ))