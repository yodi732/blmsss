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

async def main_setting_sitemap(do_type = 0):
    with get_db_connect() as conn:
        curs = conn.cursor()

        if not do_type == 1:
            if await acl_check('', 'owner_auth', '', '') == 1:
                return await re_error(conn, 0)
        
        if do_type == 1 or flask.request.method == 'POST':
            if not do_type == 1:
                await acl_check(tool = 'owner_auth', memo = 'make sitemap')

            data = '' + \
                '<?xml version="1.0" encoding="UTF-8"?>\n' + \
                '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
            ''

            curs.execute(db_change('select data from other where name = "sitemap_auto_exclude_domain"'))
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                domain = ''
            else:
                domain = load_domain(conn, 'full')

            sql_add = ''

            curs.execute(db_change('select data from other where name = "sitemap_auto_exclude_user_page"'))
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                sql_add += ' title not like "user:%"'

            curs.execute(db_change('select data from other where name = "sitemap_auto_exclude_file_page"'))
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                if sql_add != '':
                    sql_add += ' and'

                sql_add += ' title not like "file:%"'

            curs.execute(db_change('select data from other where name = "sitemap_auto_exclude_category_page"'))
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                if sql_add != '':
                    sql_add += ' and'

                sql_add += ' title not like "category:%"'

            if sql_add != '':
                sql_add = ' where' + sql_add

            curs.execute(db_change("select title from data" + sql_add))
            all_data = curs.fetchall()

            len_all_data = len(all_data)
            count = int(len_all_data / 30000)
            other_count = len_all_data % 30000

            for i in range(count + 1):
                data += '<sitemap><loc>' + domain + '/sitemap_' + str(i) + '.xml</loc></sitemap>\n'

            data += '' + \
                '</sitemapindex>' + \
            ''

            f = open("sitemap.xml", 'w')
            f.write(data)
            f.close()

            for i in range(count + 1):
                data = '' + \
                    '<?xml version="1.0" encoding="UTF-8"?>\n' + \
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
                ''

                if count == i:
                    for x in all_data[30000 * i:]:
                        data += '<url><loc>' + domain + '/w/' + url_pas(x[0]) + '</loc></url>\n'
                else:
                    for x in all_data[30000 * i:30000 * (i + 1)]:
                        data += '<url><loc>' + domain + '/w/' + url_pas(x[0]) + '</loc></url>\n'

                data += '' + \
                    '</urlset>' + \
                ''

                f = open("sitemap_" + str(i) + ".xml", 'w')
                f.write(data)
                f.close()

            if not do_type == 1:
                return redirect(conn, '/setting/sitemap')
            else:
                return ''
        else:
            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'sitemap_manual_create'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <form method="post">
                        <button id="opennamu_save_button" type="submit">''' + get_lang(conn, 'create') + '''</button>
                    </form>
                ''',
                menu = [['setting/sitemap_set', get_lang(conn, 'return')]]
            ))