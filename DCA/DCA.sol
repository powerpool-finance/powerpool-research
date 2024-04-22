// SPDX-License-Identifier: UNLINCENSE
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/access/Ownable.sol";
import "v3-periphery/interfaces/ISwapRouter.sol";
import "v3-periphery/interfaces/IQuoter.sol";
import "@openzeppelin/contracts/interfaces/IERC20.sol";

contract DCA is Ownable(msg.sender) {

    struct StructPARAMS{
        uint256 delay;
        uint256 interval;
        uint256 threshold;
        bool highLow;
        uint256 terminus;
        uint256 amount;
        uint256 tolerance;
    }
    
    StructPARAMS public PARAMS;
    bytes public path;
    IQuoter public QUOTER = IQuoter(0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6);
    ISwapRouter public UniSwapper = ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    uint256 public lastExec;
    uint256 public canExecAt;
    uint256 public constant MULTIPLIER = 1e6;

    event Swapped(uint256 amount);



    constructor (
        uint256 delay,
        uint256 interval,
        uint256 threshold,
        bool highLow,
        uint256 terminus,
        uint256 amount,
        bytes memory _path,
        uint256 tolerance

    ) {
        path = _path;
        PARAMS = StructPARAMS(delay, interval, threshold, highLow, terminus, amount, tolerance);
        canExecAt = block.timestamp+delay;
    }

    function setParams(uint256 delay, 
                       uint256 interval, 
                       uint256 threshold, 
                       uint256 amount,
                       bool highLow, 
                       uint256 terminus,
                       uint256 tolerance
                       ) public onlyOwner {
                        PARAMS = StructPARAMS(delay, interval, threshold, highLow, terminus, amount, tolerance);
    }

    function setPath (bytes memory _path) public onlyOwner {
        path = _path;
    }

    function getTokenIn() public returns (address){
        return address(bytes20(path));
    }

    function quote() public returns (uint256 out){
        if (PARAMS.highLow){
            return QUOTER.quoteExactInput(path, PARAMS.amount);
        }
        else {
            return QUOTER.quoteExactOutput(path, PARAMS.amount);
        }
    }

    function temporalResolver() public view returns (bool){
        return (block.timestamp >= canExecAt);
    }

    function priceResolver() public returns (bool){
        return (PARAMS.highLow && quote()*MULTIPLIER/PARAMS.amount > PARAMS.threshold)
    ||(!PARAMS.highLow && quote()*MULTIPLIER/PARAMS.amount < PARAMS.threshold);
    }

    function isRichEnough() public returns (bool){
        //TODO: return a check of the balance of the given token being above a certian threshold
        IERC20 tokenIn = IERC20(getTokenIn());
        return (PARAMS.highLow && tokenIn.balanceOf(address(this)) >= PARAMS.amount)
    ||(!PARAMS.highLow && quote()*MULTIPLIER/PARAMS.amount < tokenIn.balanceOf(address(this)));
    }

    function resolver() public returns (bool, bytes4){
        if (temporalResolver() && priceResolver()){
            return (true, this.performSwap.selector);
        }
        return (false, this.performSwap.selector);
    }

    function performSwap() public {
        if (!temporalResolver() || !priceResolver()){
            revert("Can't swap");
        }
        if (PARAMS.highLow){
                uint256 amount = UniSwapper.exactInput(ISwapRouter.ExactInputParams(
                path,
                owner(),
                block.timestamp + 1000,
                PARAMS.amount,
                PARAMS.amount*PARAMS.threshold / MULTIPLIER * (MULTIPLIER - PARAMS.tolerance) / MULTIPLIER
            ));
            emit Swapped(amount);
        }
    else {
        uint256 amount = UniSwapper.exactOutput(ISwapRouter.ExactOutputParams(
            path,
            owner(),
            block.timestamp + 1000,
            PARAMS.amount,
            PARAMS.amount*PARAMS.threshold / MULTIPLIER * (MULTIPLIER + PARAMS.tolerance) / MULTIPLIER
        ));
        emit Swapped(amount);
    }

    if (block.timestamp + PARAMS.interval < PARAMS.terminus) {
        canExecAt = block.timestamp + PARAMS.interval;
    } else {
        canExecAt = block.timestamp < PARAMS.terminus ? PARAMS.terminus : type(uint256).max;
    }        
    }

    function setAllowance(address token) public onlyOwner {
        IERC20(token).approve(address(UniSwapper), type(uint256).max);
    }
}