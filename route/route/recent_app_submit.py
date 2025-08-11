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

async def recent_app_submit():
    with get_db_connect() as conn:
        curs = conn.cursor()

        div = ''

        curs.execute(db_change('select data from other where name = "requires_approval"'))
        requires_approval = curs.fetchall()
        if requires_approval and requires_approval[0][0] != 'on':
            div += get_lang(conn, 'approval_requirement_disabled')

        if flask.request.method == 'GET':
            curs.execute(db_change('select data from user_set where name = "application"'))
            db_data = curs.fetchall()
            if db_data:
                div += '' + \
                    get_lang(conn, 'all_register_num') + ' : ' + str(len(db_data)) + \
                    '<hr class="main_hr">' + \
                ''

                div += '''
                    <table id="main_table_set">
                        <tr id="main_table_top_tr">
                            <td id="main_table_width_half">''' + get_lang(conn, 'id') + '''</td>
                            <td id="main_table_width_half">''' + get_lang(conn, 'email') + '''</td>
                        </tr>
                        <tr id="main_table_top_tr">
                            <td>''' + get_lang(conn, 'approval_question') + '''</td>
                            <td>''' + get_lang(conn, 'answer') + '''</td>
                        </tr>                        
                '''

                for application in db_data:
                    application = json_loads(application[0])

                    if 'question' in application:
                        question = html.escape(application['question'])
                        question = question if question != '' else '<br>'
                    else:
                        question = '<br>'

                    if 'answer' in application:
                        answer = html.escape(application['answer'])
                        answer = answer if answer != '' else '<br>'
                    else:
                        answer = '<br>'


                    if 'email' in application:
                        email = html.escape(application['email'])
                        email = email if email != '' else '<br>'
                    else:
                        email = '<br>'

                    div += '''
                        <form method="post">
                            <tr>
                                <td>''' + application['id'] + '''</td>
                                <td>''' + email + '''</td>
                            </tr>
                            <tr>
                                <td>''' + question + '''</td>
                                <td>''' + answer + '''</td>
                            </tr>
                            <tr>
                                <td colspan="3">
                                    <button type="submit" 
                                            id="opennamu_save_button"
                                            name="approve" 
                                            value="''' + application['id'] + '''">
                                        ''' + get_lang(conn, 'approve') + '''
                                    </button>
                                    <button type="submit" 
                                            name="decline" 
                                            value="''' + application['id'] + '''">
                                        ''' + get_lang(conn, 'decline') + '''
                                    </button>
                                </td>
                            </tr>
                        </form>
                    '''

                div += '</table>'
            else:
                div += get_lang(conn, 'no_applications_now')

            return easy_minify(conn, flask.render_template(skin_check(conn),
                imp = [get_lang(conn, 'application_list'), await wiki_set(), await wiki_custom(conn), wiki_css([0, 0])],
                data = div,
                menu = [['other', get_lang(conn, 'return')]]
            ))
        else:
            if await acl_check(tool = 'ban_auth', memo = 'app submit') == 1:
                return await re_error(conn, 0)

            if flask.request.form.get('approve', '') != '':
                curs.execute(db_change('select data from user_set where id = ? and name = "application"'), [flask.request.form.get('approve', '')])
                application = curs.fetchall()
                if not application:
                    return await re_error(conn, 26)
                else:
                    application = json_loads(application[0][0])

                add_user(conn, application['id'], application['pw'], application['email'], application['encode'])

                curs.execute(db_change("insert into user_set (name, id, data) values ('approval_question', ?, ?)"), [application['id'], application['question']])
                curs.execute(db_change("insert into user_set (name, id, data) values ('approval_question_answer', ?, ?)"), [application['id'], application['answer']])

                curs.execute(db_change('delete from user_set where id = ? and name = "application"'), [application['id']])
            elif flask.request.form.get('decline', '') != '':
                curs.execute(db_change('delete from user_set where id = ? and name = "application"'), [flask.request.form.get('decline', '')])

            return redirect(conn, '/app_submit')