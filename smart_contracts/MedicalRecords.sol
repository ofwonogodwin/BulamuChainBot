// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title MedicalRecords
 * @dev Smart contract for storing medical record hashes on blockchain
 * @author BulamuChainBot Team
 */
contract MedicalRecords {
    
    // Events
    event RecordStored(
        bytes32 indexed recordHash,
        address indexed patient,
        address indexed provider,
        uint256 timestamp
    );
    
    event RecordAccessed(
        bytes32 indexed recordHash,
        address indexed accessor,
        uint256 timestamp
    );
    
    event ConsentGranted(
        address indexed patient,
        address indexed provider,
        uint256 timestamp
    );
    
    event ConsentRevoked(
        address indexed patient,
        address indexed provider,
        uint256 timestamp
    );
    
    // Structs
    struct MedicalRecord {
        bytes32 recordHash;
        address patient;
        address healthcareProvider;
        uint256 timestamp;
        string recordType;
        bool isActive;
    }
    
    struct PatientConsent {
        address patient;
        address provider;
        bool hasConsent;
        uint256 grantedAt;
        uint256 revokedAt;
    }
    
    // State variables
    address public owner;
    mapping(bytes32 => MedicalRecord) public medicalRecords;
    mapping(address => bytes32[]) public patientRecords;
    mapping(address => mapping(address => PatientConsent)) public consents;
    mapping(address => bool) public authorizedProviders;
    
    bytes32[] public allRecordHashes;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action");
        _;
    }
    
    modifier onlyAuthorizedProvider() {
        require(
            authorizedProviders[msg.sender] || msg.sender == owner,
            "Only authorized healthcare providers can perform this action"
        );
        _;
    }
    
    modifier onlyWithConsent(address patient) {
        require(
            msg.sender == patient || 
            consents[patient][msg.sender].hasConsent ||
            msg.sender == owner,
            "No consent granted for accessing patient records"
        );
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
        authorizedProviders[msg.sender] = true;
    }
    
    /**
     * @dev Store a medical record hash on blockchain
     * @param _recordHash Hash of the medical record
     * @param _patient Address of the patient
     * @param _recordType Type of medical record
     */
    function storeRecord(
        bytes32 _recordHash,
        address _patient,
        string memory _recordType
    ) external onlyAuthorizedProvider {
        require(_recordHash != bytes32(0), "Record hash cannot be empty");
        require(_patient != address(0), "Patient address cannot be zero");
        require(bytes(_recordType).length > 0, "Record type cannot be empty");
        require(!medicalRecords[_recordHash].isActive, "Record already exists");
        
        medicalRecords[_recordHash] = MedicalRecord({
            recordHash: _recordHash,
            patient: _patient,
            healthcareProvider: msg.sender,
            timestamp: block.timestamp,
            recordType: _recordType,
            isActive: true
        });
        
        patientRecords[_patient].push(_recordHash);
        allRecordHashes.push(_recordHash);
        
        emit RecordStored(_recordHash, _patient, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Get medical record details
     * @param _recordHash Hash of the medical record
     * @return Record details
     */
    function getRecord(bytes32 _recordHash) 
        external 
        view 
        onlyWithConsent(medicalRecords[_recordHash].patient)
        returns (
            bytes32 recordHash,
            address patient,
            address provider,
            uint256 timestamp,
            string memory recordType,
            bool isActive
        ) 
    {
        require(medicalRecords[_recordHash].isActive, "Record does not exist");
        
        MedicalRecord memory record = medicalRecords[_recordHash];
        return (
            record.recordHash,
            record.patient,
            record.healthcareProvider,
            record.timestamp,
            record.recordType,
            record.isActive
        );
    }
    
    /**
     * @dev Get all record hashes for a patient
     * @param _patient Address of the patient
     * @return Array of record hashes
     */
    function getPatientRecords(address _patient) 
        external 
        view 
        onlyWithConsent(_patient)
        returns (bytes32[] memory) 
    {
        return patientRecords[_patient];
    }
    
    /**
     * @dev Verify if a record hash exists and is valid
     * @param _recordHash Hash to verify
     * @return True if record exists and is active
     */
    function verifyRecord(bytes32 _recordHash) external view returns (bool) {
        return medicalRecords[_recordHash].isActive;
    }
    
    /**
     * @dev Grant consent to a healthcare provider
     * @param _provider Address of the healthcare provider
     */
    function grantConsent(address _provider) external {
        require(_provider != address(0), "Provider address cannot be zero");
        require(authorizedProviders[_provider], "Provider is not authorized");
        
        consents[msg.sender][_provider] = PatientConsent({
            patient: msg.sender,
            provider: _provider,
            hasConsent: true,
            grantedAt: block.timestamp,
            revokedAt: 0
        });
        
        emit ConsentGranted(msg.sender, _provider, block.timestamp);
    }
    
    /**
     * @dev Revoke consent from a healthcare provider
     * @param _provider Address of the healthcare provider
     */
    function revokeConsent(address _provider) external {
        require(consents[msg.sender][_provider].hasConsent, "No consent granted");
        
        consents[msg.sender][_provider].hasConsent = false;
        consents[msg.sender][_provider].revokedAt = block.timestamp;
        
        emit ConsentRevoked(msg.sender, _provider, block.timestamp);
    }
    
    /**
     * @dev Check if patient has granted consent to provider
     * @param _patient Patient address
     * @param _provider Provider address
     * @return True if consent is granted
     */
    function hasConsent(address _patient, address _provider) 
        external 
        view 
        returns (bool) 
    {
        return consents[_patient][_provider].hasConsent;
    }
    
    /**
     * @dev Add authorized healthcare provider (only owner)
     * @param _provider Address of the healthcare provider
     */
    function addAuthorizedProvider(address _provider) external onlyOwner {
        require(_provider != address(0), "Provider address cannot be zero");
        authorizedProviders[_provider] = true;
    }
    
    /**
     * @dev Remove authorized healthcare provider (only owner)
     * @param _provider Address of the healthcare provider
     */
    function removeAuthorizedProvider(address _provider) external onlyOwner {
        authorizedProviders[_provider] = false;
    }
    
    /**
     * @dev Get total number of records
     * @return Total count of medical records
     */
    function getTotalRecords() external view returns (uint256) {
        return allRecordHashes.length;
    }
    
    /**
     * @dev Emergency access function for authorized personnel
     * @param _recordHash Hash of the medical record
     * @param _reason Emergency access reason
     */
    function emergencyAccess(bytes32 _recordHash, string memory _reason) 
        external 
        onlyAuthorizedProvider
        returns (
            bytes32 recordHash,
            address patient,
            address provider,
            uint256 timestamp,
            string memory recordType
        ) 
    {
        require(medicalRecords[_recordHash].isActive, "Record does not exist");
        require(bytes(_reason).length > 0, "Emergency reason required");
        
        MedicalRecord memory record = medicalRecords[_recordHash];
        
        emit RecordAccessed(_recordHash, msg.sender, block.timestamp);
        
        return (
            record.recordHash,
            record.patient,
            record.healthcareProvider,
            record.timestamp,
            record.recordType
        );
    }
    
    /**
     * @dev Update contract owner (only current owner)
     * @param _newOwner Address of the new owner
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "New owner address cannot be zero");
        owner = _newOwner;
        authorizedProviders[_newOwner] = true;
    }
}
