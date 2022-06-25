from inspect import CO_ITERABLE_COROUTINE
import numpy as np
from collections import Counter

class Game:
    def __init__(self, board):
        self.board = np.array(board)
        self.note = [[[] for _ in range(9)] for _ in range(9)]

    # ref: https://stackoverflow.com/questions/37952851/formating-sudoku-grids-python-3
    def print_board(self):
        print("+" + "---+"*9)
        for i, row in enumerate(self.board):
            print(("|" + " {}   {}   {} |"*3).format(*[x if x != 0 else " " for x in row]))
            if i % 3 == 2:
                print("+" + "---+"*9)
            else:
                print("+" + "   +"*9)


    def _get_row(self, idx):
        return self.board[idx]

    def _get_col(self, idx):
        return self.board.T[idx]
    
    def _get_block(self, idx):
        row_offset = 3 * (idx // 3)
        col_offset = 3 * (idx % 3)
        block = self.board[row_offset:row_offset+3, col_offset:col_offset+3]
        return block.flatten()

    def _get_block_idx(self, row_idx, col_idx):
        row_offset = row_idx // 3
        col_offset = col_idx // 3
        block_idx = row_offset * 3 + col_offset
        return block_idx
    
    def _block_element_idx_to_cell_position(self, block_idx, elt_idx):
        row_offset = 3 * (block_idx // 3)
        col_offset = 3 * (block_idx % 3)
        row = row_offset + (elt_idx // 3)
        col = col_offset + (elt_idx % 3)
        return {'row': row, 'col': col}
        
    
    def _is_cell_empty(self, cell_row, cell_col):
        return self.board[cell_row][cell_col] == 0

    # A zone is one row / column / block
    def _check_zone_valid(self, zone: np.array):
        assert len(zone) == 9
        uniq_elt = Counter(zone)

        # Ignore empty cells
        del uniq_elt[0]

        valid_keys = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        counter_keys = list(uniq_elt.keys())
        counter_vals = list(uniq_elt.values())

        is_valid = set(counter_keys).issubset(set(valid_keys)) and all(elt == 1 for elt in counter_vals)
            
        return is_valid


    def check_board_valid(self):
        is_valid = True        
        for idx in range(9):
            block = self._get_block(idx)
            is_valid = self._check_zone_valid(block) and is_valid
            row = self._get_row(idx)
            is_valid = self._check_zone_valid(row) and is_valid
            col = self._get_col(idx)
            is_valid = self._check_zone_valid(col) and is_valid

        return is_valid
    
    def _num_is_safe_in_cell(self, cell_row, cell_col, num):
        row = self._get_row(cell_row)
        col = self._get_col(cell_col)
        block = self._get_block(self._get_block_idx(cell_row, cell_col))
        
        is_safe = (num not in row ) and (num not in col) and (num not in block)
        return is_safe
        
    def _all_safe_num_in_cell(self, cell_row, cell_col):
        candidate_num = range(1,10)
        res = []
        for num in candidate_num:
            if self._num_is_safe_in_cell(cell_row, cell_col, num):
                res.append(num)
        return res
    
    def generate_note(self):
        for row_idx in range(9):
            for col_idx in range(9):
                if self._is_cell_empty(row_idx, col_idx):
                    safe_num = self._all_safe_num_in_cell(row_idx, col_idx)
                    self.note[row_idx][col_idx] = safe_num
        print(self.note)
    
    # https://sudoku.com/sudoku-rules/last-free-cell/
    def _last_free_cell_of_zone(self, zone):
        assert self._check_zone_valid(zone)
        uniq_elt = Counter(zone)

        free_cell_idx = -1
        free_cell_num = -1
        if uniq_elt[0] == 1:

            # find the index of last free cell
            for idx in range(9):
                if zone[idx] == 0:
                    free_cell_idx = idx
            
            # find the answer of last free cell
            candidate_num = range(1,10)
            for num in candidate_num:
                if uniq_elt[num] == 0:
                    free_cell_num = num
        
        return {'idx':free_cell_idx, 'num':free_cell_num}
        
    def find_last_free_cell(self):
        res = {'found': False, 'zone_type': None, 'row': None, 'col': None, 'ans': None}

        for idx in range(9):
            # search each row
            row = self._get_row(idx)
            last_free_cell_of_row =  self._last_free_cell_of_zone(row)
            # if found
            if last_free_cell_of_row['idx'] != -1:
                res['found'] = True
                res['zone_type'] = 'row'
                res['row'] = idx
                res['col'] = last_free_cell_of_row['idx']
                res['ans'] = last_free_cell_of_row['num']
                break
            
            # search each col
            col = self._get_col(idx)
            last_free_cell_of_col =  self._last_free_cell_of_zone(col)
            # if found
            if last_free_cell_of_col['idx'] != -1:
                res['found'] = True
                res['zone_type'] = 'col'
                res['row'] = last_free_cell_of_col['idx']
                res['col'] = idx
                res['ans'] = last_free_cell_of_col['num']
                break

            # search each block
            block = self._get_block(idx)
            last_free_cell_of_block =  self._last_free_cell_of_zone(block)
            # if found
            if last_free_cell_of_block['idx'] != -1:
                cell_pos = self._block_element_idx_to_cell_position(idx, last_free_cell_of_block['idx'])
                res['found'] = True
                res['zone_type'] = 'block'
                res['row'] = cell_pos['row']
                res['col'] = cell_pos['col']
                res['ans'] = last_free_cell_of_block['num']
                break

        return res
                
            
            

        
        
        
board = [
    [7, 5, 0, 0, 0, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 5, 0, 0, 8],
    [0, 0, 1, 7, 8, 0, 3, 0, 0],
    [1, 0, 0, 4, 6, 0, 0, 0, 9],
    [0, 0, 3, 0, 0, 0, 0, 2, 0],
    [0, 0, 0, 0, 0, 7, 0, 0, 0],
    [4, 0, 0, 8, 1, 0, 0, 0, 6],
    [0, 0, 0, 0, 5, 0, 0, 0, 0],
    [0, 6, 0, 0, 0, 0, 9, 0, 0]   
]

board2 = [
    [3, 0, 7, 0, 0, 4, 1, 0, 0],
    [0, 0, 0, 0, 0, 6, 7, 5, 4],
    [0, 9, 4, 1, 0, 0, 0, 0, 3],
    [0, 3, 0, 0, 0, 2, 0, 0, 0],
    [0, 2, 8, 0, 0, 0, 0, 0, 1],
    [0, 0, 6, 8, 3, 1, 0, 0, 0],
    [2, 0, 0, 0, 0, 0, 3, 0, 7],
    [5, 0, 1, 0, 6, 0, 4, 0, 0],
    [0, 7, 0, 0, 0, 0, 0, 0, 6]   
]


test_board = [
    [1, 2, 3, 0, 0, 6, 7, 8, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 0, 0, 0, 8, 0, 3, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 2, 0],
    [0, 0, 0, 0, 0, 7, 0, 0, 0],
    [7, 0, 0, 8, 1, 4, 0, 0, 6],
    [8, 0, 0, 0, 5, 3, 0, 0, 0],
    [0, 0, 0, 7, 6, 2, 9, 0, 0]   
]

sudoku = Game(board2)
sudoku.print_board()
sudoku.generate_note()