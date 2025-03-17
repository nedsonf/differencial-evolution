import random
import copy
import math
from common.layout_display import LayoutDisplayMixin

class DifferentialEvolution(LayoutDisplayMixin):
    def __init__(self, pop_size, max_iter, sheet_width, sheet_height, recortes_disponiveis, F=0.8, CR=0.9):
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.recortes_disponiveis = recortes_disponiveis
        self.F = F
        self.CR = CR
        self.population = self.initialize_population()
        self.optimized_layout = None
        print("Evolução Diferencial Inicializada.")

    def initialize_population(self):
        population = []
        while len(population) < self.pop_size:
            individuo = copy.deepcopy(self.recortes_disponiveis)
            layout = []
            for recorte in individuo:
                for _ in range(100):  # Aumentado para mais tentativas
                    recorte['x'] = random.randint(0, self.sheet_width - recorte.get('largura', recorte.get('r', 0)))
                    recorte['y'] = random.randint(0, self.sheet_height - recorte.get('altura', recorte.get('r', 0)))
                    if 'rotacao' in recorte:
                        recorte['rotacao'] = random.choice([0, 90, 180, 270])  # Mais opções de rotação
                    if not self.has_overlap(recorte, layout) and self.is_within_bounds(recorte):
                        layout.append(copy.deepcopy(recorte))
                        break
                else:
                    layout = None
                    break
            if layout is not None:
                population.append(layout)
        return population

    def evaluate(self, individuo):
        layout = self.lgfi_heuristic(individuo)
        if layout is None:
            return float('-inf')
        area_utilizada = sum(r.get('largura', r.get('r', 0)) * r.get('altura', r.get('r', 0)) for r in layout)
        desperdicio = (self.sheet_width * self.sheet_height) - area_utilizada
        return -desperdicio

    def lgfi_heuristic(self, individuo):
        layout = []
        for recorte in individuo:
            for _ in range(100):
                if not self.has_overlap(recorte, layout) and self.is_within_bounds(recorte):
                    layout.append(copy.deepcopy(recorte))
                    break
            else:
                return None
        return layout

    def has_overlap(self, new_recorte, layout):
        for recorte in layout:
            if self.check_collision(new_recorte, recorte):
                return True
        return False

    def check_collision(self, recorte1, recorte2):
        if recorte1['tipo'] == 'circular' or recorte2['tipo'] == 'circular':
            return self.check_circle_collision(recorte1, recorte2)
        else:
            return self.check_rect_collision(recorte1, recorte2)

    def check_circle_collision(self, recorte1, recorte2):
        if recorte1['tipo'] == 'circular' and recorte2['tipo'] == 'circular':
            distancia_centros = math.dist([recorte1['x'], recorte1['y']], [recorte2['x'], recorte2['y']])
            return distancia_centros < (recorte1['r'] + recorte2['r'])
        return False

    def check_rect_collision(self, recorte1, recorte2):
        x1, y1, w1, h1 = recorte1['x'], recorte1['y'], recorte1.get('largura', 0), recorte1.get('altura', 0)
        x2, y2, w2, h2 = recorte2['x'], recorte2['y'], recorte2.get('largura', 0), recorte2.get('altura', 0)
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    def is_within_bounds(self, recorte):
        if recorte['tipo'] == 'circular':
            return (recorte['x'] + recorte['r'] <= self.sheet_width and
                    recorte['y'] + recorte['r'] <= self.sheet_height)
        else:
            return (recorte['x'] + recorte.get('largura', 0) <= self.sheet_width and
                    recorte['y'] + recorte.get('altura', 0) <= self.sheet_height)

    def mutate(self, target_idx):
        indices = [i for i in range(self.pop_size) if i != target_idx]
        a, b, c = random.sample(indices, 3)
        mutant = copy.deepcopy(self.population[a])
        for i in range(len(mutant)):
            if random.random() < self.CR:
                mutant[i]['x'] = max(0, min(self.sheet_width, self.population[a][i]['x'] + self.F * (self.population[b][i]['x'] - self.population[c][i]['x'])))
                mutant[i]['y'] = max(0, min(self.sheet_height, self.population[a][i]['y'] + self.F * (self.population[b][i]['y'] - self.population[c][i]['y'])))
                if 'rotacao' in mutant[i]:
                    mutant[i]['rotacao'] = random.choice([0, 90, 180, 270])
        return mutant

    def crossover(self, target, mutant):
        trial = copy.deepcopy(target)
        for i in range(len(trial)):
            if random.random() < self.CR:
                trial[i]['x'] = mutant[i]['x']
                trial[i]['y'] = mutant[i]['y']
                if 'rotacao' in trial[i]:
                    trial[i]['rotacao'] = mutant[i]['rotacao']
        return trial

    def select(self, target, trial):
        return trial if self.evaluate(trial) > self.evaluate(target) else target

    def run(self):
        best_solution = None
        best_fitness = float('-inf')
        for iteration in range(self.max_iter):
            for i in range(self.pop_size):
                mutant = self.mutate(i)
                trial = self.crossover(self.population[i], mutant)
                self.population[i] = self.select(self.population[i], trial)
                fitness = self.evaluate(self.population[i])
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = copy.deepcopy(self.population[i])
            print(f"Iteração {iteration + 1}/{self.max_iter}, Melhor Fitness: {best_fitness}")
        self.optimized_layout = best_solution
        return self.optimized_layout

    def optimize_and_display(self):
        self.display_layout(self.recortes_disponiveis, title="Initial Layout - Differential Evolution")
        self.optimized_layout = self.run()
        if self.optimized_layout is None:
            print("Erro: Nenhum layout válido foi gerado.")
            return None
        self.display_layout(self.optimized_layout, title="Optimized Layout - Differential Evolution")
        return self.optimized_layout