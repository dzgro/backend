from mapping import Region, Environment

def build_layer_zip_clean():
    """
    Creates dzgroshared_layer.zip at the project root with all dependencies and custom code.
    This creates a proper AWS Lambda layer structure with dependencies in python/lib/python3.12/site-packages/
    """
    import os
    import shutil
    import zipfile
    import subprocess
    
    # Paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dzgroshared_dir = os.path.join(project_root, 'dzgroshared')
    layer_build_dir = os.path.join(os.path.dirname(__file__), 'layer_build')
    python_dir = os.path.join(layer_build_dir, 'python')
    site_packages_dir = os.path.join(python_dir, 'lib', 'python3.12', 'site-packages')
    layer_zip = os.path.join(project_root, 'dzgroshared_layer.zip')

    print("Building Lambda layer with dependencies...")
    
    # Clean up previous build
    if os.path.exists(layer_build_dir):
        shutil.rmtree(layer_build_dir)
    
    # Create layer directory structure
    os.makedirs(site_packages_dir, exist_ok=True)
    
    try:
        # Step 1: Install dependencies using pip from the dzgroshared project
        print("Installing dependencies...")
        pip_install_cmd = [
            'pip', 'install', '--target', site_packages_dir,
            '--no-deps',  # Don't install sub-dependencies to avoid conflicts
            dzgroshared_dir
        ]
        subprocess.run(pip_install_cmd, check=True, cwd=project_root)
        
        # Step 2: Install dependencies listed in pyproject.toml with specified versions
        print("Installing project dependencies...")
        import toml
        pyproject_path = os.path.join(dzgroshared_dir, 'pyproject.toml')
        pyproject = toml.load(pyproject_path)
        # Get dependencies from [tool.poetry.dependencies] (excluding python itself)
        deps = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
        dep_list = []
        for pkg, ver in deps.items():
            if pkg.lower() == 'python':
                continue
            # Poetry allows version to be a string or a dict (for extras)
            if isinstance(ver, str):
                # Handle version constraints like "^1.0.0" by converting to specific version
                if ver.startswith('^'):
                    dep_list.append(f"{pkg}>={ver[1:]}")
                elif ver.startswith('~'):
                    dep_list.append(f"{pkg}>={ver[1:]}")
                else:
                    dep_list.append(f"{pkg}=={ver}")
            elif isinstance(ver, dict) and 'version' in ver:
                version = ver['version']
                if version.startswith('^'):
                    dep_list.append(f"{pkg}>={version[1:]}")
                elif version.startswith('~'):
                    dep_list.append(f"{pkg}>={version[1:]}")
                else:
                    dep_list.append(f"{pkg}=={version}")
            else:
                dep_list.append(pkg)
        pip_deps_cmd = [
            'pip', 'install', '--target', site_packages_dir,
            # Remove --no-deps to allow installation of required sub-dependencies
            *dep_list
        ]
        subprocess.run(pip_deps_cmd, check=True, cwd=project_root)
        
        # Step 3: Copy the source code properly
        print("Copying dzgroshared source code...")
        src_dir = os.path.join(dzgroshared_dir, 'src', 'dzgroshared')
        dest_dir = os.path.join(site_packages_dir, 'dzgroshared')
        
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.copytree(src_dir, dest_dir)
        
        # Step 4: Create the zip file with proper Lambda layer structure
        print("Creating layer zip file...")
        with zipfile.ZipFile(layer_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all files from python directory to the zip
            for root, dirs, files in os.walk(python_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create archive path relative to layer_build_dir
                    archive_path = os.path.relpath(file_path, layer_build_dir)
                    zf.write(file_path, archive_path)
        
        print(f"Layer zipped at {layer_zip}")
        
        # Get zip file size for verification
        zip_size = os.path.getsize(layer_zip) / (1024 * 1024)  # Size in MB
        print(f"Layer zip size: {zip_size:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during pip install: {e}")
        raise
    except Exception as e:
        print(f"Error building layer: {e}")
        raise
    finally:
        # Clean up build directory
        if os.path.exists(layer_build_dir):
            shutil.rmtree(layer_build_dir)
            print(f"Deleted intermediary build directory: {layer_build_dir}")

def deploy_layer(region: Region, env: Environment):
    # Publish layer using boto3
    import boto3
    client = boto3.client("lambda", region_name=region.value)
    import os
    layer_name = f"dzgroshared-{env.value.lower()}"
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    layer_zip = os.path.join(project_root, f"{layer_name}.zip")
    with open(layer_zip, "rb") as f:
        response = client.publish_layer_version(
            LayerName=layer_name,
            Description=f"Dzgroshared Layer for {env.value} environment",
            Content={"ZipFile": f.read()},
            CompatibleRuntimes=["python3.12"],
            LicenseInfo="MIT"
        )
    layer_arn = response["LayerVersionArn"]
    print(f"Published Lambda layer ARN: {layer_arn}")
    return layer_arn
