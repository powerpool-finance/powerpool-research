# Proof generator

## Installation

- [Node 21](https://nodejs.org/en/download)

```bash
npm install
```

The logic is contained in the `proof_generator.js` module and is imported therefrom (e.g., `main.js`). In order to test, run `node main.js %seed %nonce &privKey` and compare the logged value with the value in the last cell of `vrfpy.ipynb`. The pipeline for getting calldata for the proof verification contract is exactly as in `main.js`.