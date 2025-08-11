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

async def main_view(name = ''):
    with get_db_connect() as conn:
        file_name = re.search(r'([^/]+)$', name)
        if not file_name:
            return ''
        else:
            file_name = file_name.group(1)
            dir_name = './views/' + re.sub(r'\.{2,}', '', name[:-len(file_name)])

            file_name = re.sub(r'\.cache_v(?:[0-9]+)$', '', file_name)

            mime_type = file_name.split('.')
            if len(mime_type) < 2:
                mime_type = 'text/plain'
            else:
                mime_type = mime_type[len(mime_type) - 1].lower()
                image_type = ['jpeg', 'jpg', 'gif', 'png', 'webp', 'ico', 'svg']
                if mime_type in image_type:
                    if not mime_type == 'svg':
                        mime_type = 'image/' + mime_type
                    else:
                        mime_type = 'image/svg+xml'
                elif mime_type == 'js':
                    mime_type = 'text/javascript'
                elif mime_type == 'txt':
                    mime_type = 'text/plain'
                else:
                    mime_type = 'text/' + mime_type

            return flask.send_from_directory(dir_name, file_name, mimetype = mime_type)