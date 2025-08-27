# PowerShell script to connect to EC2 instance
# Step 1: Download the key from S3
aws s3 cp s3://dzgro-secrets/FastApiServerKey.pem .\FastApiServerKey.pem

# Step 1.5: Fix permissions for the private key
icacls .\FastApiServerKey.pem /inheritance:r
icacls .\FastApiServerKey.pem /grant:r "$($env:USERNAME):(F)"
icacls .\FastApiServerKey.pem /remove "NT AUTHORITY\Authenticated Users"

# Step 2: Build and package projects
cd dzgroshared
poetry install
poetry build
cd ../api
poetry install
poetry lock
poetry build
cd ..

# Step 3: Prepare deployment folder
if (!(Test-Path .\deploy_upload)) {
    mkdir deploy_upload
}
copy .\api\dist\*.whl .\deploy_upload\
copy .\dzgroshared\dist\*.whl .\deploy_upload\
copy .\api\pyproject.toml .\deploy_upload\
copy .\api\poetry.lock .\deploy_upload\

# Step 4: Compress deployment folder
Compress-Archive -Path .\deploy_upload -DestinationPath .\deploy_upload.zip -Force

# Step 5: Upload to EC2
scp -i ".\FastApiServerKey.pem" .\deploy_upload.zip ubuntu@13.235.44.227:~

# Step 6: SSH into EC2 and run setup commands
$remoteCommands = @"
# Remove previous deployment folders and zip files
rm -rf ~/deploy_upload ~/venv
sudo apt-get update
sudo apt-get install -y unzip python3.12-venv
unzip -o ~/deploy_upload.zip -d ~/deploy_upload
cd ~/deploy_upload/deploy_upload
python3.12 -m venv venv
source venv/bin/activate
pip install *.whl
sudo fuser -k 8000/tcp
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
"@
$remoteCommands = $remoteCommands -replace "`r", ""
ssh -i ".\FastApiServerKey.pem" ubuntu@13.235.44.227 "$remoteCommands"

# Step 7: Remove the FastApiServerKey.pem after script is done
# Ensure key can be deleted
Takeown /F .\FastApiServerKey.pem
attrib -R .\FastApiServerKey.pem
icacls .\FastApiServerKey.pem /grant:r "$($env:USERNAME):(F)"
Remove-Item .\FastApiServerKey.pem
