#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# setup.py to install spacepy

__version__ = "$Revision: 1.9 $, $Date: 2010/05/26 22:00:01 $"
__author__ = 'Josef Koller, Los Alamos National Lab (jkoller@lanl.gov)'

# -------------------------------------
def compile_oneralib():
	
	# compile oneralib
	import os, sys
	
	
	os.chdir('spacepy/onerapy/onera_lib_V4.1')
	
	F90files = ['source/onera_desp_lib.f', 'source/CoordTrans.f']
	functions = ['make_lstar1', 'make_lstar_shell_splitting1', \
		'coord_trans1 find_magequator1', 'find_mirror_point1', 
		'get_field1']
	
	# call f2py
	os.system('f2py --overwrite-signature -m onerapylib -h onerapylib.pyf '+' '.join(F90files) \
			+' only: ' + ' '.join(functions) + ' :')
	
	# intent(out) substitute list
	outlist = ['lm', 'lstar', 'blocal', 'bmin', 'xj', 'mlt', 'xout', 'bmin', 'posit', \
			'xgeo', 'bmir', 'bl', 'bxgeo']
	
	inlist = ['sysaxesin', 'sysaxesout', 'iyr', 'idoy', 'secs', 'xin']
	
	fln = 'onerapylib.pyf'
	
	print 'Substituting fortran intent(in/out) statements'
	f = open(fln, 'r')
	filestr = f.read()
	f.close()
        
	for item in inlist:
		filestr = subst( ':: '+item, ', intent(in) :: '+item, filestr)
		
	for item in outlist:
		filestr = subst( ':: '+item, ', intent(out) :: '+item, filestr)
	
	f = open(fln, 'w')
	f.write(filestr)
	f.close()

	
	# compile (platform dependent)
	os.chdir('source')
	if sys.platform == 'darwin': # then mac OS
   		os.system('gfortran -c -w -O2 -fPIC *.f')
   		os.system('libtool -static -o libBL2.a *.o')
   		os.chdir('..')
   		os.system('f2py -c onerapylib.pyf source/onera_desp_lib.f -Lsource -lBL2 --fcompiler=gnu95')
   		
	elif sys.platform == 'linux2': # then linux   	
		os.system('gfortran -c -w -O2 -fPIC *.f')
		os.system('ar -r libBL2.a *.o')
		os.system('ranlib libBL2.a')
		os.chdir('..')
		os.system('f2py -c onerapylib.pyf source/onera_desp_lib.f -Lsource -lBL2 --fcompiler=gnu95')
	else:
		print sys.platform, ' not supported at this time'
		sys.exit(1)
	
	os.system('mv -f onerapylib.so ../')
	os.chdir('../../..')
	
	return

# -------------------------------------
def subst(pattern, replacement, filestr,
          pattern_matching_modifiers=None):
          
    """
    replace pattern by replacement in file
    pattern_matching_modifiers: re.DOTALL, re.MULTILINE, etc.
    """
    
    import os, re, sys, shutil
    
    
    if pattern_matching_modifiers is not None:
    	cp = re.compile(pattern, pattern_matching_modifiers)
    else:
    	cp = re.compile(pattern)
	
	if cp.search(filestr):  # any occurence of pattern?
		filestr = cp.sub(replacement, filestr)
		
    return filestr
	
# -------------------------------------
from distutils.core import setup
import spacepy
import spacepy.toolbox as tb
import os, shutil

# run compile for onera_desp_lib first
if os.path.exists('spacepy/onerapy/onerapylib.so'):
	ans = tb.query_yes_no('\nDo you want to recompile the ONERA-DESP library?', default="no")
	if ans=='yes':
		compile_oneralib()
else:
	compile_oneralib()

# create .spacepy in $HOME and move data
HOME = os.environ['HOME']
dotfln = HOME+'/.spacepy'
if os.path.exists(dotfln+'.bak'):
	shutil.rmtree(dotfln+'.bak', ignore_errors=True)
if os.path.exists(dotfln):
	shutil.move(dotfln, dotfln+'.bak')

os.mkdir(dotfln)
os.chmod(dotfln, 0777)
os.mkdir(dotfln+'/data')
os.chmod(dotfln+'/data', 0777)
shutil.copy('spacepy/data/spacepy.rc', dotfln+'/')
shutil.copy('spacepy/data/PSDdb.pbin', dotfln+'/data')
shutil.copy('spacepy/data/tai-utc.dat', dotfln+'/data')

pkg_files = ['onerapy/onerapylib.so','onerapy/*.py', 'doc/*.*']

# run setup from distutil
setup(name='spacepy',
      version='0.1',
      description='SpacePy: Tools for Space Science Applications',
      author='Steve Morley, Josef Koller, Dan Welling, Brian Larsen',
      author_email='spacepy_mail@lanl.gov',
      url='http://spacepy.lanl.gov',
      packages=['spacepy','spacepy.sandbox'],
      package_data={'spacepy': pkg_files}
      ) 

# update/download packages

ans = tb.query_yes_no("""\n\nSpacePy requires an OMNI database and leap seconds information for full 
functionality. Would you like to download these packages? (Internet connection required) """, default="yes")
if ans=='yes':
	dir = tb.update()
	print("Data installed to " + dir)
else:
	print "WARNING: SpacePy will have limited functionality, unless you run spacepy.toolbox.update()"
	
# offer testing routine
ans = tb.query_yes_no("\nDo you want to test your SpacePy installation", default="no")
if ans=='yes':
	spacepy.test_all()

print "\nThanks for installing SpacePy."
	
