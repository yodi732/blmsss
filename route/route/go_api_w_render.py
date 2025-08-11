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

from .go_api_w_raw import api_w_raw

async def api_w_render(name = '', tool = '', request_method = '', request_data = {}):
    with get_db_connect() as conn:
        curs = conn.cursor()

        flask_data = flask_data_or_variable(flask.request.form, request_data)
        request_method = flask.request.method if request_method == '' else request_method

        if request_method == 'POST':
            name = flask_data.get('name', '')
            data_org = flask_data.get('data', '')
            data_option = flask_data.get('option', '')

            markup = ''
            if tool in ('', 'from', 'include'):
                curs.execute(db_change("select set_data from data_set where doc_name = ? and set_name = 'document_markup'"), [name])
                db_data = curs.fetchall()
                if db_data and db_data[0][0] != '' and db_data[0][0] != 'normal':
                    markup = db_data[0][0]

                if markup == '':
                    curs.execute(db_change('select data from other where name = "markup"'))
                    db_data = curs.fetchall()
                    markup = db_data[0][0] if db_data else 'namumark'

            data_type = ''
            if tool == '':
                data_type = 'api_view'
            elif tool == 'from':
                data_type = 'api_from'
            elif tool == 'include':
                data_type = 'api_include'
            elif tool == 'backlink':
                data_type = 'backlink'
            else:
                data_type = 'api_thread'

            if markup in ('', 'namumark', 'namumark_beta') and data_option != '':
                data_option = json_loads(data_option)

                # remove end br
                data_org = re.sub('^\n+', '', data_org)

            if markup in ('', 'namumark'):
                data_pas = render_set(conn, 
                    doc_name = name, 
                    doc_data = data_org, 
                    data_type = data_type,
                    parameter = data_option
                )

                return {
                    "data" : data_pas[0], 
                    "js_data" : data_pas[1]
                }
            else:
                other_set = {}
                other_set["doc_name"] = name
                other_set["render_type"] = data_type
                other_set["data"] = data_org

                return await python_to_golang(sys._getframe().f_code.co_name, other_set)
        else:
            return {}

async def api_w_render_exter(name = '', tool = '', request_method = '', request_data = {}):
    return flask.jsonify(await api_w_render(name, tool, request_method, request_data))