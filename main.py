import sys
import random
import math
from prettytable import PrettyTable

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
	obj, vars_profits = func.split(' ')
	profits = list(map(
			lambda x : int(x.split('X')[0]), 
			vars_profits.split('+')
		)
	)
	
	print('Cantidad de variables:', vars)
	print('Restricción de pesos:', weigths, '<=', max_weigth)
	print('Función Objetivo:', obj, profits)
	return int(vars), weigths, int(max_weigth), obj, profits

def generate_initial_sol(n):
	return [0] * n

def generate_neighborhood(solution):
	neighborhood = []
	vars = len(solution)
	for i in range(vars):
		neighbour = solution.copy()
		neighbour[i] = int(not neighbour[i])
		neighborhood.append(neighbour)
	return neighborhood

def generate_evaluation_func(profits, weigths):
	C = sum(profits) / sum(weigths)
	def evaluation_func(solution, overweight = 0):
		penalty = overweight * C
		vars = len(solution)
		sum = 0
		for i in range(vars):
			sum = sum + solution[i] * profits[i]
		return sum - penalty
	return evaluation_func

def generate_weigth_func(weigths):
	def weigth_func(solution):
		vars = len(solution)
		sum = 0
		for i in range(vars):
			sum = sum + solution[i] * weigths[i]
		return sum
	return weigth_func


def simulated_annealing(vars, weigths, max_weigth, profits):
	MAX_ITERARIONS = 20
	INITIAL_TEMP = 10
	TEMP_VARIATION = 0.9

	# Config PrettyTable
	table = PrettyTable()
	table.field_names = ["It.", "sol. actual (calidad)", "peso", "sobrepeso", "T", "delta eval", "p", "decisión", "mejor solución"]

	# Generate initial solution
	initial_sol = generate_initial_sol(vars)

	# Generate evaluation function
	evaluation_func = generate_evaluation_func(profits, weigths)

	# Generate weigth function
	weigth_func = generate_weigth_func(weigths)

	current_eval = evaluation_func(initial_sol)
	#print(f'Solución inicial: {initial_sol} ==> {current_eval}')

	best_sol = initial_sol
	current_sol = initial_sol
	current_temp = INITIAL_TEMP

	table.add_row([0, f'{tuple(initial_sol)} ({current_eval})', '', '', '', '', '', '', f'{tuple(initial_sol)} ({current_eval})'])
	table.add_row([''] * len(table.field_names))

	break_flag = False
	for i in range(MAX_ITERARIONS):
		#print(f'\n\nSolución: {current_sol}')
		# Generate neighborhood and sort it randomly
		neighborhood = generate_neighborhood(current_sol)
		random.shuffle(neighborhood)

		# Iterate the neighborhood looking for an improvement
		#print('Recorriendo el vecindario...')
		for neighbour in neighborhood:
			weigth = weigth_func(neighbour)
			overweight = weigth - max_weigth if weigth > max_weigth else 0
			eval = evaluation_func(neighbour, overweight)
			#print(f'\n\t{neighbour} ==> {eval}')
			#print(f'\tTemperatura: {current_temp}')
			delta_eval = eval - current_eval
			#print(f'\tDelta evaluación: {delta_eval}')
			p = math.exp(delta_eval/current_temp)
			rand = random.random()
			#print(f'\t{p} > {rand} = {p > rand}')
			
			if p > rand:
				current_sol = neighbour
				current_eval = eval
				if eval > evaluation_func(best_sol, overweight):
					best_sol = neighbour
				break_flag =  True

			table.add_row([
				i+1 if i != '' else '', 								# Iteration
				f'{tuple(neighbour)} ({eval})', 						# Current solution
				weigth,
				overweight,
				round(current_temp, 2), delta_eval, 					# Temperature
				round(p, 2), 											# Evaluation Delta
				f'{round(p, 2)} > {round(rand, 2)} = {p > rand}', 		# Decision
				f'{tuple(best_sol)} ({evaluation_func(best_sol)})'		# Best Solution
			])

			i = ''
			if break_flag:
				break_flag = False
				break
		else:
			break
		
		current_temp = current_temp * TEMP_VARIATION
		table.add_row([''] * len(table.field_names))
		

	print(table)
	return best_sol


	
if __name__ == '__main__':
	if len(sys.argv) != 2:
		sys.exit(f'USO:\npython {sys.argv[0]} <instance-path>')

	filename = sys.argv[1]
	print('Parseando intancia:', filename)
	try:
		vars, weigths, max_weigth, obj, profits = parser(filename)
	except FileNotFoundError:
		sys.exit(f'Archivo {filename} no encontrado')

	best_sol = simulated_annealing(vars, weigths, max_weigth, profits)
	print(f'Solución Final {best_sol}')