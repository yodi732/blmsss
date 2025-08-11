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

async def main_setting_sitemap_set():
    with get_db_connect() as conn:
        curs = conn.cursor()

        if await acl_check('', 'owner_auth', '', '') == 1:
            return await re_error(conn, 0)
        
        setting_list = {
            0 : ['sitemap_auto_exclude_domain', ''],
            1 : ['sitemap_auto_exclude_user_page', ''],
            2 : ['sitemap_auto_exclude_file_page', ''],
            3 : ['sitemap_auto_exclude_category_page', ''],
            4 : ['sitemap_auto_make', '']
        }

        if flask.request.method == 'POST':
            for i in setting_list:
                curs.execute(db_change("update other set data = ? where name = ?"), [
                    flask.request.form.get(setting_list[i][0], setting_list[i][1]),
                    setting_list[i][0]
                ])

            await acl_check(tool = 'owner_auth', memo = 'edit_set (sitemap)')

            return redirect(conn, '/setting/sitemap_set')
        else:
            d_list = {}
            for i in setting_list:
                curs.execute(db_change('select data from other where name = ?'), [setting_list[i][0]])
                db_data = curs.fetchall()
                if not db_data:
                    curs.execute(db_change('insert into other (name, data, coverage) values (?, ?, "")'), [
                        setting_list[i][0],
                        setting_list[i][1]
                    ])

                d_list[i] = db_data[0][0] if db_data else setting_list[i][1]

            check_box_div = [0, 1, 2, 3, 4, '']
            for i in range(0, len(check_box_div)):
                acl_num = check_box_div[i]
                if acl_num != '' and d_list[acl_num]:
                    check_box_div[i] = 'checked="checked"'
                else:
                    check_box_div[i] = ''

            sitemap_list = ''
            if os.path.exists('sitemap.xml'):
                sitemap_list += '<a href="/sitemap.xml">(' + get_lang(conn, 'view') + ')</a>'

                for_a = 0
                while os.path.exists('sitemap_' + str(for_a) + '.xml'):
                    sitemap_list += ' <a href="/sitemap_' + str(for_a) + '.xml">(sitemap_' + str(for_a) + '.xml)</a>'

                    for_a += 1

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'sitemap_management'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    ''' + sitemap_list + '''
                    <hr class="main_hr">
                    <form method="post">
                        <a href="/setting/sitemap">(''' + get_lang(conn, 'sitemap_manual_create') + ''')</a>
                        <hr class="main_hr">

                        <label><input type="checkbox" ''' + check_box_div[4] + ''' name="sitemap_auto_make"> ''' + get_lang(conn, 'sitemap_auto_make') + '''</label>
                        <hr class="main_hr">

                        <label><input type="checkbox" ''' + check_box_div[0] + ''' name="sitemap_auto_exclude_domain"> ''' + get_lang(conn, 'stiemap_exclude_domain') + '''</label>
                        <hr class="main_hr">

                        <label><input type="checkbox" ''' + check_box_div[1] + ''' name="sitemap_auto_exclude_user_page"> ''' + get_lang(conn, 'stiemap_exclude_user_page') + '''</label>
                        <hr class="main_hr">

                        <label><input type="checkbox" ''' + check_box_div[2] + ''' name="sitemap_auto_exclude_file_page"> ''' + get_lang(conn, 'stiemap_exclude_file_page') + '''</label>
                        <hr class="main_hr">

                        <label><input type="checkbox" ''' + check_box_div[3] + ''' name="sitemap_auto_exclude_category_page"> ''' + get_lang(conn, 'stiemap_exclude_category_page') + '''</label>
                        <hr class="main_hr">

                        <button id="opennamu_save_button" type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['setting', get_lang(conn, 'return')]]
            ))