# memoir44
IA for Memoir 44 boardgame

# todo

* separate action None between move/attack
* separate nn in two: one for move actions, one for attack action
* replace state with positions by state with map
* add reward for unit gain/loss
* ...

# Remarks/Questions

* pb on maxQ(s',a') with forbiden actions (never used => nerver updated)
* pb on maxQ(s',a') with rewards<0 and model initialized with values around 0...
