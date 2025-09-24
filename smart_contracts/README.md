# BulamuChainBot Smart Contracts

This directory contains the Solidity smart contracts for the BulamuChainBot healthcare blockchain system.

## Contracts Overview

### 1. MedicalRecords.sol
- **Purpose**: Store medical record hashes on blockchain with privacy controls
- **Features**:
  - Secure hash storage for medical records
  - Patient consent management
  - Healthcare provider authorization
  - Access logging and audit trails
  - Emergency access capabilities

### 2. MedicineAuthentication.sol
- **Purpose**: Medicine verification and anti-counterfeiting system
- **Features**:
  - Medicine registration and batch tracking
  - Authenticity verification
  - Counterfeit reporting system
  - Batch recall capabilities
  - Manufacturer authorization

## Deployment

### Prerequisites
1. Node.js and npm installed
2. Python 3.8+ with required packages
3. Ethereum wallet with testnet ETH
4. Infura account for testnet deployment

### Environment Setup
Create a `.env` file in the smart_contracts directory:
```bash
PRIVATE_KEY=your_wallet_private_key
INFURA_PROJECT_ID=your_infura_project_id
```

### Local Development
```bash
# Install Truffle globally
npm install -g truffle

# Install dependencies
npm install

# Start local blockchain (Ganache)
ganache-cli

# Compile contracts
npm run compile

# Deploy to local network
npm run deploy:development
```

### Testnet Deployment
```bash
# Deploy to Sepolia testnet
npm run deploy:sepolia

# Deploy to Goerli testnet
npm run deploy:goerli
```

### Python Deployment Script
```bash
# Install Python dependencies
pip install web3 py-solc-x python-dotenv

# Deploy using Python script
python deploy.py --network development
python deploy.py --network sepolia
python deploy.py --network goerli
```

## Contract Addresses

After deployment, contract addresses will be saved in the `deployments/` directory:
- `deployments/MedicalRecords_[network].json`
- `deployments/MedicineAuthentication_[network].json`
- `deployments/all_contracts_[network].json`

## Integration with Django Backend

The deployed contracts integrate with the Django backend through:
- `backend/blockchain/services.py` - Web3 service layer
- `backend/blockchain/models.py` - Database models for blockchain data
- `backend/records/services.py` - Medical record blockchain integration
- `backend/consultations/services.py` - Medicine verification integration

## Security Features

### Access Control
- Owner-only administrative functions
- Role-based permissions (manufacturers, verifiers, providers)
- Patient consent management
- Emergency access protocols

### Data Privacy
- Only hashes stored on-chain, not raw data
- Consent-based access control
- Audit trail for all access attempts
- Encryption integration ready

### Anti-Counterfeiting
- Manufacturer authorization system
- Batch tracking and recall capabilities
- Community-based reporting system
- Verification history tracking

## Testing

### Unit Tests
```bash
# Run Truffle tests
truffle test

# Run specific test file
truffle test test/medical_records.js
```

### Integration Tests
Integration tests are included in the Django backend test suite.

## Gas Optimization

- Compiler optimization enabled (200 runs)
- Efficient data structures
- Minimal storage usage
- Event-based logging for cost efficiency

## Network Configuration

### Supported Networks
- **Development**: Local Ganache (127.0.0.1:8545)
- **Sepolia**: Ethereum testnet via Infura
- **Goerli**: Ethereum testnet via Infura
- **Mainnet**: Ready for production deployment

### Gas Limits
- Development: 6,721,975 gas
- Testnets: 4,500,000 gas
- Gas price: Auto-calculated based on network

## Monitoring and Maintenance

### Event Monitoring
All contracts emit events for:
- Record storage and access
- Medicine registration and verification
- Consent changes
- Security alerts

### Upgradability
Contracts are designed with upgradeability in mind:
- Proxy pattern ready
- Data migration support
- Backward compatibility maintained

## License
MIT License - See LICENSE file for details

## Support
For technical support or questions:
- Check the Django backend integration
- Review deployment logs in `deployments/`
- Monitor transaction status on block explorers
- Contact the development team
