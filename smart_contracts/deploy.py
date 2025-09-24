"""
BulamuChainBot Smart Contract Deployment Script
This script compiles and deploys smart contracts to Ethereum networks
"""

import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContractDeployer:
    def __init__(self, network="development"):
        self.network = network
        self.w3 = self._connect_to_network()
        self.account = self._load_account()
        
    def _connect_to_network(self):
        """Connect to blockchain network"""
        if self.network == "development":
            return Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        elif self.network == "sepolia":
            infura_url = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
            return Web3(Web3.HTTPProvider(infura_url))
        elif self.network == "goerli":
            infura_url = f"https://goerli.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
            return Web3(Web3.HTTPProvider(infura_url))
        else:
            raise ValueError(f"Unsupported network: {self.network}")
    
    def _load_account(self):
        """Load deployment account"""
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not found in environment variables")
        return self.w3.eth.account.from_key(private_key)
    
    def compile_contract(self, contract_file):
        """Compile Solidity contract"""
        # Install solc compiler
        install_solc("0.8.19")
        
        # Read contract file
        with open(contract_file, "r") as file:
            contract_source = file.read()
        
        # Compile contract
        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {
                    os.path.basename(contract_file): {
                        "content": contract_source
                    }
                },
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                        }
                    },
                    "optimizer": {
                        "enabled": True,
                        "runs": 200
                    }
                }
            },
            solc_version="0.8.19",
        )
        
        return compiled_sol
    
    def deploy_contract(self, contract_name, compiled_contract, constructor_args=None):
        """Deploy compiled contract to blockchain"""
        contract_interface = compiled_contract["contracts"][f"{contract_name}.sol"][contract_name]
        
        # Create contract instance
        contract = self.w3.eth.contract(
            abi=contract_interface["abi"],
            bytecode=contract_interface["evm"]["bytecode"]["object"]
        )
        
        # Build constructor transaction
        if constructor_args:
            constructor = contract.constructor(*constructor_args)
        else:
            constructor = contract.constructor()
        
        # Estimate gas
        gas_estimate = constructor.estimate_gas({'from': self.account.address})
        
        # Build transaction
        transaction = constructor.build_transaction({
            'from': self.account.address,
            'gas': gas_estimate,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })
        
        # Sign and send transaction
        signed_txn = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"Contract {contract_name} deployed at address: {tx_receipt.contractAddress}")
        print(f"Transaction hash: {tx_hash.hex()}")
        print(f"Gas used: {tx_receipt.gasUsed}")
        
        return tx_receipt.contractAddress, contract_interface["abi"]
    
    def save_deployment_info(self, contract_name, address, abi):
        """Save deployment information to JSON file"""
        deployment_info = {
            "contract_name": contract_name,
            "network": self.network,
            "address": address,
            "abi": abi,
            "deployed_at": self.w3.eth.get_block('latest')['timestamp']
        }
        
        # Create deployments directory if it doesn't exist
        os.makedirs("deployments", exist_ok=True)
        
        # Save to file
        filename = f"deployments/{contract_name}_{self.network}.json"
        with open(filename, "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"Deployment info saved to {filename}")
    
    def deploy_all_contracts(self):
        """Deploy all BulamuChainBot contracts"""
        contracts_to_deploy = [
            ("MedicalRecords", "MedicalRecords.sol"),
            ("MedicineAuthentication", "MedicineAuthentication.sol")
        ]
        
        deployed_contracts = {}
        
        for contract_name, contract_file in contracts_to_deploy:
            print(f"\n--- Deploying {contract_name} ---")
            
            # Compile contract
            compiled_contract = self.compile_contract(contract_file)
            
            # Deploy contract
            address, abi = self.deploy_contract(contract_name, compiled_contract)
            
            # Save deployment info
            self.save_deployment_info(contract_name, address, abi)
            
            deployed_contracts[contract_name] = {
                "address": address,
                "abi": abi
            }
        
        # Save all contracts info
        all_contracts_file = f"deployments/all_contracts_{self.network}.json"
        with open(all_contracts_file, "w") as f:
            json.dump(deployed_contracts, f, indent=2)
        
        print(f"\nAll contracts deployed successfully!")
        print(f"Summary saved to {all_contracts_file}")
        
        return deployed_contracts

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy BulamuChainBot smart contracts")
    parser.add_argument("--network", default="development", 
                       choices=["development", "sepolia", "goerli"],
                       help="Network to deploy to")
    
    args = parser.parse_args()
    
    try:
        # Create deployer instance
        deployer = ContractDeployer(network=args.network)
        
        # Check connection
        if not deployer.w3.is_connected():
            raise ConnectionError(f"Could not connect to {args.network} network")
        
        print(f"Connected to {args.network} network")
        print(f"Account address: {deployer.account.address}")
        print(f"Account balance: {deployer.w3.eth.get_balance(deployer.account.address) / 10**18} ETH")
        
        # Deploy all contracts
        deployed_contracts = deployer.deploy_all_contracts()
        
        print("\n=== Deployment Complete ===")
        for contract_name, info in deployed_contracts.items():
            print(f"{contract_name}: {info['address']}")
        
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
