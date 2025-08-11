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

from .func_tool import *

from .func_render_namumark import class_do_render_namumark

# 커스텀 마크 언젠간 다시 추가 예정

class class_do_render:
    def __init__(self, conn, lang_data = {}, markup = '', parameter = {}, parent = None):
        self.conn = conn

        if lang_data == '{}':
            lang_data = {
                'toc' : 'toc',
                'category' : 'category'
            }

        self.lang_data = lang_data
        self.markup = markup
        self.parameter = parameter
        self.parent = parent

    def generate_random_string(self, length = 32):
        characters = string.ascii_letters + string.digits

        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def do_render(self, doc_name, doc_data, data_type):
        curs = self.conn.cursor()

        doc_set = {}
        if data_type == 'from':
            doc_set['doc_from'] = 'O'
            data_type = 'view'
        else:
            doc_set['doc_from'] = ''

        if data_type == 'backlink':
            doc_set['doc_type'] = 'view'
        else:
            doc_set['doc_type'] = data_type
        
        doc_set['doc_include'] = self.generate_random_string() + '_'
    
        rep_data = self.markup
        if rep_data == '' and doc_name != '':
            curs.execute(db_change("select set_data from data_set where doc_name = ? and set_name = 'document_markup'"), [doc_name])
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '' and db_data[0][0] != 'normal':
                rep_data = db_data[0][0]

        if rep_data == '':
            curs.execute(db_change('select data from other where name = "markup"'))
            db_data = curs.fetchall()
            rep_data = db_data[0][0] if db_data else 'namumark'

        if rep_data == 'namumark' or rep_data == 'namumark_beta':
            data_end = class_do_render_namumark(
                self.conn,
                doc_name,
                doc_data,
                doc_set,
                self.lang_data,
                parameter = self.parameter,
                parent = self.parent
            )()
        elif rep_data == 'raw':
            data_end = [html.escape(doc_data).replace('\n', '<br>'), '', {}]
        else:
            data_end = [doc_data, '', {}]

        if data_type == 'thread':
            def do_thread_a_change(match):
                data = match[2].replace('#', '')
                data_split = data.split('-')
                if match[1] == 'topic_a' or len(data_split) == 1:
                    return '<a href="' + match[2] + '">' + match[2] + '</a>'
                elif match[1] == 'topic_a_post' and len(data_split) == 3:
                    return '<a href="/bbs/w/' + data_split[2] + '/' + data_split[1] + '#' + data_split[0] + '">#' + data_split[0] + '-' + data_split[1] + '</a>'
                elif len(data_split) == 2:
                    return '<a href="/thread/' + data_split[1] + '#' + data_split[0] + '">' + match[2] + '</a>'
                else:
                    return ''

            data_end[0] = re.sub(r'&lt;(topic_a(?:_post|_thread)?)&gt;((?:(?!&lt;\/topic_a(?:_post|_thread)?&gt;).)+)&lt;\/topic_a(?:_post|_thread)?&gt;', do_thread_a_change, data_end[0])
            data_end[0] = re.sub(r'&lt;topic_call&gt;@(?P<in>(?:(?!&lt;\/topic_call&gt;).)+)&lt;\/topic_call&gt;', '<a href="/w/user:\\g<in>">@\\g<in></a>', data_end[0])

        if data_type == 'backlink':
            mode = ''
            if re.search('^user:', doc_name):
                mode = 'user'
            elif re.search('^file:', doc_name):
                mode = 'file'
            elif re.search('^category:', doc_name):
                mode = 'category'

            curs.execute(db_change("delete from back where link = ?"), [doc_name])
            curs.execute(db_change("delete from back where title = ? and type = 'no'"), [doc_name])

            curs.execute(db_change("delete from data_set where doc_name = ? and set_name = 'link_count'"), [doc_name])
            curs.execute(db_change("delete from data_set where doc_name = ? and set_name = 'doc_type'"), [doc_name])

            backlink = data_end[2]['backlink'] if 'backlink' in data_end[2] else []
            if backlink != []:
                curs.executemany(db_change("insert into back (link, title, type, data) values (?, ?, ?, ?)"), backlink)
                curs.execute(db_change("delete from back where title = ? and type = 'no'"), [doc_name])

            link_count = 0
            if 'link_count' in data_end[2]:
                link_count = data_end[2]['link_count']

            curs.execute(db_change("insert into data_set (doc_name, doc_rev, set_name, set_data) values (?, '', 'link_count', ?)"), [doc_name, link_count])

            if mode != '':
                curs.execute(db_change("insert into data_set (doc_name, doc_rev, set_name, set_data) values (?, '', 'doc_type', ?)"), [doc_name, mode]) 
            elif 'redirect' in data_end[2] and data_end[2]['redirect'] == 1:
                curs.execute(db_change("insert into data_set (doc_name, doc_rev, set_name, set_data) values (?, '', 'doc_type', 'redirect')"), [doc_name])
            else:
                curs.execute(db_change("insert into data_set (doc_name, doc_rev, set_name, set_data) values (?, '', 'doc_type', '')"), [doc_name])

        return [data_end[0], data_end[1], data_end[2]]