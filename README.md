# Linux Payload Signer Tool

A specialized Linux-based tool designed for Red Team Operations to sign Windows executables using OpenSSL and osslsigncode. This tool helps in bypassing Windows security controls through digital code signing.

## ⚠️ Disclaimer

This tool is intended for authorized Red Team Operations and Penetration Testing only. Any malicious use of this tool is strictly prohibited. Use responsibly and only in environments where you have explicit permission.

## Features

- Sign Windows executable files (.exe)
- Generate self-signed code signing certificates
- Multiple signing options (Standard and Advanced)
- Automatic certificate generation
- Built-in certificate templates for common organizations
- Batch signing support
- Manual signing instructions

## Prerequisites

Before using this tool, ensure you have the following installed on your Linux system:

```bash
# For Debian/Ubuntu based systems
sudo apt update
sudo apt install -y openssl osslsigncode python3 python3-pip

# For Red Hat/Fedora based systems
sudo dnf install -y openssl osslsigncode python3 python3-pip
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zerotwo5/exe_signer.git
cd exe_signer
```

2. Make the script executable:
```bash
chmod +x exe_signer.py
```

## Usage

### Basic Usage
```bash
python3 exe_signer.py
```

The tool provides an interactive menu with the following options:

1. Standard Signing (Single Certificate)
2. Advanced Signing (Multiple Certificates)
3. Manual Instructions Only

### Standard Signing
- Generates a single code signing certificate
- Signs your payload with the generated certificate
- Creates a batch script for future use
- Verifies the signature

### Advanced Signing
- Generates multiple certificates with different organization details
- Creates multiple signed versions of your payload
- Useful for testing different certificate configurations
- Helps in identifying which signature works best for your target environment

### Manual Mode
- Provides step-by-step instructions for manual signing
- Useful when automated signing fails
- Shows exact commands for certificate generation and signing

## Examples

### Example 1: Standard Signing
1. Run the tool:
```bash
python3 exe_signer.py
```
2. Choose option 1 for Standard Signing
3. Enter the path to your payload when prompted
4. The tool will generate certificates and sign your payload

### Example 2: Advanced Signing
1. Run the tool:
```bash
python3 exe_signer.py
```
2. Choose option 2 for Advanced Signing
3. Enter the payload path
4. Optionally provide a company name for certificates
5. The tool will generate multiple signed versions

## Output Files

After successful signing, you'll get:
- Original payload: `your_payload.exe`
- Signed payload: `your_payload_signed.exe`
- Certificate file: `code_signing.pem`
- Private key: `code_signing.key`
- Batch script: `sign_payload.bat`

## Security Considerations

1. Keep your private keys secure
2. Delete sensitive files after use
3. Use different certificates for different operations
4. Test signed payloads in a safe environment first
5. Follow proper OPSEC procedures

## Troubleshooting

### Common Issues:

1. **OpenSSL Error**
   ```bash
   sudo apt install openssl
   ```

2. **osslsigncode Not Found**
   ```bash
   sudo apt install osslsigncode
   ```

3. **Permission Denied**
   ```bash
   chmod +x exe_signer_final.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

[Md.Pranto025](https://github.com/zerotwo5)

## Acknowledgments

- Thanks to the Red Team community
- All the contributors and testers
- OpenSSL and osslsigncode projects

---

⚠️ **Remember**: This tool should only be used for legitimate Red Team operations with proper authorization.

For questions and support: [Open an issue](https://github.com/zerotwo5/linux-payload-signer/issues) or contact me on GitHub [@zerotwo5](https://github.com/zerotwo5)