const { ProofGenerator } = require("./proof_generator.js");

const g = new ProofGenerator("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F")
const seed = parseInt(process.argv[2]);
const nonce = parseInt(process.argv[3]);
const privkey = parseInt(process.argv[4]);
const proof = g.solProofAsInChlink(seed, nonce, privkey);
const formattedProof = g.formatProofAsProof(proof);
const provider = "https://sepolia.gateway.tenderly.co";
const contractAddress = "0xEE52fbf97738Ae76d89f260b193f5b00d05D7401";
const abiJsonString = '[{"inputs":[{"components":[{"internalType":"uint256[2]","name":"pk","type":"uint256[2]"},{"internalType":"uint256[2]","name":"gamma","type":"uint256[2]"},{"internalType":"uint256","name":"c","type":"uint256"},{"internalType":"uint256","name":"s","type":"uint256"},{"internalType":"uint256","name":"seed","type":"uint256"},{"internalType":"address","name":"uWitness","type":"address"},{"internalType":"uint256[2]","name":"cGammaWitness","type":"uint256[2]"},{"internalType":"uint256[2]","name":"sHashWitness","type":"uint256[2]"},{"internalType":"uint256","name":"zInv","type":"uint256"}],"internalType":"struct VRF.Proof","name":"proof","type":"tuple"},{"internalType":"uint256","name":"seed","type":"uint256"}],"name":"randomValueFromVRFProof","outputs":[{"internalType":"uint256","name":"output","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[2]","name":"pk","type":"uint256[2]"},{"internalType":"uint256[2]","name":"gamma","type":"uint256[2]"},{"internalType":"uint256","name":"c","type":"uint256"},{"internalType":"uint256","name":"s","type":"uint256"},{"internalType":"uint256","name":"seed","type":"uint256"},{"internalType":"address","name":"uWitness","type":"address"},{"internalType":"uint256[2]","name":"cGammaWitness","type":"uint256[2]"},{"internalType":"uint256[2]","name":"sHashWitness","type":"uint256[2]"},{"internalType":"uint256","name":"zInv","type":"uint256"}],"name":"verifyVRFProof","outputs":[],"stateMutability":"view","type":"function"}]';
console.log(g.encodeProof(formattedProof, provider, abiJsonString, contractAddress));