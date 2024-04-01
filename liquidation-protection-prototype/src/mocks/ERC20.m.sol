// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity^0.8.0;

import "lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";

contract Token1 is ERC20 {
    constructor() ERC20("token1", "TKN1") {}

    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }
}