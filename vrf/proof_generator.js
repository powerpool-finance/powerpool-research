const EC = require('elliptic').ec;
const BN = require('bn.js');
const { keccak256 } = require('js-sha3');
const { Web3 } = require('web3');

class ProofGenerator {
	constructor(fieldSize) {
		this.elipticCurve = new EC('secp256k1');
		this.order = new BN(this.elipticCurve.curve.n.toString());
		this.fieldSize = new BN(fieldSize, 16);
	}

	numberToUint256(number) {
		let hexNumber = number.toString(16);
		return '0x' + '0'.repeat(64 - hexNumber.length) + hexNumber;
	}

	hexStringToByteArray(hexString) {
		let result = [];
		for (let i = 0; i < hexString.length; i += 2) {
			result.push(parseInt(hexString.substr(i, 2), 16));
		}
		return result;
	}

	modPow(base, exponent, modulus) {
		let result = new BN(1);
		base = base.mod(modulus);
	
		while (exponent.gt(new BN(0))) {
			if (!exponent.isEven()) {
				result = result.mul(base).mod(modulus);
			}
			exponent = exponent.shrn(1);
			base = base.mul(base).mod(modulus);
		}
		return result;
	}

	toByteArray(integer) {
		let hexString = integer.toString(16);

		if (hexString.length % 2 !== 0) {
			hexString = '0' + hexString;
		}
		const numBytes = hexString.length / 2;
		const byteArray = new Uint8Array(numBytes);
		for (let i = 0; i < numBytes; i++) {
			byteArray[i] = parseInt(hexString.substr(i * 2, 2), 16);
		}
		return byteArray;
	}

	hashToCurve(pk, seed) {
		const domsep = this.numberToUint256(new BN(1));
		let concatenatedHex = (
			domsep
			+ this.numberToUint256(pk.getX()).slice(2)
			+ this.numberToUint256(pk.getY()).slice(2)
			+ this.numberToUint256(seed).slice(2)
		);

		let hash = keccak256(Buffer.from(concatenatedHex.slice(2), 'hex'));
		let h = new BN(hash, 16);

		while (true) {
			try {
				let y2 = h.mul(h.mul(h).mod(this.fieldSize)).mod(this.fieldSize).add(new BN(7)).mod(this.fieldSize);
				let y = this.modPow(y2, this.fieldSize.add(new BN(1)).div(new BN(4)), this.fieldSize);
				let pt = this.elipticCurve.curve.point(h.toString(16), y.toString(16));
				if (!this.elipticCurve.curve.validate(pt)) {
					throw new Error("Invalid point");
				}
				return pt.getY().isEven() ? pt : pt.neg();
			} catch (e) {
				hash = keccak256(Buffer.from(this.numberToUint256(h).slice(2), 'hex'));
				h = new BN(hash, 16);
			}
		}
	}

	ptToAddress(pt) {
		const ptXBytes = pt.x.toString(16).padStart(64, '0');
		const ptYBytes = pt.y.toString(16).padStart(64, '0');
		const hash = keccak256(Buffer.from(ptXBytes + ptYBytes, 'hex'));
		return '0x' + hash.substring(hash.length - 40);
	}

	marshalPoint(pt) {
		const ptXBytes = pt.x.toString(16).padStart(64, '0');
		const ptYBytes = pt.y.toString(16).padStart(64, '0');
		return ptXBytes + ptYBytes;
	}

	ptToUint2562(pt) {
		return [pt.getX(), pt.getY()];
	}

	hashMuchToScalar(h, pubk, gamma, uw, v) {
		const chlinkDomSep = 2;
		return Web3.utils.soliditySha3(
			{ t: "uint256", v: chlinkDomSep },
			{ t: "uint256[2]", v: this.ptToUint2562(h) },
			{ t: "uint256[2]", v: this.ptToUint2562(pubk) },
			{ t: "uint256[2]", v: this.ptToUint2562(gamma) },
			{ t: "uint256[2]", v: this.ptToUint2562(v) },
			{ t: "address", v: Web3.utils.toChecksumAddress(uw) }
		);
	}

	ptToStr(pt) {
		return [pt.getX().toString(16), pt.getY().toString(16)];
	}

	genProofWithNonce(seed, nonce, privkey) {
		const pkhHex = keccak256(this.toByteArray(privkey), 16);
		const pkh = new BN(pkhHex, 16);
	
		const generator = this.elipticCurve.g;
		const pubkey = generator.mul(pkh);
	
		const h = this.hashToCurve(pubkey, seed);
	
		const gamma = h.mul(pkh);
		const u = generator.mul(new BN(nonce));
		
		const witness = this.ptToAddress(u);
		
		const v = h.mul(new BN(nonce));
	
		const cHex = this.hashMuchToScalar(h, pubkey, gamma, witness, v);
		const c = new BN(cHex.slice(2), 16);
	
		const s = new BN(nonce).sub(c.mul(pkh)).umod(this.elipticCurve.curve.n);

		const output = this.numberToUint256(3) + this.marshalPoint(gamma);

		const outputHashHex = keccak256(Buffer.from(output.slice(2), 'hex'));
		const outputHash = '0x' + outputHashHex;
	
		return {
			pubkey: pubkey,
			gamma: gamma,
			c: c.toString(16),
			s: s.toString(16),
			seed: seed,
			output: outputHash
		};
	}
	
	PROJECTIVE_MULTIPLICATION(x1, z1, x2, z2) {
		return [x1.mul(x2), z1.mul(z2)];
	}
	
	PROJECTIVE_SUBTRACTION(x1, z1, x2, z2) {
		let p1 = z2.mul(x1);
		let p2 = x2.mul(z1).neg();
		let sum = p1.add(p2).mod(this.fieldSize);

		if (sum.isNeg()) {
			sum = sum.add(this.fieldSize);
		}

		let product = z1.mul(z2).mod(this.fieldSize);

		if (product.isNeg()) {
			product = product.add(this.fieldSize);
		}

		return [sum, product];
	}
	
	PROJECTIVE_ECCADDITION(pt1, pt2) {
		let x1 = new BN(pt1.x, 10), y1 = new BN(pt1.y, 10);
		let x2 = new BN(pt2.x, 10), y2 = new BN(pt2.y, 10);
		let z1 = new BN(1), z2 = new BN(1);
		let [lx, lz] = [y2.sub(y1), x2.sub(x1)];
		let [sx, dx] = this.PROJECTIVE_MULTIPLICATION(lx, lz, lx, lz);
		[sx, dx] = this.PROJECTIVE_SUBTRACTION(sx, dx, x1, z1);
		[sx, dx] = this.PROJECTIVE_SUBTRACTION(sx, dx, x2, z2);
		let [sy, dy] = this.PROJECTIVE_SUBTRACTION(x1, z1, sx, dx);
		[sy, dy] = this.PROJECTIVE_MULTIPLICATION(sy, dy, lx, lz);
		[sy, dy] = this.PROJECTIVE_SUBTRACTION(sy, dy, y1, z1);
		let sz;
		if (!dx.eq(dy)) {
			sx = sx.mul(dy);
			sy = sy.mul(dx);
			sz = dx.mul(dy);
		} else {
			sz = dx;
		}
		return [sx.mod(this.fieldSize), sy.mod(this.fieldSize), sz.mod(this.fieldSize)];
	}
	
	modinvPRIME(a, ord) {
		return a.toRed(BN.red(ord)).redInvm().fromRed();
	}

	solProofAsInChlink(seed, nonce, privkey) {
		const proof = this.genProofWithNonce(seed, nonce, privkey);

		const cPoint = this.elipticCurve.keyFromPublic(proof.pubkey).getPublic().mul(new BN(proof.c, 16));
		const sGPoint = this.elipticCurve.g.mul(new BN(proof.s, 16));
		const u = cPoint.add(sGPoint);
	
		const hash = this.hashToCurve(proof.pubkey, proof.seed);
	
		const cgw = this.elipticCurve.keyFromPublic(proof.gamma).getPublic().mul(new BN(proof.c, 16));
		const shw = this.elipticCurve.keyFromPublic(hash).getPublic().mul(new BN(proof.s, 16));
		const [_, __, PROJDENOM] = this.PROJECTIVE_ECCADDITION(cgw, shw);

		const zinv = this.modinvPRIME(new BN(PROJDENOM), this.fieldSize);
	
		return {
			proof: proof,
			uw: this.ptToAddress(u),
			cgw: cgw,
			shw: shw,
			zinv: zinv.toString(16)
		};
	}

	ptToArr(pt) {
		return [this.numberToUint256(pt.getX()), this.numberToUint256(pt.getY())]
	}

	ptToArrNat(pt) {
		return ["0x" + pt.getX().toString(16), "0x" + pt.getY().toString(16)]
	}

	formatProofAsProof(proof) {
		return [
			this.ptToArrNat(proof["proof"]["pubkey"]),
			this.ptToArrNat(proof["proof"]["gamma"]),
			"0x" + proof["proof"]["c"],
			"0x" + proof["proof"]["s"],
        	proof["proof"]["seed"],
			Web3.utils.toChecksumAddress(proof["uw"]),
			this.ptToArrNat(proof["cgw"]),
			this.ptToArrNat(proof["shw"]),
			"0x" + proof["zinv"],
		]
	}

	encodeProof(formattedProof, provider, abiJsonString, contractAddress) {
		const web3 = new Web3(provider);

		const abi = JSON.parse(abiJsonString);

		const contract = new web3.eth.Contract(abi, contractAddress);

		return contract.methods.verifyVRFProof(...formattedProof).encodeABI();
	}
}

module.exports = { ProofGenerator };