# Research Repository for Powerpool Finance Products

Current research projects:

### Binance Smart Chain (BSCDEFI)

In progress

### YLA *(in progress)*

Yearn Lazy Ape Vault composition optimization.


### LUSD *(completed)*

A research of hypothetical LUSD:staBAL stable pool utilizing Balancer v2 mechanics.

Pool's assets are staked in the corresponding staking protocols to generate yield:

LUSD -> LUSD Stability Pool generates LQTY rewards
staBAL generates BAL rewards

The reward tokens are sold for the main assets and restaked.


### TORN *(in progress)*

This project is devoted to the research of the proposet TORN2 Tokenomics.

TORN 1.0: Relayers charge fee from withdrawals and collect is as personal income
TORN2: The major share of fee charged by Relayers is captured by the protocol and re-distributed among TORN token holders using xTORN mechanism.

Becoming a Relayer: an address stakes certain amount of TORN (not less than Tmin) to be added into the active Relayers list. This stake is used as “prepayment” for community fee charges.
Operational process: Relayers are listed in a special table. Users can select any Relayer from the table or use the custom one (not listed one). User initiates withdrawal, Relayer makes a transaction to an external wallet. User is charged for gas, Community fee, Relayer’s fee:

Total users' expenses = Gas + Community fee + Relayer fee

Community fee is deposited directly to xTORN - special Vault for TORN holders.


### Balancer Window *(completed)*

In this study, the possibility of minimizing losses during pool rebalancing was studied. 
The effectiveness of three strategies was studied for a period of 400 days with a 50-day start step and a 20-day strategy duration. 
An arbitrageur robot was programmatically modeled. 

In the first strategy, the pool composition was changed immediately in one time step. 
In the second strategy, the weights were changed and the pool was rebalanced in equal parts within 20 days. 
In the third strategy, an algorithm was worked out to minimize losses by means of an uneven change in weights depending on the price movement that occurred in the market. 

The comparison of strategies showed the effectiveness of the third strategy - the algorithm for minimizing losses.

### Vaults price calculatoins

On this research we compare growthing TVL and Prices of diffrent Vaults on 180 days period.

### HydraDX random swap model

In this repo there are libs for HydraDX idea and may help you to research the interaction with Pool with Base token and unnormalized weights updating after swap. In file HydraDX-randon-swap there is the example of use.

### Model of price determination of Indexcoop Vaults

In this repo there are the python lib with formules of Indexcoop Vaults





