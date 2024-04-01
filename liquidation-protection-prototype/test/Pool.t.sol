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


contract PoolTest is Test {

    LiquidationProtectionV2 public liquidationProtectionV2;
    OracleMock public Oracle;
    PoolMock public Pool;
    Token1 public TOKEN1;
    Token2 public TOKEN2;
    address public Agent;
    address[] public addresses_;
    uint256[] public amts;
    address public strategy = 0x0010001000100010001000100010001000100010;
    address public actor = 0x1234123412341234123412341234123412341234;


    function setUp() public {
        TOKEN1 = new Token1();
        TOKEN2 = new Token2();
        addresses_.push(address(TOKEN1));
        addresses_.push(address(TOKEN2));
        amts.push(1);
        amts.push(2);
        Oracle = new OracleMock(addresses_, amts);
        Pool = new PoolMock(address(Oracle));
        Agent = 0x1488148814881488148814881488148814881488;
        liquidationProtectionV2 = new LiquidationProtectionV2(
            address(TOKEN1),
            address(TOKEN2), 
            address(Oracle),
            address(Pool),
            Agent
        );
        TOKEN1.mint(actor, 1e20);
        TOKEN1.mint(strategy, 1e20);
        TOKEN1.mint(address(Pool), 1e20);
        TOKEN2.mint(actor, 1e20);
        TOKEN2.mint(strategy, 1e20);
        TOKEN2.mint(address(Pool), 1e20);
        vm.deal(actor, 1e20);
        vm.deal(strategy, 1e20);
    }

    function test_Deposit() public {
        vm.prank(actor);
        //let TOKEN1 be collateral for TOKEN2
        TOKEN1.approve(address(Pool), type(uint256).max);
        vm.prank(strategy);
        Pool.deposit(address(TOKEN1), 5e18, actor, 0);
        (uint256 collarbone,,,,,) = Pool.getUserAccountData(actor);
        assertEq(collarbone, Oracle.getAssetPrice(address(TOKEN1))*5e18);
        assertEq(TOKEN1.balanceOf(actor), 1e20-5e18);
        (,,bool exists) = Pool.users(actor);
        assertEq(exists, true);
    }


    function test_Withdraw() public {
        vm.startPrank(actor);
        //let TOKEN1 be collateral for TOKEN2
        TOKEN1.approve(address(Pool), type(uint256).max);
        Pool.deposit(address(TOKEN1), 5e18, actor, 0);
        (,,bool exists) = Pool.users(actor);
        assertEq(exists, true);
        assertEq(TOKEN1.balanceOf(actor), 1e20-5e18);
        Pool.withdraw(address(TOKEN1), 5e18, actor);
        assertEq(TOKEN1.balanceOf(actor), 1e20);
        vm.stopPrank();
    }

    function deposit(
        address strategy_,
        uint256 amount_
    ) public {
        TOKEN1.approve(address(Pool), type(uint256).max);
        Pool.deposit(address(TOKEN1), amount_, strategy_, 0);
        (uint256 collateral,, bool exists) = Pool.users(strategy_);
        assertEq(exists, true);
        assertEq(collateral, amount_);
    }

    function test_Borrow() public {
        vm.startPrank(actor);
        deposit(actor, 5e18);
        Pool.borrow(
            address(TOKEN1),
            1e18,
            1,
            0,
            actor
        );

        (uint256 collateral, uint256 debt, bool exists) = Pool.users(actor);

        assertEq(exists, true);
        assertEq(collateral, 5e18);
        assertEq(debt, 1e18);
        vm.stopPrank();
    }

    function test_Repay() public {

        test_Borrow();
        Pool.repay(
            address(TOKEN1),
            1e18,
            1,
            actor);

        (uint256 collateral, uint256 debt, bool exists) = Pool.users(actor);
        assertEq(exists, true);
        assertEq(collateral, 5e18);
        assertEq(debt, 0);
    }


    // 1. Deposit tests
    // 2. Withdraw tests
    // 3. Emergency exit tests
    // 4. Increase debt tests
    // 5. Decrease debt tests
    // 6. Rebalance tests
    // 7. Compute amount tests
}
