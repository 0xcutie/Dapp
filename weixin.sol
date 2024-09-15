// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "hardhat/console.sol";

contract Dapp {

    uint public amount;
    address public payee;
    address public payer;
    address public owner;

    // 定義交易的事件
    event TransferEvent(address indexed payer, address indexed payee, uint amount);

    constructor() {
        owner = msg.sender;
        //console.log("Contract deployed by: ", owner);
    }

    // 進行交易，僅記錄 payer 和 payee 的地址與金額，不實際轉移資金
    function weixin(uint amount_to_transfer, address payee_ad, address payer_ad) public {
        console.log("weixin called with: ", amount_to_transfer, payee_ad, payer_ad);
        amount = amount_to_transfer;
        payee = payee_ad;
        payer = payer_ad;

        // 觸發 TransferEvent 事件，將 payer、payee 和 amount 傳入事件
        emit TransferEvent(payer, payee, amount);
    }

    // 查詢交易的細節
    function check_tx() public view returns (address, address, uint) {
        return (payer, payee, amount);
    }

    // 存錢功能，將金額記錄下來
    function store_m(uint amount_to_store) public {
        amount = amount_to_store;
        payer = msg.sender;

        // 此處可以考慮觸發存錢事件，如果需要
    }

    // 查詢存入的金額
    function view_m() public view returns (uint) {
        return amount;
    }
}
