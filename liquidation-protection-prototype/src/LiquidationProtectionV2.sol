// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.0;

import "lib/aave-v3-core/contracts/interfaces/IPool.sol";
import "lib/aave-v3-core/contracts/interfaces/IAaveOracle.sol";
import "lib/openzeppelin-contracts/contracts/access/Ownable.sol";
import "lib/openzeppelin-contracts/contracts/interfaces/IERC20.sol";


contract LiquidationProtectionV2 is Ownable {

    
    //health factor params
    struct HF_PARAMS {
        uint256 lower;
        uint256 upper;
        uint256 target;
    }

    HF_PARAMS public hfParams;
    uint256 public constant MULTIPLIER = 1e18;

    //Assets
    address[] assets;

    //Aave addresses
    IPool aavePool;
    IAaveOracle aaveOracle;

    //Agent address
    address agentAddress;

    //events
    event AssetEmergencyWithdrawn(address indexed asset);
    event WithdrawAave(address indexed asset, uint256 indexed amount, uint256 indexed newHf);
    event DepositAave(address indexed asset, uint256 indexed amount, uint256 indexed newHf);
    event DrawDebt(address indexed asset, uint256 indexed amount, uint256 indexed newHf);
    event RepayDebt(address indexed asset, uint256 indexed amount, uint256 indexed newHf);
    event NewHealthFactorSet(uint256 indexed oldLhf, uint256 indexed oldThf, uint256 indexed newLhf, uint256 newThf);
    event Rebalance(uint256 indexed oldHf, uint256 indexed newHf, uint256 indexed thf);

    

    // modifier onlyOwnerOrAgent() {
    //     require(msg.sender == agentAddress || tx.origin == owner(), "You are not allowed to interact with this contract");
    //     _;
    // }

    modifier onlyOwnerOrAgent() {
        require(msg.sender == agentAddress || msg.sender == owner(), "You are not allowed to interact with this contract");
        _;
    }


    //constructor
    constructor(
        address collateralAsset_,
        address debtAsset_,
        address aaveOracle_,
        address aavePool_,
        address agentAddress_
    ) Ownable(msg.sender) {
        require(debtAsset_ != address(0), "Can't borrow native token");
        //set asset addresses
        assets.push(collateralAsset_);
        assets.push(debtAsset_);
        //set aave addresses
        aavePool = IPool(aavePool_);
        aaveOracle = IAaveOracle(aaveOracle_);
        //set agent address
        agentAddress = agentAddress_;
    }


    //=======

    // SETTERS

    function setHfParams(uint256 lower, uint256 upper) public onlyOwner {
        require(lower <= upper, "Lower bound should be <= upper bound");
        hfParams = _setHfParams(lower, upper);
    }

    function _setHfParams(uint256 lower, uint256 upper) internal pure returns(HF_PARAMS memory) {
        return HF_PARAMS(lower, upper, lower/2 + upper/2);
    }



    function depositCollateral(uint256 amount) public payable onlyOwnerOrAgent {
        
        address collateral = assets[0];
        if (collateral != address(0)) {
            //Transfer collateral from muzhik to this contract
            require(msg.value == 0, "Do not send ETH when depositing ERC20 token as collateral");
            require(amount != 0, "Empty deposits are not allowed");

            IERC20 collateralToken = IERC20(collateral);
            collateralToken.transferFrom(owner(), address(this), amount);
            collateralToken.approve(address(aavePool), amount);
        } else {
            //Amount should be equal to ETH sent in the tx
            require(msg.value == amount, "Set amount == msg.value");
        }

        //2. Supply tokens to aave
        aavePool.deposit(collateral, amount, address(this), 0);

        //3. Query new HF

        (, , , , , uint256 newHF) = aavePool.getUserAccountData(address(this));

        emit DepositAave(collateral, amount, newHF);

    }

    function withdrawCollateral(uint256 amount) public onlyOwnerOrAgent {
        address collateral = assets[0];

        //1. get current collateral amount deposited and current debt
        (uint256 currentCollateralBaseAsset, uint256 currentDebtBaseAsset, , , ,) = aavePool.getUserAccountData(address(this));
        //4. calculate withdrawable collateral
        uint256 withdrawableCollateralBaseAsset = currentCollateralBaseAsset - currentDebtBaseAsset * hfParams.lower / MULTIPLIER;
        //5. calculate amounts from base assets
        uint256 withdrawableCollateral = _calculateAmountFromBaseAsset(collateral, withdrawableCollateralBaseAsset);
        //6. take min(amount, widthdrawable)
        uint256 maxWithdrawable = withdrawableCollateral > amount ? amount : withdrawableCollateral;
        //7. withdraw
        aavePool.withdraw(collateral, maxWithdrawable, owner());
    }

    function increaseDebt() public onlyOwnerOrAgent {

        //get current position details
        address debtAsset = assets[1];

        (uint256 currentCollateralBaseAsset, uint256 currentDebtBaseAsset, , , ,) = aavePool.getUserAccountData(address(this));

        //calculate borrowable amount
        uint256 availableDebtBaseAsset = currentCollateralBaseAsset * MULTIPLIER / hfParams.target - currentDebtBaseAsset;
        uint256 availableDebt = _calculateAmountFromBaseAsset(debtAsset, availableDebtBaseAsset);
        //borrow
        aavePool.borrow(debtAsset, availableDebt, 1, 0, address(this));
        //transfer debt to the owner
        IERC20 debtAssetToken = IERC20(debtAsset);
        uint256 debtAssetBalance = debtAssetToken.balanceOf(address(this));
        bool success = debtAssetToken.transfer(owner(), debtAssetBalance);

        require(success, "Could not borrow");
    }

    function repayDebt() public onlyOwnerOrAgent {
        address debtAsset = assets[1];
        (uint256 currentCollateralBaseAsset, uint256 currentDebtBaseAsset, , , ,) = aavePool.getUserAccountData(address(this));
        uint256 repayableDebtBaseAsset = currentDebtBaseAsset - currentCollateralBaseAsset * MULTIPLIER / hfParams.target;
        uint256 repayableDebt = _calculateAmountFromBaseAsset(debtAsset, repayableDebtBaseAsset);

        IERC20 debtAssetToken = IERC20(debtAsset);
        bool success = debtAssetToken.transferFrom(owner(), address(this), repayableDebt);

        require(success, "Could not transfer debt from owner");

        aavePool.repay(debtAsset, repayableDebt, 1, address(this));
    }


    // BALANCING HEALTH FACTOR

    function balanceHF() public onlyOwnerOrAgent {
        (, , , , ,uint256 currentHealthFactor) = aavePool.getUserAccountData(address(this));

        if (currentHealthFactor < hfParams.lower) {
            repayDebt();
        } else if (currentHealthFactor > hfParams.upper) {
            increaseDebt();
        }
    }

    function resolver() public view returns (bool, bytes memory) {
        (, , , , ,uint256 currentHealthFactor) = aavePool.getUserAccountData(address(this));
        if (
            currentHealthFactor < hfParams.lower
            ||
            currentHealthFactor > hfParams.upper
        ) {
            return (true, abi.encodePacked(this.balanceHF.selector));
        }

        return (false, abi.encodePacked(this.balanceHF.selector));
    }


    // GETTERS AND QUOTERS

    function calculateAmountFromBaseAsset(address asset_, uint256 amount_) public view returns(uint256) {
        return _calculateAmountFromBaseAsset(asset_, amount_);
    }

    //amount_ in aave base asset
    function _calculateAmountFromBaseAsset(address asset_, uint256 amount_) internal view returns(uint256) {
        uint256 price = aaveOracle.getAssetPrice(asset_);
        return amount_ / price;
    }

    //amounts_ in aave base assets
    function _calculateAmountsFromBaseAsset(address[] calldata assets_, uint256[] calldata amounts_) internal view returns(uint256[] memory) {
        uint256 n = assets_.length;
        uint256[] memory prices = aaveOracle.getAssetsPrices(assets);
        uint256[] memory amounts = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            amounts[i] = amounts_[i] / prices[i];
        }
        return amounts;
    }



    // EMERGENCY EXIT

    function emergencyExit(address[] calldata assetsToWithdraw, bool assertWithdraw) public onlyOwner {
        uint256 n = assetsToWithdraw.length;
        for (uint256 i = 0; i < n; i++) {
            uint256 amount;
            address ass = assetsToWithdraw[i];
            if (ass == address(0)) {
                amount = IERC20(ass).balanceOf(address(this));
                payable(owner()).call{value: address(this).balance};
            } else {
                amount = IERC20(ass).balanceOf(address(this));
                bool success = IERC20(ass).transfer(owner(), amount);
                if (assertWithdraw) {
                    require(success, "Say Goodbye to your tokens!");
                }
            }

            emit AssetEmergencyWithdrawn(ass);
        }
    }



}