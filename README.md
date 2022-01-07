# Research Repository for Powerpool Finance Products

This repository is devoted to variuos research objectives.

The list of past and ongoing research is given below.

## Past Research:

### LUSD *(completed)*

A research of hypothetical LUSD:staBAL stable pool utilizing Balancer v2 mechanics.

Pool's assets are staked in the corresponding staking protocols to generate yield:

LUSD -> LUSD Stability Pool generates LQTY rewards
staBAL generates BAL rewards

The reward tokens are sold for the main assets and restaked.

## Current Research:

### YLA *(in progress)*

Yearn Lazy Ape Vault composition optimization.

### TORN *(in progress)*

This project is devoted to the research of the proposet TORN2 Tokenomics.

TORN 1.0: Relayers charge fee from withdrawals and collect is as personal income
TORN2: The major share of fee charged by Relayers is captured by the protocol and re-distributed among TORN token holders using xTORN mechanism.

Becoming a Relayer: an address stakes certain amount of TORN (not less than Tmin) to be added into the active Relayers list. This stake is used as “prepayment” for community fee charges.
Operational process: Relayers are listed in a special table. Users can select any Relayer from the table or use the custom one (not listed one). User initiates withdrawal, Relayer makes a transaction to an external wallet. User is charged for gas, Community fee, Relayer’s fee:

Total users' expenses = Gas + Community fee + Relayer fee

Community fee is deposited directly to xTORN - special Vault for TORN holders.


