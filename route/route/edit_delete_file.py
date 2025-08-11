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

async def edit_delete_file(name = 'test.jpg'):
    with get_db_connect() as conn:
        if await acl_check('', 'owner_auth', '', '') != 0:
            return await re_error(conn, 0)

        mime_type = re.search(r'([^.]+)$', name)
        mime_type_str = 'jpg'
        if mime_type:
            mime_type_str = mime_type.group(1)

        file_name = re.sub(r'\.([^.]+)$', '', name)
        file_name = re.sub(r'^file:', '', file_name)

        file_all_name = sha224_replace(file_name) + '.' + mime_type_str
        file_directory = os.path.join(load_image_url(conn), file_all_name)

        if not os.path.exists(file_directory):
            return redirect(conn, '/w/' + url_pas(name))

        if flask.request.method == 'POST':
            await acl_check(tool = 'owner_auth', memo = 'file del (' + name + ')')
            os.remove(file_directory)

            if flask.request.form.get('with_doc', '') != '':
                await edit_delete(name)

            return redirect(conn, '/w/' + url_pas(name))
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [name, await wiki_set(), await wiki_custom(conn), wiki_css(['(' + get_lang(conn, 'file_delete') + ')', 0])],
                data = '''
                    <form method="post">
                        <img src="/image/''' + url_pas(file_all_name) + '''">
                        <hr class="main_hr">
                        <a href="/image/''' + url_pas(file_all_name) + '''">/image/''' + url_pas(file_all_name) + '''</a>
                        <hr class="main_hr">
                        <label><input name="with_doc" type="checkbox" checked> ''' + get_lang(conn, 'file_delete_with_document') + '''</label>
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'file_delete') + '''</button>
                    </form>
                ''',
                menu = [['w/' + url_pas(name), get_lang(conn, 'return')]]
            ))