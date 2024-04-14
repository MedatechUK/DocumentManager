
cond13=>condition: for f in [f for f in Path('s:/').glob('**/*') if (f.is_file() and (f.suffix == '.jpeg'))]
op77=>operation: fi = file(f)
cond80=>condition: if (not fi.err)
op84=>operation: ad = True
cond87=>condition: for i in files
cond107=>condition: if i.Compare(fi)
sub111=>subroutine: i.AddPage(f)
op113=>operation: ad = False
sub115=>subroutine: break
cond123=>operation: files.append(fi) if  ad

cond13(yes)->op77
op77->cond80
cond80(yes)->op84
op84->cond87
cond87(yes)->cond107
cond107(yes)->sub111
sub111->op113
op113->sub115
cond107(no)->cond87
cond87(no)->cond123
cond80(no)->cond13
cond123->cond13
