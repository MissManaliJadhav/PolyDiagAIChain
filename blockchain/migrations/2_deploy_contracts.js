const DiseaseRecord = artifacts.require("DiseaseRecord");

module.exports = function (deployer) {
  deployer.deploy(DiseaseRecord);
};