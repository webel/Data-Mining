# Homework 2: Discovery of Frequent Itemsets and Association Rules

## Dataset

### Simple dataset

File `simple_test_abc.dat`. Used the dataset from slide 43 in lecture 3:

```sh
A C D
B C E
A B C E
B E
```

## Notes from the paper

[Fast Algorithms for Mining Association Rules](https://www.cse.msu.edu/~cse960/Papers/MiningAssoc-AgrawalAS-VLDB94.pdf)

### Differences to eariler approaches

The main difference apriori has to earlier approaches is how candidate itemsets are generated. I.e. by only using the itemsets found to be large inte the previous step, without considering the transactions in the database.

Basic intuition:

$$\because Y \text{ is large} \land X \subset Y \therefore X \text{ is large}.$$ 

Plain english: because $Y$ is large and $X$ is a subset of $Y$, therefor $X$ is large.

### Words

**Basket data** Consists of transactions

**Transactions** Each line in our file are transactions, i.e. a record of items bought together.

**Item** An element in a record, i.e. what transactions consist of.

### Formal statement of problem

$$ I = \{ i_1, i_2, i_3, ... i_m \} \text{ a set of items.} $$
Let $D$ be a set of transactions, where each transaction $T$ is a set of items such that $T \subseteq I$. Associated with each transaction is a unique identifier, called its TID (transaction ID).

A transaction $T$ contains $X$ ($X \subset I$) if $X \subseteq T$.

An **association rule** is a rule in the form $X \to Y$, where $X \subset I$, $Y \subset I$ and $X \land Y = \emptyset$. In other words; both $X$ and $Y$ are subsets of $I$ and have no items in common.

A rule holds with **confidence** $c$ if $c%$ of transactions in $D$ that contain $X$ also contain $Y$.

A rule has **support** $s$ in the transaction set $D$ if $s%$ of transactions in $D$ contain $X \lor Y$.

#### Subproblems

##### Find all itemsets that have transaction support above minimum support

The support for an itemset is the numer of transactions that contain the itemset. Itemsets with minimum support are called *large* itemsets. Others are called *small* itemsets.

First pass: count individual items and determine which are large, $C_1$ and $L_1$.

Subsequent steps: Use the previous large itemset, $L_{k-1}$, to determine $C_k$. Count the actual support for these candidate itemsets during the pass over the data (*TODO: I don't understand this sentence...maybe I do, I think it's the increment of the itemset for each found candidate*). Determine $L_k$ and continue until no more large datasets are found.

##### Mining association rules

Use the *large* itemsets to generate the desired rules.

Generate all assiociation rules that have support and confidence greater than the user-specified minimum support ($minsup$) and minimum confidence ($minconf$).
