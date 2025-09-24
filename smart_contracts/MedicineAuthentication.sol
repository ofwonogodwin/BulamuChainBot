// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title MedicineAuthentication
 * @dev Smart contract for medicine verification and anti-counterfeiting
 * @author BulamuChainBot Team
 */
contract MedicineAuthentication {
    
    // Events
    event MedicineRegistered(
        string indexed medicineId,
        address indexed manufacturer,
        uint256 timestamp
    );
    
    event MedicineVerified(
        string indexed medicineId,
        address indexed verifier,
        bool isAuthentic,
        uint256 timestamp
    );
    
    event BatchCreated(
        string indexed batchId,
        string indexed medicineId,
        uint256 quantity,
        uint256 timestamp
    );
    
    event OwnershipTransferred(
        string indexed medicineId,
        address indexed from,
        address indexed to,
        uint256 timestamp
    );
    
    event AlertRaised(
        string indexed medicineId,
        address indexed reporter,
        string alertType,
        uint256 timestamp
    );
    
    // Structs
    struct Medicine {
        string medicineId;
        string name;
        string activeIngredient;
        address manufacturer;
        uint256 manufactureDate;
        uint256 expiryDate;
        string batchNumber;
        uint256 dosage;
        string dosageUnit;
        string[] indications;
        bool isActive;
        uint256 registeredAt;
    }
    
    struct Batch {
        string batchId;
        string medicineId;
        uint256 quantity;
        uint256 manufactured;
        uint256 distributed;
        uint256 remaining;
        address currentHolder;
        bool isRecalled;
        string recallReason;
    }
    
    struct VerificationRecord {
        address verifier;
        uint256 timestamp;
        bool isAuthentic;
        string location;
        string notes;
    }
    
    struct CounterfeitAlert {
        string medicineId;
        address reporter;
        string alertType;
        string description;
        string location;
        uint256 timestamp;
        bool investigated;
        string resolution;
    }
    
    // State variables
    address public owner;
    mapping(string => Medicine) public medicines;
    mapping(string => Batch) public batches;
    mapping(string => VerificationRecord[]) public verificationHistory;
    mapping(address => bool) public authorizedManufacturers;
    mapping(address => bool) public authorizedVerifiers;
    mapping(string => CounterfeitAlert[]) public counterfeitAlerts;
    
    string[] public allMedicineIds;
    string[] public allBatchIds;
    
    uint256 public totalVerifications;
    uint256 public totalCounterfeitReports;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action");
        _;
    }
    
    modifier onlyAuthorizedManufacturer() {
        require(
            authorizedManufacturers[msg.sender] || msg.sender == owner,
            "Only authorized manufacturers can perform this action"
        );
        _;
    }
    
    modifier onlyAuthorizedVerifier() {
        require(
            authorizedVerifiers[msg.sender] || msg.sender == owner,
            "Only authorized verifiers can perform this action"
        );
        _;
    }
    
    modifier medicineExists(string memory _medicineId) {
        require(medicines[_medicineId].isActive, "Medicine not found or inactive");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
        authorizedManufacturers[msg.sender] = true;
        authorizedVerifiers[msg.sender] = true;
    }
    
    /**
     * @dev Register a new medicine
     * @param _medicineId Unique identifier for the medicine
     * @param _name Name of the medicine
     * @param _activeIngredient Active ingredient
     * @param _manufactureDate Manufacturing date (timestamp)
     * @param _expiryDate Expiry date (timestamp)
     * @param _batchNumber Batch number
     * @param _dosage Dosage amount
     * @param _dosageUnit Unit of dosage (mg, ml, etc.)
     * @param _indications Array of medical indications
     */
    function registerMedicine(
        string memory _medicineId,
        string memory _name,
        string memory _activeIngredient,
        uint256 _manufactureDate,
        uint256 _expiryDate,
        string memory _batchNumber,
        uint256 _dosage,
        string memory _dosageUnit,
        string[] memory _indications
    ) external onlyAuthorizedManufacturer {
        require(bytes(_medicineId).length > 0, "Medicine ID cannot be empty");
        require(bytes(_name).length > 0, "Medicine name cannot be empty");
        require(_expiryDate > _manufactureDate, "Expiry date must be after manufacture date");
        require(!medicines[_medicineId].isActive, "Medicine already registered");
        
        medicines[_medicineId] = Medicine({
            medicineId: _medicineId,
            name: _name,
            activeIngredient: _activeIngredient,
            manufacturer: msg.sender,
            manufactureDate: _manufactureDate,
            expiryDate: _expiryDate,
            batchNumber: _batchNumber,
            dosage: _dosage,
            dosageUnit: _dosageUnit,
            indications: _indications,
            isActive: true,
            registeredAt: block.timestamp
        });
        
        allMedicineIds.push(_medicineId);
        
        emit MedicineRegistered(_medicineId, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Create a new batch for a medicine
     * @param _batchId Unique batch identifier
     * @param _medicineId Medicine identifier
     * @param _quantity Total quantity in this batch
     */
    function createBatch(
        string memory _batchId,
        string memory _medicineId,
        uint256 _quantity
    ) external onlyAuthorizedManufacturer medicineExists(_medicineId) {
        require(bytes(_batchId).length > 0, "Batch ID cannot be empty");
        require(_quantity > 0, "Quantity must be greater than zero");
        require(bytes(batches[_batchId].batchId).length == 0, "Batch already exists");
        require(medicines[_medicineId].manufacturer == msg.sender, "Only medicine manufacturer can create batch");
        
        batches[_batchId] = Batch({
            batchId: _batchId,
            medicineId: _medicineId,
            quantity: _quantity,
            manufactured: _quantity,
            distributed: 0,
            remaining: _quantity,
            currentHolder: msg.sender,
            isRecalled: false,
            recallReason: ""
        });
        
        allBatchIds.push(_batchId);
        
        emit BatchCreated(_batchId, _medicineId, _quantity, block.timestamp);
    }
    
    /**
     * @dev Verify medicine authenticity
     * @param _medicineId Medicine identifier
     * @param _location Location of verification
     * @param _notes Additional notes
     * @return True if medicine is authentic
     */
    function verifyMedicine(
        string memory _medicineId,
        string memory _location,
        string memory _notes
    ) external onlyAuthorizedVerifier returns (bool) {
        bool isAuthentic = medicines[_medicineId].isActive;
        
        verificationHistory[_medicineId].push(VerificationRecord({
            verifier: msg.sender,
            timestamp: block.timestamp,
            isAuthentic: isAuthentic,
            location: _location,
            notes: _notes
        }));
        
        totalVerifications++;
        
        emit MedicineVerified(_medicineId, msg.sender, isAuthentic, block.timestamp);
        
        return isAuthentic;
    }
    
    /**
     * @dev Get medicine details
     * @param _medicineId Medicine identifier
     * @return All medicine details
     */
    function getMedicine(string memory _medicineId) 
        external 
        view 
        medicineExists(_medicineId)
        returns (
            string memory name,
            string memory activeIngredient,
            address manufacturer,
            uint256 manufactureDate,
            uint256 expiryDate,
            string memory batchNumber,
            uint256 dosage,
            string memory dosageUnit,
            string[] memory indications
        ) 
    {
        Medicine memory med = medicines[_medicineId];
        return (
            med.name,
            med.activeIngredient,
            med.manufacturer,
            med.manufactureDate,
            med.expiryDate,
            med.batchNumber,
            med.dosage,
            med.dosageUnit,
            med.indications
        );
    }
    
    /**
     * @dev Get batch information
     * @param _batchId Batch identifier
     * @return Batch details
     */
    function getBatch(string memory _batchId) 
        external 
        view 
        returns (
            string memory medicineId,
            uint256 quantity,
            uint256 manufactured,
            uint256 distributed,
            uint256 remaining,
            address currentHolder,
            bool isRecalled,
            string memory recallReason
        ) 
    {
        require(bytes(batches[_batchId].batchId).length > 0, "Batch not found");
        
        Batch memory batch = batches[_batchId];
        return (
            batch.medicineId,
            batch.quantity,
            batch.manufactured,
            batch.distributed,
            batch.remaining,
            batch.currentHolder,
            batch.isRecalled,
            batch.recallReason
        );
    }
    
    /**
     * @dev Get verification history for a medicine
     * @param _medicineId Medicine identifier
     * @return Array of verification records
     */
    function getVerificationHistory(string memory _medicineId) 
        external 
        view 
        returns (VerificationRecord[] memory) 
    {
        return verificationHistory[_medicineId];
    }
    
    /**
     * @dev Report counterfeit medicine
     * @param _medicineId Medicine identifier
     * @param _alertType Type of alert (counterfeit, expired, etc.)
     * @param _description Description of the issue
     * @param _location Location where found
     */
    function reportCounterfeit(
        string memory _medicineId,
        string memory _alertType,
        string memory _description,
        string memory _location
    ) external {
        require(bytes(_medicineId).length > 0, "Medicine ID required");
        require(bytes(_alertType).length > 0, "Alert type required");
        
        counterfeitAlerts[_medicineId].push(CounterfeitAlert({
            medicineId: _medicineId,
            reporter: msg.sender,
            alertType: _alertType,
            description: _description,
            location: _location,
            timestamp: block.timestamp,
            investigated: false,
            resolution: ""
        }));
        
        totalCounterfeitReports++;
        
        emit AlertRaised(_medicineId, msg.sender, _alertType, block.timestamp);
    }
    
    /**
     * @dev Recall a batch of medicine
     * @param _batchId Batch identifier
     * @param _reason Reason for recall
     */
    function recallBatch(string memory _batchId, string memory _reason) 
        external 
        onlyAuthorizedManufacturer 
    {
        require(bytes(batches[_batchId].batchId).length > 0, "Batch not found");
        require(bytes(_reason).length > 0, "Recall reason required");
        
        string memory medicineId = batches[_batchId].medicineId;
        require(medicines[medicineId].manufacturer == msg.sender, "Only manufacturer can recall");
        
        batches[_batchId].isRecalled = true;
        batches[_batchId].recallReason = _reason;
    }
    
    /**
     * @dev Check if medicine is expired
     * @param _medicineId Medicine identifier
     * @return True if medicine is expired
     */
    function isExpired(string memory _medicineId) 
        external 
        view 
        medicineExists(_medicineId)
        returns (bool) 
    {
        return block.timestamp > medicines[_medicineId].expiryDate;
    }
    
    /**
     * @dev Add authorized manufacturer
     * @param _manufacturer Manufacturer address
     */
    function addAuthorizedManufacturer(address _manufacturer) external onlyOwner {
        require(_manufacturer != address(0), "Invalid manufacturer address");
        authorizedManufacturers[_manufacturer] = true;
    }
    
    /**
     * @dev Add authorized verifier
     * @param _verifier Verifier address
     */
    function addAuthorizedVerifier(address _verifier) external onlyOwner {
        require(_verifier != address(0), "Invalid verifier address");
        authorizedVerifiers[_verifier] = true;
    }
    
    /**
     * @dev Remove authorized manufacturer
     * @param _manufacturer Manufacturer address
     */
    function removeAuthorizedManufacturer(address _manufacturer) external onlyOwner {
        authorizedManufacturers[_manufacturer] = false;
    }
    
    /**
     * @dev Remove authorized verifier
     * @param _verifier Verifier address
     */
    function removeAuthorizedVerifier(address _verifier) external onlyOwner {
        authorizedVerifiers[_verifier] = false;
    }
    
    /**
     * @dev Get total number of medicines registered
     * @return Total count
     */
    function getTotalMedicines() external view returns (uint256) {
        return allMedicineIds.length;
    }
    
    /**
     * @dev Get total number of batches created
     * @return Total count
     */
    function getTotalBatches() external view returns (uint256) {
        return allBatchIds.length;
    }
    
    /**
     * @dev Get counterfeit alerts for a medicine
     * @param _medicineId Medicine identifier
     * @return Array of counterfeit alerts
     */
    function getCounterfeitAlerts(string memory _medicineId) 
        external 
        view 
        returns (CounterfeitAlert[] memory) 
    {
        return counterfeitAlerts[_medicineId];
    }
    
    /**
     * @dev Transfer contract ownership
     * @param _newOwner New owner address
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Invalid new owner address");
        owner = _newOwner;
        authorizedManufacturers[_newOwner] = true;
        authorizedVerifiers[_newOwner] = true;
    }
}
