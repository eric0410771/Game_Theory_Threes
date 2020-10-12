# Game_Theory_Threes

## Train a new agent to play threes via the following command 

```
python 2048.py --play="name=td_learning init=1800000 train" --total=2000
```
The argument "play" with different "name" like td_learning, greedy, dummy specifies what kind of the agent is.
The argument "init" should be provided if the name is setted to be td_learning or greedy. It means the row of table.
The argument "train" should be provided if you hope to update the agent.
The argument "total" is the number of training episodes.

It saves a "weight.bin" file that stores the table of q-values.

## To reuse the stored table, you can use the following command
```
python 2048.py --play="name=td_learning init-1800000 train load=weight.bin" --total=2000
```

