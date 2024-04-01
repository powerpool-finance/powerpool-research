// SPDX-License-Identifier: UNLICENSED 
pragma solidity^0.8.0;

contract OracleMock {

    mapping(address=>uint256) prices;

    constructor(
        address[] memory assets_,
        uint256[] memory prices_
    ) {

        require(assets_.length == prices_.length, "Error");
        for (uint256 i = 0; i < assets_.length; i++) {
            prices[assets_[i]] = prices_[i];
        }

    }

    function getAssetPrice(address asset) public view returns (uint256 price) {
        return prices[asset];
    }

    function getAssetsPrices(address[] calldata assets) public view returns(uint256[] memory prices_) {
        for (uint256 i = 0; i < assets.length; i++) {
            require(prices[assets[i]] != 0, "Error"); 
            prices_[i] = prices[assets[i]];
        }
    }

    function setPrices(address[] calldata assets_, uint256[] calldata prices_) public {
        require(assets_.length == prices_.length, "Error");
        for (uint256 i = 0; i < assets_.length; i++) {
            require(prices_[i] != 0, "Error");
            prices[assets_[i]] = prices_[i];
        }
    }
}