"""
Implementação do Algoritmo Simplex do Zero
Resolve problemas de Programação Linear sem bibliotecas externas.

Autor: Victor Colen
Data: 18/11/2025
"""

import numpy as np
from typing import Tuple, List, Optional
from enum import Enum


class OptimizationStatus(Enum):
    """Status da otimização"""
    OPTIMAL = "optimal"
    UNBOUNDED = "unbounded"
    INFEASIBLE = "infeasible"
    ERROR = "error"


class SimplexSolver:
    """
    Implementação do Método Simplex para Programação Linear.

    Resolve problemas na forma:
        Minimizar: c^T × x
        Sujeito a: A × x {<=, =, >=} b
                   x >= 0

    Utiliza o Método das Duas Fases quando necessário.
    """

    def __init__(self, tolerance: float = 1e-8):
        """
        Inicializa o solver.

        Args:
            tolerance: Tolerância numérica para comparações
        """
        self.tolerance = tolerance
        self.tableau = None
        self.basis = None
        self.status = None
        self.iterations = 0
        self.max_iterations = 10000

    def solve(
        self,
        c: np.ndarray,
        A: np.ndarray,
        b: np.ndarray,
        signs: List[str],
        minimize: bool = True
    ) -> Tuple[OptimizationStatus, Optional[np.ndarray], Optional[float]]:
        """
        Resolve o problema de Programação Linear.

        Args:
            c: Vetor de coeficientes da função objetivo (n,)
            A: Matriz de restrições (m, n)
            b: Vetor de lados direitos (m,)
            signs: Lista de sinais das restrições ['<=', '=', '>=']
            minimize: True para minimizar, False para maximizar

        Returns:
            (status, solution, objective_value)
        """
        # Validação de entrada
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        c = np.array(c, dtype=float)

        if len(b) != len(signs) or A.shape[0] != len(b) or A.shape[1] != len(c):
            return OptimizationStatus.ERROR, None, None

        # Verifica se b >= 0 (se não, multiplica linha por -1)
        for i in range(len(b)):
            if b[i] < 0:
                b[i] = -b[i]
                A[i, :] = -A[i, :]
                # Inverte o sinal da restrição
                if signs[i] == '<=':
                    signs[i] = '>='
                elif signs[i] == '>=':
                    signs[i] = '<='

        # Converte para forma padrão e adiciona variáveis artificiais
        tableau, basis, artificial_vars = self._to_standard_form(c, A, b, signs, minimize)

        # Se há variáveis artificiais, usa Método das Duas Fases
        if len(artificial_vars) > 0:
            # Fase 1: Minimizar soma das variáveis artificiais
            phase1_status, phase1_basis = self._phase_one(tableau, basis, artificial_vars)

            if phase1_status != OptimizationStatus.OPTIMAL:
                return OptimizationStatus.INFEASIBLE, None, None

            # Remove variáveis artificiais e prepara para Fase 2
            tableau, basis = self._prepare_phase_two(tableau, phase1_basis, artificial_vars, c, minimize)

        # Fase 2 (ou única fase se não havia artificiais): Otimiza função objetivo original
        status = self._optimize(tableau, basis)

        if status != OptimizationStatus.OPTIMAL:
            return status, None, None

        # Extrai solução
        solution, obj_value = self._extract_solution(tableau, basis, len(c))

        return status, solution, obj_value

    def _to_standard_form(
        self,
        c: np.ndarray,
        A: np.ndarray,
        b: np.ndarray,
        signs: List[str],
        minimize: bool
    ) -> Tuple[np.ndarray, List[int], List[int]]:
        """
        Converte o problema para forma padrão do Simplex.

        Forma padrão:
            MIN/MAX: c^T × x
            s.a.: A × x = b
                  x >= 0

        Returns:
            (tableau, basis, artificial_vars)
        """
        m, n = A.shape

        # Converte maximização em minimização (multiplica c por -1)
        if not minimize:
            c = -c.copy()

        # Conta variáveis de folga, excesso e artificiais necessárias
        num_slack = sum(1 for s in signs if s == '<=')
        num_surplus = sum(1 for s in signs if s == '>=')
        num_artificial = sum(1 for s in signs if s in ['>=', '='])

        total_vars = n + num_slack + num_surplus + num_artificial

        # Cria tableau expandido: [A | I | c^T]
        # Linhas: [restricoes | funcao_objetivo]
        # Colunas: [vars_orig | slack | surplus | artificial | rhs]
        tableau = np.zeros((m + 1, total_vars + 1))

        # Preenche parte de A
        tableau[:m, :n] = A

        # Preenche c^T na última linha (função objetivo)
        tableau[m, :n] = c

        # Preenche b (lado direito)
        tableau[:m, -1] = b

        # Adiciona variáveis de folga, excesso e artificiais
        col_idx = n
        artificial_vars = []
        basis = []

        for i, sign in enumerate(signs):
            if sign == '<=':
                # Adiciona variável de folga (entra na base)
                tableau[i, col_idx] = 1
                basis.append(col_idx)
                col_idx += 1

            elif sign == '>=':
                # Adiciona variável de excesso (coef -1)
                tableau[i, col_idx] = -1
                col_idx += 1

                # Adiciona variável artificial (entra na base)
                tableau[i, col_idx] = 1
                artificial_vars.append(col_idx)
                basis.append(col_idx)
                col_idx += 1

            elif sign == '=':
                # Adiciona apenas variável artificial (entra na base)
                tableau[i, col_idx] = 1
                artificial_vars.append(col_idx)
                basis.append(col_idx)
                col_idx += 1

        return tableau, basis, artificial_vars

    def _phase_one(
        self,
        tableau: np.ndarray,
        basis: List[int],
        artificial_vars: List[int]
    ) -> Tuple[OptimizationStatus, List[int]]:
        """
        Fase 1 do Método das Duas Fases.
        Minimiza a soma das variáveis artificiais.

        Returns:
            (status, basis_updated)
        """
        # Salva função objetivo original
        original_objective = tableau[-1, :].copy()

        # Cria nova função objetivo: minimizar soma de artificiais
        m = tableau.shape[0] - 1
        tableau[-1, :] = 0
        for var in artificial_vars:
            tableau[-1, var] = 1

        # Atualiza linha objetivo para refletir base atual (elimina artificiais da base)
        for i, basic_var in enumerate(basis):
            if basic_var in artificial_vars:
                # Subtrai a linha da restrição correspondente
                tableau[-1, :] -= tableau[i, :]

        # Otimiza Fase 1
        status = self._optimize(tableau, basis)

        # Verifica se atingiu solução com artificiais = 0
        if status == OptimizationStatus.OPTIMAL:
            artificial_sum = abs(tableau[-1, -1])
            if artificial_sum > self.tolerance:
                # Artificiais não zeradas = problema inviável
                return OptimizationStatus.INFEASIBLE, basis

        # Restaura função objetivo original
        tableau[-1, :] = original_objective

        return OptimizationStatus.OPTIMAL, basis

    def _prepare_phase_two(
        self,
        tableau: np.ndarray,
        basis: List[int],
        artificial_vars: List[int],
        c_original: np.ndarray,
        minimize: bool
    ) -> Tuple[np.ndarray, List[int]]:
        """
        Prepara tableau para Fase 2 após Fase 1.
        Remove colunas de variáveis artificiais.
        """
        # Remove colunas das variáveis artificiais (em ordem reversa para não bagunçar índices)
        cols_to_keep = [i for i in range(tableau.shape[1]) if i not in artificial_vars]
        tableau = tableau[:, cols_to_keep]

        # Atualiza índices da base
        mapping = {old: new for new, old in enumerate(cols_to_keep[:-1])}  # Exclui RHS
        basis = [mapping[b] for b in basis if b not in artificial_vars]

        # Reconstrói linha objetivo com c original
        m = tableau.shape[0] - 1
        n = len(c_original)

        if not minimize:
            c_original = -c_original

        tableau[-1, :] = 0
        tableau[-1, :n] = c_original

        # Atualiza linha objetivo para refletir variáveis básicas
        for i, basic_var in enumerate(basis):
            if basic_var < n:  # Apenas variáveis originais
                # Zera coeficiente de variáveis básicas na função objetivo
                if abs(tableau[-1, basic_var]) > self.tolerance:
                    multiplier = tableau[-1, basic_var] / tableau[i, basic_var]
                    tableau[-1, :] -= multiplier * tableau[i, :]

        return tableau, basis

    def _optimize(self, tableau: np.ndarray, basis: List[int]) -> OptimizationStatus:
        """
        Executa o algoritmo Simplex no tableau.

        Returns:
            OptimizationStatus
        """
        self.iterations = 0
        m = tableau.shape[0] - 1  # Número de restrições

        while self.iterations < self.max_iterations:
            self.iterations += 1

            # 1. Seleciona variável de entrada (coluna pivô)
            entering_var = self._select_entering_variable(tableau)

            if entering_var is None:
                # Todos coeficientes na função objetivo são >= 0 (minimização)
                return OptimizationStatus.OPTIMAL

            # 2. Seleciona variável de saída (linha pivô)
            leaving_var_idx = self._select_leaving_variable(tableau, entering_var)

            if leaving_var_idx is None:
                # Nenhuma razão finita encontrada = problema ilimitado
                return OptimizationStatus.UNBOUNDED

            # 3. Atualiza base
            basis[leaving_var_idx] = entering_var

            # 4. Realiza operação de pivoteamento
            self._pivot(tableau, leaving_var_idx, entering_var)

        # Excedeu número máximo de iterações
        return OptimizationStatus.ERROR

    def _select_entering_variable(self, tableau: np.ndarray) -> Optional[int]:
        """
        Seleciona variável de entrada usando regra de Bland (menor índice).
        Previne ciclagem.

        Para minimização: escolhe variável com coeficiente negativo na função objetivo.
        """
        obj_row = tableau[-1, :-1]  # Exclui RHS

        # Encontra índices com coeficientes negativos
        candidates = np.where(obj_row < -self.tolerance)[0]

        if len(candidates) == 0:
            return None

        # Regra de Bland: menor índice
        return int(candidates[0])

    def _select_leaving_variable(self, tableau: np.ndarray, entering_var: int) -> Optional[int]:
        """
        Seleciona variável de saída usando teste da razão mínima.
        """
        m = tableau.shape[0] - 1
        column = tableau[:m, entering_var]
        rhs = tableau[:m, -1]

        min_ratio = float('inf')
        leaving_idx = None

        for i in range(m):
            if column[i] > self.tolerance:  # Apenas coeficientes positivos
                ratio = rhs[i] / column[i]

                # Regra de Bland em caso de empate
                if ratio < min_ratio - self.tolerance:
                    min_ratio = ratio
                    leaving_idx = i
                elif abs(ratio - min_ratio) < self.tolerance:
                    # Empate: escolhe menor índice da variável básica
                    if leaving_idx is None or i < leaving_idx:
                        leaving_idx = i

        return leaving_idx

    def _pivot(self, tableau: np.ndarray, pivot_row: int, pivot_col: int):
        """
        Realiza operação de pivoteamento no tableau.
        """
        pivot_element = tableau[pivot_row, pivot_col]

        # Normaliza linha do pivô
        tableau[pivot_row, :] /= pivot_element

        # Elimina coluna do pivô nas outras linhas
        for i in range(tableau.shape[0]):
            if i != pivot_row and abs(tableau[i, pivot_col]) > self.tolerance:
                multiplier = tableau[i, pivot_col]
                tableau[i, :] -= multiplier * tableau[pivot_row, :]

    def _extract_solution(
        self,
        tableau: np.ndarray,
        basis: List[int],
        num_original_vars: int
    ) -> Tuple[np.ndarray, float]:
        """
        Extrai solução ótima do tableau.

        Returns:
            (solution_vector, objective_value)
        """
        m = tableau.shape[0] - 1
        solution = np.zeros(num_original_vars)

        for i, basic_var in enumerate(basis):
            if basic_var < num_original_vars:
                solution[basic_var] = tableau[i, -1]

        # Valor da função objetivo (negativo do valor no tableau para minimização)
        obj_value = tableau[-1, -1]

        return solution, obj_value

    def get_iterations(self) -> int:
        """Retorna número de iterações realizadas"""
        return self.iterations

    def print_tableau(self):
        """Imprime tableau para debug (opcional)"""
        if self.tableau is not None:
            print("\nTableau:")
            print(self.tableau)
            print(f"\nBase: {self.basis}")


def solve_linear_program(
    c: np.ndarray,
    A: np.ndarray,
    b: np.ndarray,
    signs: List[str],
    minimize: bool = True
) -> dict:
    """
    Interface simplificada para resolver programas lineares.

    Args:
        c: Coeficientes da função objetivo
        A: Matriz de restrições
        b: Lados direitos
        signs: Lista de sinais ['<=', '=', '>=']
        minimize: True para minimizar, False para maximizar

    Returns:
        {
            'status': OptimizationStatus,
            'x': np.ndarray ou None,
            'fun': float ou None,
            'iterations': int,
            'success': bool,
            'message': str
        }
    """
    solver = SimplexSolver()
    status, x, fun = solver.solve(c, A, b, signs, minimize)

    messages = {
        OptimizationStatus.OPTIMAL: "Otimização concluída com sucesso",
        OptimizationStatus.UNBOUNDED: "Problema ilimitado - função objetivo pode diminuir infinitamente",
        OptimizationStatus.INFEASIBLE: "Problema inviável - não há solução que satisfaça todas as restrições",
        OptimizationStatus.ERROR: "Erro durante otimização"
    }

    return {
        'status': status,
        'x': x,
        'fun': fun,
        'iterations': solver.get_iterations(),
        'success': status == OptimizationStatus.OPTIMAL,
        'message': messages.get(status, "Status desconhecido")
    }


# Testes básicos
if __name__ == "__main__":
    print("=== Teste do Simplex Solver ===\n")

    # Teste 1: Problema simples
    print("Teste 1: Problema de maximização simples")
    print("MAX: 3x1 + 2x2")
    print("s.a.: x1 + x2 <= 4")
    print("      2x1 + x2 <= 5")
    print("      x1, x2 >= 0")

    c = np.array([3.0, 2.0])
    A = np.array([[1.0, 1.0],
                  [2.0, 1.0]])
    b = np.array([4.0, 5.0])
    signs = ['<=', '<=']

    result = solve_linear_program(c, A, b, signs, minimize=False)
    print(f"Status: {result['status'].value}")
    print(f"Solução ótima: x = {result['x']}")
    print(f"Valor ótimo: {result['fun']}")
    print(f"Iterações: {result['iterations']}\n")

    # Teste 2: Problema com restrição de igualdade
    print("Teste 2: Problema com restrição de igualdade")
    print("MIN: 2x1 + 3x2")
    print("s.a.: x1 + x2 = 10")
    print("      x1 >= 3")
    print("      x2 >= 2")

    c = np.array([2.0, 3.0])
    A = np.array([[1.0, 1.0],
                  [1.0, 0.0],
                  [0.0, 1.0]])
    b = np.array([10.0, 3.0, 2.0])
    signs = ['=', '>=', '>=']

    result = solve_linear_program(c, A, b, signs, minimize=True)
    print(f"Status: {result['status'].value}")
    print(f"Solução ótima: x = {result['x']}")
    print(f"Valor ótimo: {result['fun']}")
    print(f"Iterações: {result['iterations']}\n")
