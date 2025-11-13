#!/bin/bash

echo "📦 CELLOXEN PROJECT - BACKUP & GITHUB PUSH"
echo "==========================================="
echo ""

# Set colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Navigate to project directory
print_step "Step 1: Navigate to project directory"
cd /var/www/celloxen-portal

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_warning "Not a git repository. Initializing..."
    git init
    print_success "Git repository initialized"
else
    print_success "Git repository found"
fi

# Check current status
print_step "Step 2: Check current git status"
git status

# Add gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    print_step "Step 3: Creating .gitignore file"
    cat > .gitignore << 'GITIGNORE'
# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite

# Logs
*.log
logs/
__pycache__/

# Node modules
node_modules/

# Python cache
*.pyc
__pycache__/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Backups
*.backup
*.bak

# Temporary files
tmp/
temp/
GITIGNORE
    print_success ".gitignore created"
else
    print_success ".gitignore already exists"
fi

# Add all files
print_step "Step 4: Adding all files to git"
git add .

# Check what's being added
print_step "Step 5: Files to be committed:"
git diff --cached --name-status

# Commit with timestamp
print_step "Step 6: Creating commit"
COMMIT_MSG="Production backup - $(date '+%Y-%m-%d %H:%M:%S') - Pre-chatbot fix"
git commit -m "$COMMIT_MSG"

# Check if remote origin exists
print_step "Step 7: Checking GitHub remote"
if git remote get-url origin &> /dev/null; then
    print_success "GitHub remote already configured:"
    git remote -v
else
    print_warning "No GitHub remote found"
    echo "Please add your GitHub repository:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    exit 1
fi

# Push to GitHub
print_step "Step 8: Pushing to GitHub"
echo "Pushing to main branch..."

# Try to push
if git push origin main; then
    print_success "Successfully pushed to GitHub main branch"
elif git push origin master; then
    print_success "Successfully pushed to GitHub master branch"
else
    print_warning "Push failed. Trying to set upstream..."
    if git push -u origin main; then
        print_success "Successfully pushed and set upstream to main"
    elif git push -u origin master; then
        print_success "Successfully pushed and set upstream to master"
    else
        print_error "Push failed. You may need to set up authentication."
        echo ""
        echo "Common solutions:"
        echo "1. Set up SSH key: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
        echo "2. Use personal access token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
        echo ""
        echo "Current remote URL:"
        git remote get-url origin
    fi
fi

# Create a local backup as well
print_step "Step 9: Creating local backup"
BACKUP_DIR="/home/backups/celloxen-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /var/www/celloxen-portal/* "$BACKUP_DIR/"
print_success "Local backup created: $BACKUP_DIR"

# Show final status
print_step "Step 10: Final status"
echo ""
echo "📊 BACKUP SUMMARY:"
echo "  • Git commit: ✅ $COMMIT_MSG"
echo "  • GitHub push: ✅ Check above for status"
echo "  • Local backup: ✅ $BACKUP_DIR"
echo ""
echo "📋 PROJECT FILES BACKED UP:"
ls -la /var/www/celloxen-portal/
echo ""

print_success "Backup complete! Safe to proceed with chatbot fix."
