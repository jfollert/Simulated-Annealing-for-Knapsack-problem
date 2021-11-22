import sys

def parser(filename):
	file = open(filename, 'r')
	text = file.read().strip()
	file.close()

	vars, cons, func = text.split('\n\n')

	# Parse weigth constraint
	vars_weigths, max_weigth =  cons.split('<=')
	weigths = list(map(
			lambda x : int(x.split('X')[0]), 
			vars_weigths.split('+')
		)
	)
	
	# Parse function
	obj, vars_profit = func.split(' ')
	profit = list(map(
			lambda x : int(x.split('X')[0]), 
			vars_profit.split('+')
		)
	)
	
	print('Cantidad de variables:', vars)
	print('Restricción de pesos:', weigths, '<=', max_weigth)
	print('Función Objetivo:', obj, profit)
	return int(vars), weigths, int(max_weigth), obj, profit
	
if __name__ == '__main__':
	if len(sys.argv) != 2:
		#raise Exception('Falta ingresar ruta de instancia a resolver')
		sys.exit(f'USO:\npython {sys.argv[0]} <instance-path>')

	filename = sys.argv[1]
	print('Parseando intancia:', filename)
	try:
		vars, weigths, max_weigth, obj, profit = parser(filename)
	except FileNotFoundError:
		sys.exit(f'Archivo {filename} no encontrado')