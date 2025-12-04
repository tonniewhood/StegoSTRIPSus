
The current winning configurations (FEN string) are as follows

1. Starting: "1k6/8/K1R5/8/8/8/8/2R5 w - - 0 1" -> Move: RC6 to B6 -> Move: RC1 to C8 -> Final: "k1R5/8/KR6/8/8/8/8/8 w HAha - 0 1" (PUSH)
2. Starting: "1k6/8/1KQ5/8/8/8/8/8 w - - 0 1"   -> Move: QC6 to C7 -> Move: QC7 to B7 -> Final: "k7/1Q6/1K6/8/8/8/8/8 w - - 0 1"    (POP)
3. Starting: "6k1/8/5R1K/8/8/8/8/5R2 w - - 0 1" -> Move: RF6 to F8 -> Final: "5Rk1/8/7K/8/8/8/8/5R2 w - - 0 1"                      (ADD)
4. Starting: "7k/8/6K1/5R2/8/8/8/8 w - - 0 1"   -> Move: RF5 to F8 -> Final: "5R1k/8/6K1/8/8/8/8/8 w - - 0 1"                       (SUB)
5. Starting: "8/2R5/8/8/8/1K6/8/k7 w - - 0 1"   -> Move: RC7 to C1 -> Final: "8/8/8/8/8/1K6/8/k1R5 w - - 0 1"                       (JMP)
6. Starting: "7k/8/4Q1K1/8/8/8/8/8 w - - 0 1"   -> Move: QE6 to E8 -> Final: "4Q2k/8/6K1/8/8/8/8/8 w - - 0 1"                       (JZ)
7. Starting: "3Q4/8/k1K5/8/8/8/8/8 w - - 0 1"   -> Move: QD8 to B6 -> Final: "8/8/kQK5/8/8/8/8/8 w - - 0 1"                         (LOAD)
8. Starting: "4Q3/8/5K1k/8/8/8/8/8 w - - 0 1"   -> Move: QE8 to G6 -> Final: "7Q/8/5K1k/8/8/8/8/8 w - - 0 1"                        (HALT)
