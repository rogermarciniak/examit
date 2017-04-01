from fpdf import FPDF


"""
This tool generates the test in a PDF format.
"""


class PDF(FPDF):

    def header(self):  # automatically called, do not call
        # Arial bold 8
        self.set_font('Arial', 'B', 8)
        # Title
        self.cell(190, 5, 'ExamIT - IT Carlow', 0, 0, align='C')
        # Line break
        self.ln(10)

    # Page footer
    def footer(self):  # automatically called, do not call
        # Position at 2cm from bottom
        self.set_y(-20)
        # Arial italic 8
        self.set_font('Arial', 'B', 12)
        # content
        # pdf.image(name='carlow.png', x = 170, y = 12, w = 30, h = 29)


# when called, generates a PDF document of the test
# the library doesn't allow for a cleaner way of doing this
def generate(test):
    pdf = PDF()
    pdf.set_margins(left=10, top=5)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=47, h=7, txt='C001', border='B', ln=0)
    pdf.cell(w=13)
    pdf.cell(w=70, h=7, txt=' ANSWERBOOK ', border=0, ln=1, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(100)
    pdf.cell(w=47, h=7, txt='STUDENT NUMBER', border=0, ln=1, align='L')
    pdf.set_text_color(0)
    pdf.ln(2)
    pdf.cell(w=85, h=5, txt='Title: ', border=0, ln=0, align='R')
    pdf.cell(w=105, h=5, txt=test['TITLE'], border=0, ln=1, align='L')
    pdf.cell(w=85, h=5, txt='Time: ', border=0, ln=0, align='R')
    pdf.cell(w=105, h=5, txt=test['TIME_ALLOWED'], border=0, ln=1, align='L')
    pdf.cell(w=85, h=5, txt='Lecturer: ', border=0, ln=0, align='R')
    pdf.cell(w=105, h=5, txt=test['LECTURER'], border=0, ln=1, align='L')
    pdf.cell(w=85, h=5, txt='Module: ', border=0, ln=0, align='R')
    pdf.cell(w=105, h=5, txt=test['MODULE'], border=0, ln=1, align='L')
    pdf.cell(w=85, h=5, txt='Questions: ', border=0, ln=0, align='R')
    pdf.cell(w=105, h=5, txt=str(test['QUESTCNT']), border=0, ln=1, align='L')
    pdf.ln(5)
    pdf.cell(w=50, h=198)  # pushes question grid to the right

    if test['QUESTCNT'] == 5:
        type = 'pdf/shortwhite.png'
        height = 66
    elif test['QUESTCNT'] == 10:
        type = 'pdf/regularwhite.png'
        height = 132
    else:  # questionAm == 15
        type = 'pdf/longwhite.png'
        height = 198

    # question grid
    pdf.image(name=type, x=None, y=None, w=80, h=height)

    # adds a question sheet to the test
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=190, h=7, txt=' QUESTION SHEET ', border=0, ln=1, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.ln(10)
    letter = 'abcde'
    for n, q in enumerate(test['QUESTIONS']):
        pdf.cell(w=10, h=5, txt="{}. ".format(n + 1), ln=0, align='R')
        pdf.cell(w=160, h=5, txt=str(q['QUESTION']), border=0, ln=1, align='L')
        pdf.ln(1)
        for l, a in zip(letter, q['ANSWERS']):
            pdf.cell(w=20, h=5, txt="{}. ".format(l), ln=0, align='C')
            pdf.cell(w=170, h=5, txt=a, border=0, ln=1, align='L')
        pdf.ln(3)
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 13)
    pdf.cell(w=190, h=7, txt='Test completion guidelines', ln=1, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.ln(2)
    guidelines = ['Only use pen inside the answer circles and for student no.',
                  'Try not to go outside the circles when marking them',
                  'Try to mark only one circle in each row',
                  'The circle filled in more, will be considered your answer',
                  'Only return the answerbook']
    for n, guide in enumerate(guidelines):
        pdf.cell(w=20, h=5, txt='{}. '.format(n + 1), ln=0, align='R')
        pdf.cell(w=160, h=5, txt=guide, border=0, ln=1, align='L')

    # save file, same name, will always be overwritten for space conservation
    fname = "pdf/ptest.pdf"
    pdf.output(fname)
    return fname
