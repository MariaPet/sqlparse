from sympy.logic.boolalg import to_cnf
from sympy.abc import A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z

import sqlparse
from sqlparse import sql,tokens

def where_to_cnf(where_token):
	#clause = sql.TokenList(where_token.tokens[1:-1])
	symbols = (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z)
	identifiers = {}
	trans_form = ''
	sym_idx = 0
	tok_idx = 0
	subtokens = list(where.flatten())
	#print tokens[0].ttype
	if(subtokens[tok_idx].ttype == tokens.Token.Operator.Comparison):
		print 'einai comparison'
	else:
		print 'den einai comparison'
	n=len(subtokens)
	while tok_idx < n:
		print tok_idx, ' ' ,subtokens[tok_idx].ttype
		if(subtokens[tok_idx].ttype == tokens.Token.Operator.Comparison):
			comparison_group = ('kati',)
			print comparison_group
			left = subtokens[:tok_idx]
			left = left[::-1]
			#print left ,'\n reversed left: ',left[::-1]
			for i in range(len(left)):
				if(left[i].ttype == tokens.Token.Name and left[i+1].value =='.' and left[i+2].ttype == tokens.Token.Name):
					comparison_group += (left[i],left[i+1],left[i+2],subtokens[tok_idx])
				elif((left[i].ttype == tokens.Token.Name or left[i].ttype in tokens.Token.Literal) and left[i+1].ttype == tokens.Token.Text.Whitespace):
					comparison_group += (left[i],subtokens[tok_idx])
			right = subtokens[tok_idx+1:]
			#print right,'\n'
			for i in range(len(right)):
				if(right[i].ttype == tokens.Token.Name and right[i+1].value =='.' and right[i+2].ttype == tokens.Token.Name):
					comparison_group += (right[i],right[i+1],right[i+2]) 
				elif((right[i].ttype == tokens.Token.Name or right[i].ttype in tokens.Token.Literal) and (right[i+1].ttype == tokens.Token.Text.Whitespace or right[i+1] is None)):
					comparison_group += (right[i],)
			print 'to comparison group:',comparison_group
		else:
			print 'den einai comparison'
		
		tok_idx += 1
	"""	
	while tok_idx < n:
		if(subtokens[tok_idx].ttype is tokens.Token.Operator.Comparison):
			comparison_group = ('kati',)
			print comparison_group
			left = subtokens[:idx]
			for x,attribute in enumerate(left[::-1]):
				if(attribute.ttype == tokens.Token.Name and attribute.token_next(x).value =='.' and attribute.token_next(x+1).ttype == tokens.Token.Name):
					comparison_group += (left[x],left[x+1],left[x+2],tokens[tok_idx]) 
				elif((attribute.ttype == tokens.Token.Name or attribute.ttype in tokens.Token.Literal) and attribute.token_next(x,skip_ws=False).ttype == tokens.Token.Text.Whitespace):
					comparison_group += (left[x],tokens[tok_idx])
			right = subtokens[idx+1:]
			for x,attribute in enumerate(right):
				if(attribute.ttype == tokens.Token.Name and attribute.token_next(x).value =='.' and attribute.token_next(x+1).ttype == tokens.Token.Name):
					comparison_group += (right[x],right[x+1],right[x+2]) 
				elif((attribute.ttype == tokens.Token.Name or attribute.ttype in tokens.Token.Literal) and attribute.token_next(x,skip_ws=False).ttype == tokens.Token.Text.Whitespace):
					comparison_group += (right[x])
			print(comparison_group)
			tok_idx+=1"""
			
	"""	if(sym_idx < len(symbols)):
					identifiers[symbols[sym_idx]] = tokens[tok_idx].value + tokens[tok_idx+1].value + tokens[tok_idx+2].value
					trans_form += symbols[sym_idx]
					sym_idx += 1
					tok_idx += 3
		elif(tokens[tok_idx].ttype == tokens.Token.Name and tokens[tok_idx].token_next(tok_idx).value != '.'):
			if(sym_idx < len(symbols)):
				identifiers[symbols[sym_idx]] = tokens[tok_idx].value
				trans_form += symbols[sym_idx]
				sym_idx += 1
				tok_idx += 1
		elif(tokens[tok_idx].ttype == tokens.Token.Name and):
		else:
			translated += token.value
	
	
	for token in proposition:
		if(isinstance(token,sql.Parenthesis)):
			parentheses += (token,)
		if(isinstance(token,sql.Function)):
			for idx,subtoken in enumerate(token.get_sublists()):
				if(isinstance(subtoken,sql.Identifier) and subtoken.normalized == 'NOT' and isinstance(subtoken.token_next(idx),sql.Parenthesis)):
					parentheses += (token,)"""
					
						
	#print proposition, '\n',parentheses

#--------------------------debugging-----------------------
sql_test = 'select v1.name as nom,V2.code,count(V2.id) from view1 as v1, view2 as V2 where (v1.code="12345" and v1.id<>2.9) or v1.id!=v2.id and v2.stuff=0 group by nom;'
parsed=sqlparse.parse(sql_test)

for where in parsed[0].tokens:
	if(isinstance(where,sql.Where)):
		where_to_cnf(where)
