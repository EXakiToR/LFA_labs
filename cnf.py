from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, List, Set, Tuple

Symbol = str
RHS = Tuple[Symbol, ...]
Productions = Dict[Symbol, Set[RHS]]


@dataclass
class CFG:
    non_terminals: Set[Symbol]
    terminals: Set[Symbol]
    productions: Productions
    start_symbol: Symbol

    def copy(self) -> "CFG":
        return CFG(
            non_terminals=set(self.non_terminals),
            terminals=set(self.terminals),
            productions={k: set(v) for k, v in self.productions.items()},
            start_symbol=self.start_symbol,
        )

    def pretty(self) -> str:
        lines: List[str] = []
        lines.append(f"Vn = {sorted(self.non_terminals)}")
        lines.append(f"Vt = {sorted(self.terminals)}")
        lines.append("P = {")
        for lhs in sorted(self.productions):
            rhss = self.productions[lhs]
            rhs_text = " | ".join("".join(rhs) if rhs else "eps" for rhs in sorted(rhss))
            lines.append(f"  {lhs} -> {rhs_text}")
        lines.append("}")
        lines.append(f"Start = {self.start_symbol}")
        return "\n".join(lines)


class CNFNormalizer:
    def __init__(self) -> None:
        self._fresh_idx = 1

    def normalize(self, grammar: CFG) -> tuple[CFG, List[str]]:
        g = grammar.copy()
        log: List[str] = []

        log.append("Step 1: eliminate epsilon productions")
        self._eliminate_epsilon(g)
        log.append(g.pretty())

        log.append("Step 2: eliminate unit (renaming) productions")
        self._eliminate_unit(g)
        log.append(g.pretty())

        log.append("Step 3: eliminate inaccessible symbols")
        self._remove_inaccessible(g)
        log.append(g.pretty())

        log.append("Step 4: eliminate non-productive symbols")
        self._remove_non_productive(g)
        log.append(g.pretty())

        log.append("Step 5: convert to Chomsky Normal Form")
        self._to_cnf(g)
        log.append(g.pretty())

        return g, log

    def _eliminate_epsilon(self, g: CFG) -> None:
        nullable: Set[Symbol] = set()
        changed = True
        while changed:
            changed = False
            for lhs, rhss in g.productions.items():
                if lhs in nullable:
                    continue
                for rhs in rhss:
                    if len(rhs) == 0 or all(sym in nullable for sym in rhs):
                        nullable.add(lhs)
                        changed = True
                        break

        new_productions: Productions = {lhs: set() for lhs in g.productions}
        for lhs, rhss in list(g.productions.items()):
            for rhs in rhss:
                if len(rhs) == 0:
                    continue
                nullable_positions = [i for i, sym in enumerate(rhs) if sym in nullable]
                for mask in product([0, 1], repeat=len(nullable_positions)):
                    drop = {nullable_positions[i] for i, b in enumerate(mask) if b == 1}
                    new_rhs = tuple(sym for i, sym in enumerate(rhs) if i not in drop)
                    if len(new_rhs) == 0:
                        if lhs == g.start_symbol:
                            new_productions[lhs].add(tuple())
                    else:
                        new_productions[lhs].add(new_rhs)

        g.productions = new_productions

    def _eliminate_unit(self, g: CFG) -> None:
        unit_graph: Dict[Symbol, Set[Symbol]] = {nt: set() for nt in g.non_terminals}
        for lhs, rhss in list(g.productions.items()):
            for rhs in rhss:
                if len(rhs) == 1 and rhs[0] in g.non_terminals:
                    unit_graph[lhs].add(rhs[0])

        closure: Dict[Symbol, Set[Symbol]] = {nt: {nt} for nt in g.non_terminals}
        for nt in g.non_terminals:
            stack = [nt]
            while stack:
                cur = stack.pop()
                for nxt in unit_graph[cur]:
                    if nxt not in closure[nt]:
                        closure[nt].add(nxt)
                        stack.append(nxt)

        new_productions: Productions = {nt: set() for nt in g.non_terminals}
        for lhs in g.non_terminals:
            for reachable in closure[lhs]:
                for rhs in g.productions.get(reachable, set()):
                    if len(rhs) == 1 and rhs[0] in g.non_terminals:
                        continue
                    new_productions[lhs].add(rhs)
        g.productions = new_productions

    def _remove_inaccessible(self, g: CFG) -> None:
        reachable = {g.start_symbol}
        stack = [g.start_symbol]
        while stack:
            cur = stack.pop()
            for rhs in g.productions.get(cur, set()):
                for sym in rhs:
                    if sym in g.non_terminals and sym not in reachable:
                        reachable.add(sym)
                        stack.append(sym)

        g.non_terminals.intersection_update(reachable)
        g.productions = {lhs: set(rhss) for lhs, rhss in g.productions.items() if lhs in g.non_terminals}

    def _remove_non_productive(self, g: CFG) -> None:
        original_nonterminals = set(g.non_terminals)
        productive: Set[Symbol] = set()
        changed = True
        while changed:
            changed = False
            for lhs, rhss in g.productions.items():
                if lhs in productive:
                    continue
                for rhs in rhss:
                    ok = True
                    for sym in rhs:
                        if sym in g.non_terminals and sym not in productive:
                            ok = False
                            break
                    if ok:
                        productive.add(lhs)
                        changed = True
                        break

        g.non_terminals.intersection_update(productive)
        filtered: Productions = {}
        for lhs, rhss in list(g.productions.items()):
            if lhs not in g.non_terminals:
                continue
            keep: Set[RHS] = set()
            for rhs in rhss:
                if all(sym not in original_nonterminals or sym in g.non_terminals for sym in rhs):
                    keep.add(rhs)
            filtered[lhs] = keep
        g.productions = filtered

    def _fresh_nonterminal(self, g: CFG, prefix: str = "X") -> Symbol:
        while True:
            name = f"{prefix}{self._fresh_idx}"
            self._fresh_idx += 1
            if name not in g.non_terminals:
                g.non_terminals.add(name)
                g.productions.setdefault(name, set())
                return name

    def _to_cnf(self, g: CFG) -> None:
        terminal_map: Dict[Symbol, Symbol] = {}
        updated: Productions = {lhs: set() for lhs in g.productions}

        for lhs, rhss in list(g.productions.items()):
            for rhs in rhss:
                if len(rhs) <= 1:
                    updated[lhs].add(rhs)
                    continue

                new_rhs = list(rhs)
                for i, sym in enumerate(new_rhs):
                    if sym in g.terminals:
                        if sym not in terminal_map:
                            t_nt = self._fresh_nonterminal(g, prefix=f"T_{sym}_")
                            terminal_map[sym] = t_nt
                            updated.setdefault(t_nt, set()).add((sym,))
                        new_rhs[i] = terminal_map[sym]
                updated[lhs].add(tuple(new_rhs))

        g.productions = updated

        binarized: Productions = {lhs: set() for lhs in g.productions}
        for lhs, rhss in list(g.productions.items()):
            for rhs in rhss:
                if len(rhs) <= 2:
                    binarized[lhs].add(rhs)
                    continue
                current_lhs = lhs
                parts = list(rhs)
                while len(parts) > 2:
                    first = parts.pop(0)
                    fresh = self._fresh_nonterminal(g, prefix="X")
                    binarized.setdefault(current_lhs, set()).add((first, fresh))
                    current_lhs = fresh
                binarized.setdefault(current_lhs, set()).add(tuple(parts))

        g.productions = {lhs: rhss for lhs, rhss in binarized.items() if lhs in g.non_terminals}

def build_variant_11_cfg() -> CFG:
    non_terminals = {"S", "A", "B", "C", "D"}
    terminals = {"a", "b"}
    productions: Productions = {
        "S": {("b", "A"), ("A", "C")},
        "A": {("b", "S"), ("B", "C"), ("A", "b", "A", "a")},
        "B": {("B", "b", "a", "A"), ("a",), ("b", "S", "a")},
        "C": {tuple()},  # epsilon
        "D": {("A", "B")},
    }
    return CFG(
        non_terminals=non_terminals,
        terminals=terminals,
        productions=productions,
        start_symbol="S",
    )

