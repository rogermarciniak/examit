import time

import flask_admin as admin
import flask_login as login
from flask import flash, redirect, render_template, request, url_for
from flask_admin import expose, helpers
from pymongo import MongoClient

import stub as stub
from loginform import LoginForm

# prepares db
client = MongoClient()
db = client.examit
cats = db.cats
quests = db.quests  # question col
tests = db.tests


# Create customized index view class that handles login & registration
class AdminIndexView(admin.AdminIndexView):

    def get_quests(self):
        columns = ["Question", "Category", "Key", "Creation Date", "Unique ID"]
        found = quests.find()
        rows = []
        for q in found:
            row = []
            row.append(q['QUESTION'])
            row.append(q['CATEGORY'])
            row.append(q['KEY'])
            row.append(q['CREATED'])
            row.append(q['_id'])
            rows.append(row)
        return (columns, rows)

    def get_cats(self):
        columns = ["Category", "Creation Date", "Unique ID"]
        found = cats.find()
        rows = []
        for c in found:
            row = []
            row.append(c['CATEGORY'])
            row.append(c['CREATED'])
            row.append(c['_id'])
            rows.append(row)
        return (columns, rows)

    def _stubs(self):
        self.nav = {
            "tasks": stub.get_tasks(),
            "messages": stub.get_messages_summary(),
            "alerts": stub.get_alerts()
        }

        (cols, rows) = stub.get_adv_tables()
        (scols, srows, context) = stub.get_tables()

        self.tables = {
            "advtables": {"columns": cols, "rows": rows},
            "table": {"columns": scols, "rows": srows, "context": context}
        }

        self.panelswells = {
            "accordion": stub.get_accordion_items(),
            "tabitems": stub.get_tab_items()
        }

    def _tools(self):
        (qcols, qrows) = self.get_quests()
        self.qtable = {"questions": {"columns": qcols,
                                     "rows": qrows}}

        (ccols, crows) = self.get_cats()
        self.ctable = {"categories": {"columns": ccols,
                                      "rows": crows}}

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Welcome to ExamIT"
        return render_template('sb-admin/pages/start.html', admin_view=self)

    @expose('/categories', methods=['GET', 'POST'])
    def cats(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        if request.method == 'POST':
            cat = request.form.get('category')
            current_time = time.localtime()
            ctime = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                  current_time)

            cat_to_db = {"CATEGORY": cat,
                         "CREATED": ctime}

            db_checker = {"CATEGORY": cat}

            result = cats.replace_one(db_checker, cat_to_db, upsert=True)
            if result.modified_count == 1:
                flash('Category/already existed!',
                      category='info')
            else:
                flash('Category was successfully added!',
                      category='success')
            return redirect(url_for('.cats'))

        self._tools()
        self.header = "Categories"
        return render_template('sb-admin/pages/cats.html',
                               admin_view=self)

    @expose('/questions/display')
    def questions(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._tools()
        self.header = "Questions"
        return render_template('sb-admin/pages/questions.html',
                               admin_view=self)

    @expose('/questions/add', methods=['GET', 'POST'])
    def add_question(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        catlist = []
        found = cats.find()
        for c in found:
            catlist.append(c['CATEGORY'])
        catlist.sort()

        if request.method == 'POST':
            cat = request.form.get('category')
            qbody = " ".join(request.form.get('question').split())
            answers = []
            answers.extend([" ".join(request.form.get('A').split()),
                            " ".join(request.form.get('B').split()),
                            " ".join(request.form.get('C').split()),
                            " ".join(request.form.get('D').split()),
                            " ".join(request.form.get('E').split())])
            anskey = request.form.get('anskey')
            current_time = time.localtime()
            ctime = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                  current_time)

            quest_to_db = {"CATEGORY": cat,
                           "QUESTION": qbody,
                           "ANSWERS": answers,
                           "KEY": anskey,
                           "CREATED": ctime}

            db_checker = {"CATEGORY": cat,
                          "QUESTION": qbody}

            # if a question with the same category/question combo exists,
            # then it is replaced with the new one,
            # otherwise treated as a new question and added to the db
            result = quests.replace_one(db_checker, quest_to_db, upsert=True)
            if result.modified_count == 1:
                flash('Category/Answer combination existed and was updated!',
                      category='info')
            else:
                flash('Question was successfully added!',
                      category='success')
            return render_template('sb-admin/pages/qadd.html',
                                   categs=catlist,
                                   admin_view=self)

        self._tools()
        self.header = "Add Question"
        return render_template('sb-admin/pages/qadd.html',
                               categs=catlist,
                               admin_view=self)

    @expose('/tests/display')
    def tests(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Tests"
        return render_template('sb-admin/pages/tests.html', admin_view=self)

    @expose('/tests/generate')
    def gentest(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        catlist = []
        found = cats.find()
        for c in found:
            catlist.append(c['CATEGORY'])
        catlist.sort()

        if request.method == 'POST':
            title = request.form.get('title')
            timeal = request.form.get('timeallowed')
            lecturer = request.form.get('lecturer')
            module = request.form.get('module')
            category = request.form.get('category')
            qamount = 5  # request.form.get('amount')
            current_time = time.localtime()
            ctime = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                  current_time)

            test_to_db = {"TITLE": title,
                          "TIME_ALLOWED": timeal,
                          "LECTURER": lecturer,
                          "MODULE": module,
                          "CATEGORY": category,
                          "QUESTCNT": qamount,
                          "CREATED": ctime}

            db_checker = {"TITLE": title,
                          "MODULE": module,
                          "CATEGORY": category,
                          "QUESTCNT": qamount}

            result = tests.replace_one(db_checker, test_to_db, upsert=True)
            if result.modified_count == 1:
                flash('Test existed and was updated!',
                      category='info')
            else:
                flash('Question was successfully added!',
                      category='success')
            return render_template('sb-admin/pages/tgen.html',
                                   categs=catlist,
                                   admin_view=self)

        self._stubs()
        self.header = "Generate Test"
        return render_template('sb-admin/pages/tgen.html',
                               categs=catlist,
                               admin_view=self)

    @expose('/blank')
    def blank(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Blank"
        return render_template('sb-admin/pages/blank.html', admin_view=self)

    @expose('/flot')
    def flot(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Flot Charts"
        return render_template('sb-admin/pages/flot.html', admin_view=self)

    @expose('/morris')
    def morris(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Morris Charts"
        return render_template('sb-admin/pages/morris.html', admin_view=self)

    @expose('/tables')
    def tables(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Tables"
        return render_template('sb-admin/pages/tables.html', admin_view=self)

    @expose('/forms')
    def forms(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Forms"
        return render_template('sb-admin/pages/forms.html', admin_view=self)

    @expose('/ui/panelswells')
    def panelswells(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Panels Wells"
        return render_template('sb-admin/pages/ui/panels-wells.html',
                               admin_view=self)

    @expose('/ui/buttons')
    def buttons(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Buttons"
        return render_template('sb-admin/pages/ui/buttons.html',
                               admin_view=self)

    @expose('/ui/notifications')
    def notifications(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Notifications"
        return render_template('sb-admin/pages/ui/notifications.html',
                               admin_view=self)

    @expose('/ui/typography')
    def typography(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Typography"
        return render_template('sb-admin/pages/ui/typography.html',
                               admin_view=self)

    @expose('/ui/icons')
    def icons(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Icons"
        return render_template('sb-admin/pages/ui/icons.html',
                               admin_view=self)

    @expose('/ui/grid')
    def grid(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._stubs()
        self.header = "Grid"
        return render_template('sb-admin/pages/ui/grid.html',
                               admin_view=self)

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return render_template('sb-admin/pages/login.html',
                               form=form)

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


class BlankView(admin.BaseView):

    @expose('/')
    def index(self):
        return render_template('sb-admin/pages/blank.html',
                               admin_view=self)
