#!/bin/bash
# Update version and upload to Test PyPI

echo "🔄 Updating package version for Test PyPI..."

# Get current version from pyproject.toml
current_version=$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
echo "📋 Current version: $current_version"

# Suggest new version
if [ "$current_version" = "0.1.0" ]; then
    new_version="0.1.1"
elif [ "$current_version" = "0.1.1" ]; then
    new_version="0.1.2"
elif [ "$current_version" = "0.1.2" ]; then
    new_version="0.1.3"
else
    # Parse version and increment patch
    IFS='.' read -ra ADDR <<< "$current_version"
    major=${ADDR[0]}
    minor=${ADDR[1]}
    patch=${ADDR[2]}
    new_patch=$((patch + 1))
    new_version="$major.$minor.$new_patch"
fi

echo "🆕 New version will be: $new_version"
echo ""

# Ask for confirmation
read -p "Update to version $new_version? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ Updating version..."
    
    # Update pyproject.toml
    sed -i.backup "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
    
    echo "📝 Updated pyproject.toml:"
    grep 'version = ' pyproject.toml
    
    # Clean previous builds
    echo "🧹 Cleaning previous builds..."
    rm -rf dist/ build/ *.egg-info/
    
    # Build new package
    echo "📦 Building package version $new_version..."
    python -m build
    
    if [ $? -eq 0 ]; then
        echo "✅ Package built successfully!"
        echo ""
        echo "📋 New package files:"
        ls -la dist/
        echo ""
        
        # Check package
        echo "🔍 Checking package..."
        python -m twine check dist/*
        
        if [ $? -eq 0 ]; then
            echo "✅ Package check passed!"
            echo ""
            echo "🚀 Uploading to Test PyPI..."
            echo "   (You'll need your Test PyPI API token)"
            echo ""
            
            python -m twine upload --repository testpypi dist/*
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "🎉 Successfully uploaded version $new_version to Test PyPI!"
                echo ""
                echo "📦 Test installation:"
                echo "   pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence==$new_version"
                echo ""
                echo "🔗 View updated package:"
                echo "   https://test.pypi.org/project/langchain-iointelligence/"
                echo ""
                echo "✅ Package successfully updated on Test PyPI!"
            else
                echo "❌ Upload failed!"
                # Restore backup
                mv pyproject.toml.backup pyproject.toml
                exit 1
            fi
        else
            echo "❌ Package check failed!"
            mv pyproject.toml.backup pyproject.toml
            exit 1
        fi
    else
        echo "❌ Build failed!"
        mv pyproject.toml.backup pyproject.toml
        exit 1
    fi
else
    echo "❌ Version update cancelled."
    exit 1
fi
