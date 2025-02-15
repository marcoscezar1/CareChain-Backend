// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "../lib/coprocessor-base-contract/src/CoprocessorAdapter.sol";

contract CareChainContract is CoprocessorAdapter {
    string public careResults;
    event ResultReceived(bytes32 indexed inputPayloadHash, bytes output);

    constructor(address _taskIssuerAddress, bytes32 _machineHash)
        CoprocessorAdapter(_taskIssuerAddress, _machineHash)
    {}

    function runExecution(bytes memory input) external {
        callCoprocessor(input);
    }

    function handleNotice(bytes32 inputPayloadHash, bytes memory notice) internal override {
        careResults = abi.decode(notice, (string));
        emit ResultReceived(inputPayloadHash, notice);
    }

    function get() external view returns (string memory) {
        return careResults;
    }
}
