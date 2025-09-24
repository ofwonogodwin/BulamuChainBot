const MedicalRecords = artifacts.require("MedicalRecords");
const MedicineAuthentication = artifacts.require("MedicineAuthentication");

module.exports = function (deployer) {
  // Deploy MedicalRecords contract first
  deployer.deploy(MedicalRecords).then(function () {
    // Deploy MedicineAuthentication contract
    return deployer.deploy(MedicineAuthentication);
  });
};
