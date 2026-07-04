#!/bin/bash
# Kamal wrapper script with interactive versioning support
#
# Usage:
#   ./kamal.sh deploy                    # Interactive version selection
#   ./kamal.sh deploy -v v1.2.3          # Deploy with specific version (skip prompt)
#   ./kamal.sh deploy --auto             # Auto-generate version (skip prompt)
#   ./kamal.sh rollback v1.2.2           # Rollback to specific version
#   ./kamal.sh app containers            # List deployed versions
#   ./kamal.sh <any kamal command>       # Pass through to kamal

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Generate version from git
generate_version() {
    local sha=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    local timestamp=$(date +%Y%m%d-%H%M)
    echo "${sha}-${timestamp}"
}

# Get current git tag if exists
get_current_tag() {
    git describe --tags --exact-match 2>/dev/null || echo ""
}

# Get latest tag (globally, not just reachable from HEAD)
get_latest_tag() {
    git tag --sort=-v:refname | head -1 2>/dev/null || echo ""
}

# Check for uncommitted changes and unpushed commits
check_git_status() {
    local has_issues=false

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                  GIT STATUS CHECK                      ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "  ${RED}⚠ UNCOMMITTED CHANGES DETECTED${NC}"
        echo ""
        echo "  Modified files:"
        git diff --name-only HEAD | while read file; do
            echo -e "    ${YELLOW}• $file${NC}"
        done
        echo ""
        has_issues=true
    fi

    # Check for staged but uncommitted changes
    if ! git diff --cached --quiet 2>/dev/null; then
        echo -e "  ${RED}⚠ STAGED CHANGES NOT COMMITTED${NC}"
        echo ""
        echo "  Staged files:"
        git diff --cached --name-only | while read file; do
            echo -e "    ${YELLOW}• $file${NC}"
        done
        echo ""
        has_issues=true
    fi

    # Check for unpushed commits
    local unpushed=$(git log @{u}..HEAD --oneline 2>/dev/null)
    if [ -n "$unpushed" ]; then
        echo -e "  ${RED}⚠ UNPUSHED COMMITS DETECTED${NC}"
        echo ""
        echo "  Commits not pushed to remote:"
        git log @{u}..HEAD --oneline | while read line; do
            echo -e "    ${YELLOW}• $line${NC}"
        done
        echo ""
        has_issues=true
    fi

    if [ "$has_issues" = true ]; then
        echo -e "${CYAN}───────────────────────────────────────────────────────${NC}"
        echo ""
        echo -e "  ${RED}WARNING: Kamal builds from git, so uncommitted/unpushed${NC}"
        echo -e "  ${RED}changes will NOT be included in the deploy!${NC}"
        echo ""
        echo "  Options:"
        echo -e "    ${GREEN}1)${NC} Commit & push changes, then continue"
        echo -e "    ${GREEN}2)${NC} Continue anyway (deploy without local changes)"
        echo -e "    ${RED}q)${NC} Cancel deploy"
        echo ""

        read -p "  Choice [1, 2, q]: " git_choice
        echo ""

        case $git_choice in
            1)
                # Offer to commit
                if ! git diff-index --quiet HEAD -- 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
                    read -p "  Commit message: " commit_msg
                    if [ -z "$commit_msg" ]; then
                        echo -e "  ${RED}No commit message, cancelled.${NC}"
                        exit 1
                    fi
                    git add -A
                    git commit -m "$commit_msg"
                    echo -e "  ${GREEN}Changes committed${NC}"
                fi

                # Push if there are unpushed commits
                if [ -n "$(git log @{u}..HEAD --oneline 2>/dev/null)" ]; then
                    echo -e "  ${YELLOW}Pushing to remote...${NC}"
                    git push
                    echo -e "  ${GREEN}Changes pushed${NC}"
                fi
                echo ""
                ;;
            2)
                echo -e "  ${YELLOW}Continuing without local changes...${NC}"
                echo ""
                ;;
            q|Q|*)
                echo -e "  ${RED}Cancelled.${NC}"
                exit 0
                ;;
        esac
    else
        echo -e "  ${GREEN}✓ Working directory clean${NC}"
        echo -e "  ${GREEN}✓ All commits pushed${NC}"
        echo ""
    fi
}

# Suggest next version based on latest tag
suggest_next_version() {
    local latest=$(get_latest_tag)
    if [ -z "$latest" ]; then
        echo "v1.0.0"
        return
    fi

    # Try to increment patch version (v1.2.3 -> v1.2.4)
    if [[ $latest =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        local major="${BASH_REMATCH[1]}"
        local minor="${BASH_REMATCH[2]}"
        local patch="${BASH_REMATCH[3]}"
        echo "v${major}.${minor}.$((patch + 1))"
    else
        echo "${latest}-2"
    fi
}

# Interactive version selection
select_version() {
    local current_tag=$(get_current_tag)
    local latest_tag=$(get_latest_tag)
    local auto_version=$(generate_version)
    local suggested=$(suggest_next_version)

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}              KAMAL DEPLOY - VERSION SELECT             ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Current commit: ${YELLOW}$(git rev-parse --short HEAD)${NC} - $(git log -1 --format=%s)"
    [ -n "$current_tag" ] && echo -e "  Current tag:    ${GREEN}$current_tag${NC}"
    [ -n "$latest_tag" ] && echo -e "  Latest tag:     ${BLUE}$latest_tag${NC}"
    echo ""
    echo -e "${CYAN}───────────────────────────────────────────────────────${NC}"
    echo ""
    echo "  Select versioning option:"
    echo ""
    echo -e "    ${GREEN}1)${NC} Create new git tag ${YELLOW}[$suggested]${NC}"
    echo -e "    ${GREEN}2)${NC} Enter custom version/tag"
    echo -e "    ${GREEN}3)${NC} Use auto-generated ${YELLOW}[$auto_version]${NC}"
    [ -n "$current_tag" ] && echo -e "    ${GREEN}4)${NC} Use existing tag ${YELLOW}[$current_tag]${NC}"
    echo ""
    echo -e "    ${RED}q)${NC} Cancel"
    echo ""

    read -p "  Choice [1-4, q]: " choice
    echo ""

    case $choice in
        1)
            read -p "  Enter tag name [$suggested]: " tag_name
            tag_name=${tag_name:-$suggested}

            # Auto-generate tag message from latest commit
            tag_message="Release $tag_name - $(git log -1 --format=%s)"

            echo ""
            echo -e "  ${YELLOW}Creating git tag:${NC} $tag_name"
            git tag -a "$tag_name" -m "$tag_message"

            echo -e "  ${YELLOW}Pushing tag to remote...${NC}"
            git push origin "$tag_name"
            echo -e "  ${GREEN}Tag pushed to remote${NC}"

            VERSION="$tag_name"
            ;;
        2)
            read -p "  Enter version: " custom_version
            if [ -z "$custom_version" ]; then
                echo -e "  ${RED}No version entered, cancelled.${NC}"
                exit 1
            fi
            VERSION="$custom_version"
            ;;
        3)
            VERSION="$auto_version"
            ;;
        4)
            if [ -n "$current_tag" ]; then
                VERSION="$current_tag"
            else
                echo -e "  ${RED}No current tag available${NC}"
                exit 1
            fi
            ;;
        q|Q)
            echo -e "  ${RED}Cancelled.${NC}"
            exit 0
            ;;
        *)
            echo -e "  ${RED}Invalid choice, cancelled.${NC}"
            exit 1
            ;;
    esac

    echo ""
    echo -e "${CYAN}───────────────────────────────────────────────────────${NC}"
    echo -e "  ${GREEN}Deploying version:${NC} ${YELLOW}$VERSION${NC}"
    echo -e "${CYAN}───────────────────────────────────────────────────────${NC}"
    echo ""

}

# Parse arguments
VERSION=""
AUTO_MODE=false
KAMAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        --auto)
            AUTO_MODE=true
            shift
            ;;
        *)
            KAMAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Interactive version selection for deploy command
if [[ " ${KAMAL_ARGS[*]} " =~ " deploy " ]]; then
    # Check git status first
    check_git_status

    if [ -z "$VERSION" ]; then
        if [ "$AUTO_MODE" = true ]; then
            VERSION=$(generate_version)
            echo -e "${GREEN}Auto-generated version:${NC} $VERSION"
        else
            select_version
        fi
    else
        echo -e "${YELLOW}Using specified version:${NC} $VERSION"
    fi
fi

# Clear caches before deploy
if [[ " ${KAMAL_ARGS[*]} " =~ " deploy " ]]; then
    echo ""
    echo -e "${YELLOW}Clearing Python bytecode cache...${NC}"
    find . -type f -name "*.pyc" -delete 2>/dev/null
    find . -type f -name "*.pyo" -delete 2>/dev/null
    find . -type d -name "__pycache__" -empty -delete 2>/dev/null
    echo -e "${GREEN}Python cache cleared${NC}"

    echo -e "${YELLOW}Pulling fresh base images...${NC}"
    docker pull python:3.12-slim-bookworm 2>/dev/null || true
    docker pull node:22-bookworm-slim 2>/dev/null || true
    echo -e "${GREEN}Base images refreshed${NC}"

    echo -e "${YELLOW}Clearing Docker build cache...${NC}"
    docker builder prune -af --force 2>/dev/null || true
    echo -e "${GREEN}Docker build cache cleared${NC}"
    echo ""
fi

# Detect project paths dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKDIR_NAME="$(basename "$SCRIPT_DIR")"

# Build the kamal command
KAMAL_CMD="docker run --rm \
  -v $PROJECT_ROOT:/workdir \
  -v $HOME/.ssh:/root/.ssh \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -w /workdir/$WORKDIR_NAME"

# Add version if specified
if [ -n "$VERSION" ]; then
    KAMAL_CMD="$KAMAL_CMD -e VERSION=$VERSION"
fi

# Run kamal
$KAMAL_CMD ghcr.io/basecamp/kamal:latest "${KAMAL_ARGS[@]}"
