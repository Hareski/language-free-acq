# Details
For this experiments, we use four files: 
- [jigsaw_1_desc.csv](jigsaw_1_desc.csv): one line per jigsaw shape
- [jigsaw_1_equiv.csv](1_jigsaw_equiv.csv): one line per redundant inequality with the target network.
These redundancies are proved by the authors by checking with ChocoSolver if it exists a solution to the jigsaw puzzle that do 
not satisfy the redundant inequality.
- [jigsaw_1_test.csv](jigsaw_1_test.csv): testing examples
- [jigsaw_1_train.csv](jigsaw_1_train.csv): training examples set