# Language-Free Acq
## Learning constraint networks over unknown constraint languages

![Action of build, test, and deploy on PyPI](https://github.com/Hareski/language-free-acq/actions/workflows/build_test_deploy.yml/badge.svg)

We propose a method to efficiently solve the Language-Free Acq optimisation problem by
giving an optimal consistent constraint network, if it exists.
We have implemented our method in the Python programming language. Our program take as 
input a training set in the form of a file with one assignment by line completed by the 
classification for this assignment (solution or non-solution). We compute the vocabulary 
and generate the corresponding Partial Max-Sat instance and solve it using the OR-Tools
library.

## Requirements
```
tqdm~=4.66.3
ortools~=9.10.4067
```
Tqdm is a progress bar library, used to display the progress of the algorithm.

## Installation
```
pip install -r requirements.txt
```

## Usage
In this new version of the program, the solver is OR-Tools.
You don't have to specify the solver anymore.


### Use the program in your own code

Install the program with pip:
``pip install languageFreeAcq``

You can now use it in your own code:
```python
from src.languageFreeAcq import Acquisition, CspScopesRelations


lfa = Acquisition()
csp: CspScopesRelations = lfa.learn(
  file_train=_examples_file_path_, max_examples=_maximum_number_examples_, timeout=_timeout_)
problem_variables = list(range(0, lfa.get_variables_numbers()))
problem_domain = lfa.get_domains()
relations_learned = csp.get_relations(0)  # The first learned relation
tuples_learned = csp.get_scope(0)  # The scope where the first learned relation is applied to form
# the constraint network
```

### Edit this program
You can use the script `main.py` with the following commands:
  - `main.py all` to run the program on all the datasets of the paper.
  - `main.py dataset_name` to run the program on a specific dataset.
  - `main.py custom` to run the program on the custom dataset. You can configure this
  by modifying the `experiments/xp_custom.py` file.


## Reproduce the experiments of the paper

The paper associated with this program is:
```
Christian Bessiere, Clément Carbonnel, Areski Himeur:
Learning Constraint Networks over Unknown Constraint Languages. IJCAI 2023
```

Because the program now use a new solver, the results may be slightly different from the ones
in the paper. Moreover, there is some difference between the program in this repository and the one used
in the paper notably the way indexes are used. In the paper, the indexes are 1-based while
in this repository, the indexes are 0-based. This difference is due to the fact that the
solver used in the paper was the Max-Sat solver from the Minisat library which uses 1-based
indexes.

The original code can be found here:
https://gite.lirmm.fr/coconut/language-free-acq

---

To reproduce the experiments of the paper, you can use the script `main.py all` which will
run the program on all the datasets of the paper. You can also run the program on a specific
dataset by using the command `main.py dataset_name`.

The results appear in the console with the following format:
```
FILE_TRAIN: data/_.csv  NB_EXAMPLES: _  FILE_TEST: data/_.csv  KR: (_, _) ACCURACY: _ RELATION: _  NETWORK: _ TIME: _
```
where accuracy is the accuracy of the network on the test set, relation is a boolean indicating
if the network obtained has the same relation as the one used to generate the dataset, network
indicates if the network is strictly the same as the one used to generate the dataset.
