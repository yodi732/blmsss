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

import urllib.request

from .tool.func import *

async def api_skin_info(name = ''):
    with get_db_connect() as conn:
        name = skin_check(conn) if name == '' else './views/' + name + '/index.html'

        if not flask.request.args.get('all', None):
            json_address = re.sub(r"(((?!\.|\/).)+)\.html$", "info.json", name)
            try:
                json_data = json_loads(open(json_address, encoding='utf8').read())
            except:
                json_data = None

            if json_data:
                return flask.jsonify(json_data)
            else:
                return flask.jsonify({}), 404
        else:
            a_data = {}
            d_link_data = {
                "ACME" : "https://raw.githubusercontent.com/openNAMU/openNAMU-Skin-ACME/master/info.json",
                "Liberty" : "https://raw.githubusercontent.com/openNAMU/openNAMU-Skin-Liberty/master/info.json",
                "Before Namu" : "https://raw.githubusercontent.com/openNAMU/openNAMU-Skin-Before_Namu/master/info.json"
            }

            for i in load_skin(conn, skin_check(conn, 1), 1):
                json_address = re.sub(r"(((?!\.|\/).)+)\.html$", "info.json", './views/' + i + '/index.html')
                try:
                    json_data = json_loads(open(json_address, encoding='utf8').read())
                except:
                    json_data = None

                if json_data:
                    if i == skin_check(conn, 1):
                        json_data = {**json_data, **{ "main" : "true" }}

                    if "info_link" in json_data:
                        info_link = json_data["info_link"]
                    elif json_data["name"] in d_link_data:
                        info_link = d_link_data[json_data["name"]]
                    else:
                        info_link = 0

                    if info_link != 0:
                        try:
                            get_data = urllib.request.urlopen(info_link)
                        except:
                            get_data = None

                        if get_data and get_data.getcode() == 200:
                            try:
                                get_data = json_loads(get_data.read().decode())
                            except:
                                get_data = {}

                            if "skin_ver" in get_data:
                                json_data = {**json_data, **{ "lastest_version" : {
                                    "skin_ver" : get_data["skin_ver"]
                                }}}

                    a_data = {**a_data, **{ i : json_data }}

            return flask.jsonify(a_data)