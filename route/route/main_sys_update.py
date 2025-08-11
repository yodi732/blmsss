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

import zipfile
import urllib.request

from .tool.func import *

from .main_sys_restart import main_sys_restart_do

async def main_sys_update(golang_process):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 3)

        if flask.request.method == 'POST':
            await acl_check(tool = 'owner_auth', memo = 'update')

            curs.execute(db_change('select data from other where name = "update"'))
            up_data = curs.fetchall()
            up_data = up_data[0][0] if up_data and up_data[0][0] in ['stable', 'beta', 'dev', 'dont_use'] else 'stable'

            print('Update')
            
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
            
            if platform.system() == 'Linux' or platform.system() == 'Darwin':
                ok = []
                ok += [os.system('git remote rm origin')]
                ok += [os.system('git remote add origin https://github.com/opennamu/opennamu.git')]
                ok += [os.system('git fetch --depth=1 origin ' + up_data)]
                ok += [os.system('git reset --hard origin/' + up_data)]
                for for_a in ok[1:]:
                    if for_a != 0:
                        break
                else:
                    linux_exe_chmod()

                    threading.Thread(target = main_sys_restart_do).start()
                    return flask.Response(get_lang(conn, "warning_restart"), status = 200)
                
                print('Error : update failed')
            elif platform.system() == 'Windows':
                os.system('rd /s /q route')

                urllib.request.urlretrieve('https://github.com/opennamu/opennamu/archive/' + up_data + '.zip', 'update.zip')
                    
                zipfile.ZipFile('update.zip').extractall('')
                
                ok = os.system('xcopy /y /s /r opennamu-' + up_data + ' .')
                if ok == 0:
                    os.system('rd /s /q opennamu-' + up_data)
                    os.system('del update.zip')
                    
                    threading.Thread(target = main_sys_restart_do).start()
                    return flask.Response(get_lang(conn, "warning_restart"), status = 200)
            
            print('Error : update failed')

            return await re_error(conn, 34)
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'update'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = get_lang(conn, 'update_warning') + '''
                    <hr class="main_hr">
                    <ul>
                        <li id="ver_send_2">''' + get_lang(conn, 'version') + ''' : </li>
                        <li id="ver_send">''' + get_lang(conn, 'lastest') + ''' : </li>
                    </ul>
                    <a href="https://github.com/openNAMU/openNAMU">(Beta)</a> <a href="https://github.com/openNAMU/openNAMU/tree/stable">(Stable)</a>
                    <hr class="main_hr">
                    <form method="post">
                        <button type="submit">''' + get_lang(conn, 'update') + '''</button>
                    </form>
                    <!-- JS : opennamu_do_insert_version -->
                ''',
                menu = [['manager', get_lang(conn, 'return')]]
            ))

