from sympy.logic.boolalg import to_cnf
#from sympy.abc import A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z

import sqlparse
from sqlparse import sql,tokens

import re

def where_to_cnf(where_token):
	#clause = sql.TokenList(where_token.tokens[1:-1])
	symbols = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')
	comparisons = {}
	trans_form = ''
	sym_idx = 0
	tok_idx = 0
	subtokens = list(where.flatten())
	#print tokens[0].ttype
	#if(subtokens[tok_idx].ttype == tokens.Token.Operator.Comparison):
		#print 'einai comparison'
	#else:
		#print 'den einai comparison'
	n=len(subtokens)
	while (tok_idx < n and sym_idx < 24):
	
		#print tok_idx, ' ' ,subtokens[tok_idx].ttype,' ',subtokens[tok_idx].normalized,' ' 
		if subtokens[tok_idx].ttype in  tokens.Token.Literal: print 'einai kai literal'
		
		#parenthesis handling
		if(subtokens[tok_idx].ttype == tokens.Token.Punctuation and subtokens[tok_idx].value in '()'):
			trans_form += subtokens[tok_idx].value
		#logical operators handling
		elif(subtokens[tok_idx].ttype == tokens.Token.Keyword and subtokens[tok_idx].normalized in ('NOT','AND','OR') or subtokens[tok_idx].value == 'not' ):
			if(subtokens[tok_idx].normalized == 'OR'):
				trans_form += '|'
			elif(subtokens[tok_idx].normalized == 'AND'):
				trans_form += '&'
			else:
				trans_form += '~'
			
		#comparisons handling
		elif(subtokens[tok_idx].ttype == tokens.Token.Operator.Comparison):
			comparison_group = ()
			#print comparison_group
			left = subtokens[:tok_idx]
			left = left[::-1]
			#print left ,'\n reversed left: ',left[::-1]
			
			for i in range(len(left)):
				if(left[i].ttype == tokens.Token.Name and left[i+1].value =='.' and left[i+2].ttype == tokens.Token.Name):
					comparison_group += (left[i],left[i+1],left[i+2])
					break;
				elif(left[i].ttype in tokens.Token.Literal):
					comparison_group += (left[i],)
					break;
			comparison_group = comparison_group[::-1]
			comparison_group += (subtokens[tok_idx],)		
			right = subtokens[tok_idx+1:]
			#print right,'\n'
			
			for i in range(len(right)):
				if(i == len(right)-1):
					comparison_group += (right[i],)
					break;
				else:
					if(right[i].ttype == tokens.Token.Name and right[i+1].value =='.' and right[i+2].ttype == tokens.Token.Name):
						comparison_group += (right[i],right[i+1],right[i+2]) 
						break;
					elif(right[i].ttype in tokens.Token.Literal):
						comparison_group += (right[i],)
						break;
			print " ".join(str(comp) for comp in comparison_group)
			comparisons[symbols[sym_idx]] = comparison_group
			trans_form += symbols[sym_idx]
			sym_idx +=1
		
		tok_idx += 1
	print 'arxiki formula',trans_form , 'cnf : ',to_cnf(trans_form).__str__()
	print sympylogic_to_symbolic(to_cnf(trans_form).__str__())	



def sympylogic_to_symbolic(sympy_logic_str):
	symbolic_form = ''
	
	#Transform negations from Not(S) to ~S
	reg = re.compile('Not\([A-Z]\)')
	negations = reg.findall(sympy_logic_str)
	if(len(negations)>0):
		for negative in negations:
			symbols = re.findall(r'(?!Not)[A-Z]', negative)
			#print 'negatives stin arxiki formula: ',symbols
			for symbol in symbols:
				sympy_logic_str = sympy_logic_str.replace(negative, '~'+symbol);
				
	#If it is in simple cnf already return the clause
	reg = re.compile('^And\((~?[A-Z],?\s?)*\)')
	cnf = reg.match(sympy_logic_str)
	#print sympy_logic_str
	if(cnf is not None):
		print 'cnf>0',cnf.group(),' klasi tis cnf ',cnf.__class__.__name__
		sym = re.findall(r'(?!And)~?[A-Z]', cnf.group())
		for i,sy in enumerate(sym):
			if(i == (len(sym)-1)):
				symbolic_form += sy
			else:
				symbolic_form += sy+' & '
	
	#if not in cnf already convert disjunctions
	disjunctions =  re.findall(r'Or\((?:~?\w,?\s?)*\)', sympy_logic_str)
	if(len(disjunctions)>0):
		#symbolic_form = ''
		for x,dis in enumerate(disjunctions):
			symbolic_form = ''
			symbolic_form += '('
			symbols = re.findall(r'(?<!\w)~?\w(?!\w)',dis)
			for i,symbol in enumerate(symbols):
				if(i == (len(symbols)-1)):
					symbolic_form += symbol
				else:
					symbolic_form += symbol+' | '
			symbolic_form += ')'
			sympy_logic_str = sympy_logic_str.replace(dis, symbolic_form)
	
	#replace the commas with ampersands and return symbolic cnf
	commas = re.findall(r',',sympy_logic_str)
	if(len(commas)>0):
		for comma in commas:
			sympy_logic_str = sympy_logic_str.replace(comma,' &')
	sympy_logic_str = re.sub('And', '', sympy_logic_str)
	print 'Teliki morfi se cnf : ',sympy_logic_str
	

	
#--------------------------debugging-----------------------
#sql_test = 'select v1.name as nom,V2.code,count(V2.id) from view1 as v1, view2 as V2 where (v1.code="12345" and v1.id<>2.9) or not( v1.id!=v2.id and v2.stuff=0) group by nom;'
#sql_test='select * from v1 where not(v1.id!=123 or  v1.id=v2.name) and (v1.name="kati" or v1.code=g.kati);'
sql_test = 'select * from t where  v1=10 or not v2=5'
parsed=sqlparse.parse(sql_test)
for where in parsed[0].tokens:
	if(isinstance(where,sql.Where)):
		where_to_cnf(where)
