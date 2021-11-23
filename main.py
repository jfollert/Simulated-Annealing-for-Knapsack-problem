import sys
import random
import math
from prettytable import PrettyTable
import numpy as np

MAX_ITERARIONS = 20
INITIAL_TEMP = 10
TEMP_VARIATION = 0.9
PENALTY_WEIGHT = 7

# Config PrettyTable
table = PrettyTable()
table.field_names = ["It.", "sol. actual (calidad)", "peso", "sobrepeso", "T", "delta eval", "p", "decisión", "mejor solución"]
#prev_row = []

def parser(filename):
	file = open(filename, 'r')
	text = file.read().strip()
	file.close()

	vars, cons, func = text.split('\n\n')

	# Parse weight constraint
	vars_weights, max_weight =  cons.split('<=')
	weights = list(map(
			lambda x : int(x.split('X')[0]), 
			vars_weights.split('+')
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
	print('Restricción de pesos:', weights, '<=', max_weight)
	print('Función Objetivo:', obj, profits)
	return int(vars), weights, int(max_weight), obj, profits

def generate_initial_sol(n, max_weight=0):
	initial_sol = [0] * n
	initial_sol = list(map(
		lambda x : x if random.random() > 0.5 else int(not x),
		initial_sol
	))
	return initial_sol

def generate_neighborhood(solution):
	neighborhood = []
	vars = len(solution)
	for i in range(vars):
		neighbour = solution.copy()
		neighbour[i] = int(not neighbour[i])
		neighborhood.append(neighbour)
	return neighborhood

def generate_evaluation_func(profits, weights):
	C = sum(profits) / sum(weights)
	def evaluation_func(solution, overweight = 0):
		penalty = overweight * PENALTY_WEIGHT * C
		sum = np.dot(
			np.array(profits), 
			np.array(solution)
		)
		return sum - penalty
	return evaluation_func

def generate_weight_func(weights):
	return lambda solution : np.dot(
		np.array(weights), 
		np.array(solution)
	)

def add_table_row(table, row):
	columns = len(table.field_names)
	if row == []: 
		table.add_row([''] * columns)
	else:
		table.add_row(row)

def simulated_annealing(vars, weights, max_weight, profits):
	# Generate initial solution
	initial_sol = generate_initial_sol(vars)

	# Generate evaluation function
	evaluation_func = generate_evaluation_func(profits, weights)

	# Generate weight function
	weight_func = generate_weight_func(weights)

	init_weight = weight_func(initial_sol)
	init_overweight = init_weight - max_weight if init_weight > max_weight else 0
	current_eval = evaluation_func(initial_sol, init_overweight)
	best_sol = initial_sol
	best_eval = current_eval
	current_sol = initial_sol
	current_temp = INITIAL_TEMP
	row = [
		0,
		f'{tuple(initial_sol)} ({round(current_eval, 2)})',
		weight_func(initial_sol),
		init_overweight,
		'', '', '', '', 
		f'{tuple(initial_sol)} ({current_eval})']
	add_table_row(table, row)
	add_table_row(table, [])

	break_flag = False
	for i in range(MAX_ITERARIONS):
		# Generate neighborhood and sort it randomly
		neighborhood = generate_neighborhood(current_sol)
		random.shuffle(neighborhood)

		# Iterate the neighborhood looking for an improvement
		for neighbour in neighborhood:
			weight = weight_func(neighbour)
			overweight = weight - max_weight if weight > max_weight else 0
			eval = evaluation_func(neighbour, overweight)
			delta_eval = eval - current_eval
			p = math.exp(delta_eval/current_temp)
			rand = random.random()
			
			if p > rand:
				current_sol = neighbour
				current_eval = eval
				if eval > best_eval:
					best_sol = neighbour
					best_eval = eval
				break_flag =  True

			row = [
				i+1 if i != '' else '', 								# Iteration
				f'{tuple(neighbour)} ({round(eval, 2)})', 				# Current solution
				weight,
				overweight,
				round(current_temp, 2), 								# Temperature
				round(delta_eval, 2), 									# Evaluation Delta
				round(p, 2), 											# p
				f'{round(p, 2)} > {round(rand, 2)} = {p > rand}', 		# Decision
				f'{tuple(best_sol)} ({evaluation_func(best_sol)})'		# Best Solution
			]
			add_table_row(table, row)

			i = ''
			if break_flag:
				break_flag = False
				break
		else:
			break
		
		current_temp = current_temp * TEMP_VARIATION
		add_table_row(table, [])
		

	print(table)
	print(f'=> Solución Final: {tuple(best_sol)}')
	print(f'=> Ganancia: {round(best_eval, 2)}')
	print(f'=> Peso: {weight_func(best_sol)}')
	return best_sol


	
if __name__ == '__main__':
	if len(sys.argv) != 2:
		sys.exit(f'USO:\npython {sys.argv[0]} <instance-path>')

	filename = sys.argv[1]
	print('Parseando intancia:', filename)
	try:
		vars, weights, max_weight, obj, profits = parser(filename)
	except FileNotFoundError:
		sys.exit(f'Archivo {filename} no encontrado')

	best_sol = simulated_annealing(vars, weights, max_weight, profits)
	#print(f'Solución Final {best_sol}')