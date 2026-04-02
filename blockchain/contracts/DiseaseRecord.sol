// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract DiseaseRecord {

    struct Record {
        string patientId;
        string disease;
        string result;
        uint256 timestamp;
    }

    Record[] public records;

    // STORE RECORD (timestamp auto-added)
    function addRecord(
        string memory _patientId,
        string memory _disease,
        string memory _result
    ) public {

        records.push(
            Record(
                _patientId,
                _disease,
                _result,
                block.timestamp   // ⭐ BLOCKCHAIN TIME
            )
        );
    }

    // GET SINGLE RECORD
    function getRecord(uint index)
        public view
        returns(
            string memory,
            string memory,
            string memory,
            uint256
        )
    {
        Record memory r = records[index];
        return (r.patientId, r.disease, r.result, r.timestamp);
    }

    // TOTAL RECORD COUNT
    function recordsLength() public view returns(uint256){
        return records.length;
    }
}