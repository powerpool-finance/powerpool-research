// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "lib/forge-std/src/Test.sol";
import {LiquidationProtectionV2} from "src/LiquidationProtectionV2.sol";
import "src/mocks/AaveOracle.m.sol";
import "src/mocks/AavePool.m.sol";
import "src/mocks/ERC20.m.sol";
import "src/mocks/ERC202.m.sol";
import "lib/forge-std/src/Vm.sol";
import "lib/forge-std/src/console.sol";
import "lib/aave-v3-core/contracts/interfaces/IPool.sol";
import "lib/aave-v3-core/contracts/interfaces/IAaveOracle.sol";


contract LiquidationProtectionV2Test is Test {

    LiquidationProtectionV2 public liquidationProtectionV2;
    OracleMock public Oracle;
    PoolMock public Pool;
    Token1 public TOKEN1;
    Token2 public TOKEN2;
    address public Agent;
    address[] public addresses_;
    uint256[] public amts;
    address public actor = 0x1234123412341234123412341234123412341234;
    address strategy;    

    function setUp() public {

        TOKEN1 = new Token1();
        TOKEN2 = new Token2();

        addresses_.push(address(TOKEN1));
        addresses_.push(address(TOKEN2));
        amts.push(1);
        amts.push(2);

        Oracle = new OracleMock(
            addresses_,
            amts
        );
        Pool = new PoolMock(
            address(Oracle)
        );

        Agent = 0x1488148814881488148814881488148814881488;


        vm.deal(actor, 10e18);
        // vm.prank(actor);

        liquidationProtectionV2 = new LiquidationProtectionV2(
            address(TOKEN1),
            address(TOKEN2),
            address(Oracle),
            address(Pool),
            Agent
        );

        strategy = address(liquidationProtectionV2);

        //---
        vm.deal(strategy, 10e18);

        TOKEN1.mint(actor, 300e18);
        TOKEN2.mint(actor, 300e18);

        TOKEN1.mint(strategy, 300e18);
        TOKEN2.mint(strategy, 300e18);

        TOKEN1.mint(address(Pool), 10e18);
        TOKEN2.mint(address(Pool), 10e18);

        liquidationProtectionV2.transferOwnership(actor);

        vm.startPrank(strategy);
        TOKEN1.approve(address(Pool), type(uint256).max);
        TOKEN2.approve(address(Pool), type(uint256).max);
        vm.stopPrank();

        vm.startPrank(actor);
        TOKEN1.approve(strategy, type(uint256).max);
        TOKEN2.approve(strategy, type(uint256).max);
        vm.stopPrank();

    }

    function test_Deposit_Strategy() public {

        assertEq(liquidationProtectionV2.owner(), actor);

        vm.startPrank(actor);
        TOKEN1.approve(strategy, type(uint256).max);
        liquidationProtectionV2.depositCollateral(
            5e18
        );

        (uint256 collateral, uint256 debt, bool exists) = Pool.users(strategy);

        assertEq(exists, true);
        assertEq(collateral, 5e18);

        vm.stopPrank();
    }

    function test_Withdraw_Strategy() public {
        test_Deposit_Strategy();

        vm.startPrank(actor);
        liquidationProtectionV2.withdrawCollateral(
            5e18
        );

        (uint256 collateral, uint256 debt, bool exists) = Pool.users(strategy);
        
        assertEq(exists, true);
        assertEq(collateral, 0);
        assertEq(TOKEN1.balanceOf(actor), 300e18);

        vm.stopPrank();

    }

    function test_Set_HF_Params() public {

        vm.prank(actor);
        liquidationProtectionV2.setHfParams(11e17, 21e17);

        (uint256 lower, uint256 upper, uint256 target) = liquidationProtectionV2.hfParams();
        assertEq(lower, 11e17);
        assertEq(upper, 21e17);
        assertEq(target, 16e17);
    }

    function test_Increase_Debt() public {

        test_Deposit_Strategy();
        test_Set_HF_Params();
        vm.startPrank(actor);
        assertEq(liquidationProtectionV2.owner(), actor);


        (uint256 collateral, uint256 debt, bool exists) = Pool.users(strategy);
        uint256 availableDebtBaseAsset = collateral * 1e18 / 16e17 - debt;
        assertEq(availableDebtBaseAsset, 3125e15);
        uint256 availableDebt = liquidationProtectionV2.calculateAmountFromBaseAsset(address(TOKEN2), availableDebtBaseAsset);
        assertEq(availableDebt, 15625e14);

        liquidationProtectionV2.increaseDebt();

        (collateral, debt, exists) = Pool.users(strategy);
        
        assertEq(exists, true);
        assertEq(debt, 15625e14*2);

        vm.stopPrank();

    }

    function test_Repay_Debt() public {
        test_Increase_Debt();
        vm.startPrank(actor);

        liquidationProtectionV2.setHfParams(15e17, 25e17);
        (uint256 lower, uint256 upper, uint256 target) = liquidationProtectionV2.hfParams();
        assertEq(target, 2e18);

        (uint256 currentCollateralBaseAsset, uint256 currentDebtBaseAsset, , , ,) = Pool.getUserAccountData(strategy);
        uint256 repayableDebtBaseAsset = currentDebtBaseAsset - currentCollateralBaseAsset * liquidationProtectionV2.MULTIPLIER() / target;
        uint256 repayableDebt = liquidationProtectionV2.calculateAmountFromBaseAsset(address(TOKEN2), repayableDebtBaseAsset);

        assertEq(repayableDebtBaseAsset, 625e15);
        assertEq(repayableDebt, 625e15/2);

        assertEq(currentCollateralBaseAsset, 5e18);
        assertGt(currentDebtBaseAsset, currentCollateralBaseAsset * liquidationProtectionV2.MULTIPLIER() / target);
        assertEq(currentCollateralBaseAsset * liquidationProtectionV2.MULTIPLIER() / target, currentCollateralBaseAsset/2);
        
        liquidationProtectionV2.repayDebt();
        (uint256 collateral, uint256 debt, bool exists) = Pool.users(strategy);
        (
            uint256 totalCollateralBase,
            uint256 totalDebtBase,
            uint256 availableBorrowsBase,
            uint256 currentLiquidationThreshold,
            uint256 ltv,
            uint256 healthFactor
        ) = Pool.getUserAccountData(strategy);

        assertEq(healthFactor, target);
        assertEq(collateral, totalCollateralBase);
        // assertEq(debt, totalDebtBase);
        //assertEq(debt, collateral);
    }

    function test_Balance_HF() public {
        test_Deposit_Strategy();
        test_Set_HF_Params();
        vm.startPrank(actor);
        assertEq(liquidationProtectionV2.owner(), actor);

        (bool flag, bytes memory cdata) = liquidationProtectionV2.resolver();
        assertEq(flag, true);
        assertEq(cdata, abi.encodePacked(liquidationProtectionV2.balanceHF.selector));

        liquidationProtectionV2.balanceHF();

        (uint256 collateral, uint256 debt, bool exists) = Pool.users(strategy);
        
        assertEq(exists, true);
        assertEq(debt, 15625e14*2);

        liquidationProtectionV2.setHfParams(18e17, 22e17);


        (flag, cdata) = liquidationProtectionV2.resolver();
        assertEq(flag, true);
        assertEq(cdata, abi.encodePacked(liquidationProtectionV2.balanceHF.selector));

        liquidationProtectionV2.balanceHF();

        (collateral, debt, exists) = Pool.users(strategy);
        (
            uint256 totalCollateralBase,
            uint256 totalDebtBase,
            uint256 availableBorrowsBase,
            uint256 currentLiquidationThreshold,
            uint256 ltv,
            uint256 healthFactor
        ) = Pool.getUserAccountData(strategy);


        (uint256 lower, uint256 upper, uint256 target) = liquidationProtectionV2.hfParams();
        assertEq(healthFactor, target);
        assertEq(collateral, totalCollateralBase);

        vm.stopPrank();
    }

    function test_Resolver() public {

        



    }




}