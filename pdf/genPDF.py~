from fpdf import FPDF

"""
This tool generates the test in a PDF format.
"""
# TODO: MAKE THIS A CALLABLE METHOD

class PDF(FPDF):
	def header(self): #automatically called, do not call
		# Arial bold 8
		self.set_font('Arial', 'B', 8)
		# Title
		self.cell(190, 5, 'ExamIT - IT Carlow', 0, 0, align='C')
		# Line break
		self.ln(10)

	# Page footer
	def footer(self): #automatically called, do not call
		# Position at 3cm from bottom
		self.set_y(-35)
		# Arial italic 8
		self.set_font('Arial', 'B', 12)
		# content
		#pdf.image(name='carlow.png', x = 170, y = 12, w = 30, h = 29)

# TODO: DEHARDCODE
titl = 'Electronics Basics'
timeAll = '20 minutes'
lect = 'John Marks'
module = 'Advanced Electronics'
questAm = '15' #TODO: 5|10|15

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
pdf.cell(w=105,h=5, txt=titl, border=0, ln=1, align='L')
pdf.cell(w=85, h=5, txt='Time: ', border=0, ln=0, align='R')
pdf.cell(w=105, h=5, txt=timeAll, border=0, ln=1, align='L')
pdf.cell(w=85, h=5, txt='Lecturer: ', border=0, ln=0, align='R')
pdf.cell(w=105, h=5, txt=lect, border=0, ln=1, align='L')
pdf.cell(w=85, h=5, txt='Module: ', border=0, ln=0, align='R')
pdf.cell(w=105, h=5, txt=module, border=0, ln=1, align='L')
pdf.cell(w=85, h=5, txt='Questions: ', border=0, ln=0, align='R')
pdf.cell(w=105, h=5, txt=questAm, border=0, ln=1, align='L')
pdf.ln(5)
pdf.cell(w=50, h=198) #pushes question grid 4cm to the right
#TODO:(name='shortwhite.png'|'regularwhite.png'|'longwhite', h=66|132|198) 
pdf.image(name='longwhite.png', x = None, y = None, w = 80, h = 198)
pdf.output("test.pdf")
