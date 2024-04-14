op2=>operation: from pathlib import Path
op4=>operation: from scanfile import file
op6=>operation: from reportlab.pdfgen import canvas
op8=>operation: PREAUTH = False
op10=>operation: files = []
cond13=>condition: for f in [f for f in Path('s:/').glob('**/*') if (f.is_file() and (f.suffix == '.jpeg'))]
op73=>operation: fi = file(f)
cond76=>condition: if (not fi.err)
op80=>operation: ad = True
cond83=>condition: for i in files
cond101=>condition: if i.Compare(fi)
sub105=>subroutine: i.AddPage(f)
op107=>operation: ad = False
cond115=>operation: files.append(fi) if  ad
cond131=>condition: for f in files
op284=>operation: p = f.NextPage()
cond287=>condition: while p
cond349=>condition: if p.barcode
cond354=>operation: c.save() if  f.hascanvas
cond365=>operation: PREAUTH = True if  p.preauth
op375=>operation: c = f.CreatePDF(p, preauth=PREAUTH)
cond392=>operation: f.AppendPDF(p, c) if  f.hascanvas
op402=>operation: p = f.NextPage(p.pageid)
cond380=>operation: c.showPage() if  f.hascanvas
cond407=>operation: c.save() if  f.hascanvas
cond418=>operation: pdf.dbSave() while  pdf in f.PDFfiles
sub430=>subroutine: f.delPages()

op2->op4
op4->op6
op6->op8
op8->op10
op10->cond13
cond13(yes)->op73
op73->cond76
cond76(yes)->op80
op80->cond83
cond83(yes)->cond101
cond101(yes)->sub105
sub105->op107
op107->cond83
cond101(no)->cond83
cond83(no)->cond115
cond115->cond13
cond76(no)->cond13
cond13(no)->cond131
cond131(yes)->op284
op284->cond287
cond287(yes)->cond349
cond349(yes)->cond354
cond354->cond365
cond365->op375
op375->cond392
cond392->op402
op402(left)->cond287
cond349(no)->cond380
cond380->cond392
cond287(no)->cond407
cond407->cond418
cond418->sub430
sub430(left)->cond131

