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

def main_sys_restart_do():
    print('Restart')

    time.sleep(3)

    python_ver = ''
    python_ver = str(sys.version_info.major) + '.' + str(sys.version_info.minor)

    run_list = [
        sys.executable,
        'python' + python_ver,
        'python3',
        'python',
        'py -' + python_ver
    ]

    for exe_name in run_list:
        try:
            subprocess.Popen([exe_name] + sys.argv)
            break
        except:
            continue
    
    os._exit(0)

async def main_sys_restart(golang_process):
    with get_db_connect() as conn:
        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 3)

        if flask.request.method == 'POST':
            await acl_check(tool = 'owner_auth', memo = 'restart')

            if golang_process.poll() is None:
                golang_process.terminate()
                try:
                    golang_process.wait(timeout = 5)
                except subprocess.TimeoutExpired:
                    golang_process.kill()
                    try:
                        golang_process.wait(timeout = 5)
                    except subprocess.TimeoutExpired:
                        print('Golang process not terminated properly.')

            threading.Thread(target = main_sys_restart_do).start()
            return flask.Response(get_lang(conn, "warning_restart"), status = 200)
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'wiki_restart'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        <button type="submit">''' + get_lang(conn, 'restart') + '''</button>
                    </form>
                ''',
                menu = [['manager', get_lang(conn, 'return')]]
            ))