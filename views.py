import shutil
import time
from random import sample

import flask_admin as admin
import flask_login as login
from flask import (flash, redirect, render_template, request, send_file,
                   session, url_for)
from flask_admin import expose, helpers
from pymongo import MongoClient

import corrector
import genPDF
import PDF2jpg
from loginform import LoginForm

ALLOWED_EXTENSIONS = set(['pdf'])

# prepares db
client = MongoClient()
db = client.examit
cats = db.cats
quests = db.quests  # question col
tests = db.tests
results = db.results


# Create customized index view class that handles login & registration
class AdminIndexView(admin.AdminIndexView):

    # converts answer keys from ABCDE form to 01234 needed for correction
    def letter2num(self, l):
        num = ord(l) - 65
        return num

    # takes a test cursor, returns a dict of answer key items
    def getAnswerKey(self, test):
        key = {}
        for i, question in enumerate(test['QUESTIONS']):
            key[i] = self.letter2num(question['KEY'])
        return key

    # ensures the file uploaded is an allowed file type
    def allowed_file(self, filename):
        print(filename)
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            qamount = int(request.form.get('amount'))
            current_time = time.localtime()
            ctime = time.strftime('%a, %d %b %Y %H:%M:%S GMT', current_time)
            # draw n questions from category
            query = list(quests.find({"CATEGORY": categ}))
            if len(query) >= qamount:
                samp = sample(query, qamount)
                for doc in samp:
                    doc['_id'] = str(doc['_id'])
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
                return render_template('sb-admin/pages/tgenconf.html',
                                       test=test,
                                       admin_view=self)
            else:  # not enough questions in the category
                flash('Not enough questions in the selected category!',
                      category='danger')
                return redirect(url_for('admin.gentest'))

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
            session['title'] = title
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

        if request.method == 'POST':
            tfound = tests.find_one({"TITLE": session['title']})
            # generates the PDF
            pdf = genPDF.generate(tfound)  # "pdf/ptest.pdf"
            try:
                return send_file(pdf, attachment_filename='test.pdf')
            except Exception as e:
                return str(e)
        self.header = "Printout"
        return render_template('sb-admin/pages/printconfd.html',
                               admin_view=self)

    @expose('/tests/correct/', methods=['GET', 'POST'])
    def correcttest(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        found = tests.find()

        if request.method == 'POST':
            title = request.form.get('title')
            tfound = tests.find_one({"TITLE": title})
            # if request does not contain the file part
            if 'file' not in request.files:
                flash('No file was sent', category='danger')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser will
            # submit an empty part without filename
            if file.filename == '':
                flash('No file was selected', category='danger')
                return redirect(request.url)
            # if file was selected but of the wrong type
            if file and not self.allowed_file(file.filename):
                flash('Please select a .pdf file', category='danger')
                return redirect(request.url)
            # if file was selected & is correct type
            if file and self.allowed_file(file.filename):
                # FIXME: as_jpeg = PDF2jpg.convert(file)
                as_jpeg = 'el15.jpg'  # FIXME: DEHARDCODE
                # fetches the answer key corresponding to the test
                key = self.getAnswerKey(tfound)
                print(key)
                # corrects the test image using the answer key
                # returns (location, score, correct, AMOUNT)
                loc, corr, am, sc, flag = corrector.correct(as_jpeg, key)
                curr_time = time.localtime()
                ctime = time.strftime('%a, %d %b %Y %H:%M:%S GMT', curr_time)
                corrected = {"TEST": title,
                             "SCORE": sc,
                             "CORRECT": corr,
                             "AMOUNT": am,
                             "FLAG": flag,
                             "CREATED": ctime}
                result = results.insert_one(corrected)
                id = str(result.inserted_id)
                # move and give a unique name to the test image for storage
                # destination = path to file
                destination = shutil.move(loc, 'results/' + id)
                print('NEW_FILE_SAVED={}'.format(destination))
                flash("File was corrected. Visit 'Test Results' to see scores",
                      category='success')
                return render_template('sb-admin/pages/uploadtest.html',
                                       tests=found,
                                       admin_view=self)

        self.header = "Correct Test"
        return render_template('sb-admin/pages/uploadtest.html',
                               tests=found,
                               admin_view=self)

    @expose('/tests/results/')
    def results(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        # returns a list of unique test titles
        tests = results.distinct('TEST')

        self.header = "Corrected Assessments"
        return render_template('sb-admin/pages/corrected.html',
                               tests=tests,
                               admin_view=self)

    @expose('/tests/results/<test>')
    def displayresult(self, test):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        # TODO: when accessing id later (ObjectId('_id'))

        self.header = "Results: {}".format(test)
        return render_template('sb-admin/pages/listresults.html',
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
