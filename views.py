import time
from random import sample

import flask_admin as admin
import flask_login as login
from flask import flash, redirect, render_template, request, session, url_for
from flask_admin import expose, helpers
from pymongo import MongoClient

import genPDF
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

    def get_tests(self):
        columns = ["Test", "Lecturer", "Time Allowed", "Module",
                   "Questions", "Category", "Creation Date", "Unique ID"]
        found = tests.find()
        rows = []
        for t in found:
            row = []
            row.append(t['TITLE'])
            row.append(t['LECTURER'])
            row.append(t['TIME_ALLOWED'])
            row.append(t['MODULE'])
            row.append(t['QUESTCNT'])
            row.append(t['CATEGORY'])
            row.append(t['CREATED'])
            row.append(t['_id'])
            rows.append(row)
        return (columns, rows)

    def _tools(self):
        (qcols, qrows) = self.get_quests()
        self.qtable = {"questions": {"columns": qcols, "rows": qrows}}

        (ccols, crows) = self.get_cats()
        self.ctable = {"categories": {"columns": ccols, "rows": crows}}

        (tcols, trows) = self.get_tests()
        self.ttable = {"tests": {"columns": tcols, "rows": trows}}

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self.header = "Welcome to ExamIT"
        return render_template('sb-admin/pages/start.html', admin_view=self)

    @expose('/categories/', methods=['GET', 'POST'])
    def cats(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        if request.method == 'POST':
            cat = request.form.get('category').strip()
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

    @expose('/questions/display/')
    def questions(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._tools()
        self.header = "Questions"
        return render_template('sb-admin/pages/questions.html',
                               admin_view=self)

    @expose('/questions/add/', methods=['GET', 'POST'])
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

    @expose('/tests/display/', methods=['GET', 'POST'])
    def tests(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._tools()
        self.header = "Tests"
        return render_template('sb-admin/pages/tests.html',
                               admin_view=self)

    @expose('/tests/generate/', methods=['GET', 'POST'])
    def gentest(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        catlist = []
        found = cats.find()
        for c in found:
            catlist.append(c['CATEGORY'])

        catlist.sort()
        self.header = "Generate Test"
        return render_template('sb-admin/pages/tgen.html',
                               categs=catlist,
                               admin_view=self)

    @expose('/tests/confirm/', methods=['GET', 'POST'])
    def gentest_conf(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        if request.method == 'POST':
            title = request.form.get('title').strip()
            timeal = request.form.get('timeallowed').strip()
            lecturer = request.form.get('lecturer').strip()
            module = request.form.get('module').strip()
            categ = request.form.get('category').strip()
            qamount = 5  # TODO: request.form.get('amount')
            current_time = time.localtime()
            ctime = time.strftime('%a, %d %b %Y %H:%M:%S GMT', current_time)
            # draw n questions from category
            query = list(quests.find({"CATEGORY": categ}))
            if len(query) >= qamount:
                samp = sample(query, qamount)
                for doc in samp:
                    doc['_id'] = str(doc['_id'])
                    # TODO: when accessing id later (ObjectId('_id'))
                # FIXME: UnboundLocalError:
                #        local variable 'test' referenced before assignment
                test = {"TITLE": title,
                        "TIME_ALLOWED": timeal,
                        "LECTURER": lecturer,
                        "MODULE": module,
                        "CATEGORY": categ,
                        "QUESTCNT": qamount,
                        "QUESTIONS": samp,
                        "CREATED": ctime}

                db_checker = {"TITLE": title,
                              "MODULE": module,
                              "CATEGORY": categ,
                              "QUESTCNT": qamount}

                session['test'] = test
                session['db_checker'] = db_checker
            else:  # not enough questions in the category
                flash('Not enough questions in the selected category!',
                      category='danger')
            return render_template('sb-admin/pages/tgenconf.html',
                                   test=test,
                                   admin_view=self)

        self._tools()
        self.header = "Confirm Test Creation"
        return render_template('sb-admin/pages/tgenconf.html', admin_view=self)

    @expose('/tests/confirmed/', methods=['GET', 'POST'])
    def gentest_confd(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        if request.method == 'POST':
            result = tests.replace_one(session['db_checker'],
                                       session['test'],
                                       upsert=True)
            if result.modified_count == 1:
                flash('Test existed and was updated!',
                      category='info')
            else:
                flash('Test was successfully generated!',
                      category='success')
            return render_template('sb-admin/pages/tgenconfd.html',
                                   admin_view=self)

        self.header = "Generation Confirmation"
        return render_template('sb-admin/pages/tgenconfd.html',
                               admin_view=self)

    @expose('/tests/print/', methods=['GET', 'POST'])
    def printtest(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        found = tests.find()

        if request.method == 'POST':
            title = request.form.get('title')
            print('picked test title: ' + title)
            tfound = tests.find_one({"TITLE": title})
            return render_template('sb-admin/pages/printtest.html',
                                   tests=found,
                                   selected=tfound,
                                   admin_view=self)

        self.header = "Print Test"
        return render_template('sb-admin/pages/printtest.html',
                               tests=found,
                               admin_view=self)

    @expose('/tests/print/printout/', methods=['GET', 'POST'])
    def printconfd(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self.header = "Printout"
        return render_template('sb-admin/pages/printconfd.html',
                               admin_view=self)

    @expose('/tests/correct/')
    def correcttest(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self.header = "Blank"
        return render_template('sb-admin/pages/blank.html', admin_view=self)

    @expose('/tests/results/')
    def results(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self.header = "Blank"
        return render_template('sb-admin/pages/blank.html', admin_view=self)

    @expose('/blank/')
    def blank(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self.header = "Blank"
        return render_template('sb-admin/pages/blank.html', admin_view=self)

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
