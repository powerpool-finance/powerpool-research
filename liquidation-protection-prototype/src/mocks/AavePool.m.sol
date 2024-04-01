pragma solidity ^0.8.0;

import "lib/aave-v3-core/contracts/interfaces/IPool.sol";
import "lib/aave-v3-core/contracts/interfaces/IAaveOracle.sol";
import "lib/openzeppelin-contracts/contracts/interfaces/IERC20.sol";

contract PoolMock {
    
    struct UserAccount {
        uint256 collateral;
        uint256 debt;
        bool exists;
    }

    uint256 MULTIPLIER = 1e18;
    address Oracle;

    mapping(address=>UserAccount) public users;

    constructor(address oracle) {
        Oracle = oracle;
    }

    function deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode) public {

        if (users[onBehalfOf].exists == false) {
            users[onBehalfOf].exists = true;
        }

        users[onBehalfOf].collateral += toBaseAsset(asset, amount);
        bool success = IERC20(asset).transferFrom(onBehalfOf, address(this), amount);
        require(success);

    }

    function toBaseAsset(address asset, uint256 amount) internal view returns (uint256) {
        return IAaveOracle(Oracle).getAssetPrice(asset)*amount;
    }

    function getUserAccountData(address user) public view returns (
      uint256 totalCollateralBase,
      uint256 totalDebtBase,
      uint256 availableBorrowsBase,
      uint256 currentLiquidationThreshold,
      uint256 ltv,
      uint256 healthFactor
    ) {

        if (users[user].exists == false) {
            revert("User not found");
        }

        totalCollateralBase = users[user].collateral;
        totalDebtBase = users[user].debt;
        healthFactor = _calculateHealthFactor(totalCollateralBase, totalDebtBase);

        availableBorrowsBase = 0;
        currentLiquidationThreshold = 0;
        ltv = 0;

    }

    function _calculateHealthFactor(uint256 collateral, uint256 debt) internal view returns (uint256 hf) {
           
        if (debt != 0) {
            hf = collateral * MULTIPLIER / debt;
        } else {
            hf = collateral == 0 ? 1 * MULTIPLIER : type(uint256).max;
        }

    }

    function withdraw(
        address asset,
        uint256 amount,
        address to) public returns (uint256) {

        require(users[msg.sender].exists, "Not exists");
        require(users[msg.sender].collateral >= amount, "Collateral not enough");

        users[msg.sender].collateral -= toBaseAsset(asset, amount);
        IERC20(asset).transfer(to, amount);

    }

    function borrow(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        uint16 referralCode,
        address onBehalfOf
    ) public {

        require(users[msg.sender].exists, "Not exists");
        uint256 hf = _calculateHealthFactor(users[onBehalfOf].collateral, users[onBehalfOf].debt);
        require(hf >= 1 * MULTIPLIER, "Position is not ok");
        uint256 borrowableAmount = users[onBehalfOf].collateral * 10 / 11 - users[onBehalfOf].debt;
        require(borrowableAmount > 0, "Negative");
        require(amount <= borrowableAmount, "You have no borrowable");
        
        users[onBehalfOf].debt += toBaseAsset(asset, amount);
        IERC20(asset).transfer(onBehalfOf, toBaseAsset(asset, amount));

    }

    function repay(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        address onBehalfOf
    ) external returns (uint256) {

        require(IERC20(asset).allowance(onBehalfOf, address(this)) >= amount, "Not allowed");
        require(amount <= users[onBehalfOf].debt, "Wanna spend too much manei");
        IERC20(asset).transferFrom(onBehalfOf, address(this), amount);
        users[onBehalfOf].debt -= toBaseAsset(asset, amount);

    }
}