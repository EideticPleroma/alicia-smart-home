You are Cline, enforcing GitFlow in the Alicia project. These are foundational rules for version control, ensuring organized development across phases and components like Docker files and voice scripts. Always adhere strictly, integrating with other rules (e.g., run tests from integrationTesting.md before merges).

### Core GitFlow Rules from README (Summarized and Enforced)
1. **Branch Structure**:
   - **main**: Production-ready code. Only merge from release or hotfix branches. Never commit directly here.
   - **develop**: Integration branch for features. Merge feature branches here after testing.
   - **feature/**: For new features. Branch from develop, merge back via PR.
     - Current active features:
       - `feature/add-cline-rules`: Consolidating Cline workflow rules
       - `feature/docs-obsidian-updates`: Documentation updates for Obsidian
       - `feature/docs-restructure`: Restructuring project documentation
       - `feature/phase-2-sonos-integration`: Sonos speaker integration
       - `feature/phase-4-multi-language-support`: Multi-language voice support
       - `feature/sonos-bdd-tests`: BDD testing for Sonos integration
       - `feature/test-pack-development`: Test framework development
   - **test/**: For test development and BDD scenarios. Branch from develop, merge back after validation.
   - **release/**: For preparing releases (e.g., release/v1.0). Branch from develop, merge to main and develop after QA.
   - **hotfix/**: For urgent fixes (e.g., hotfix/security-patch). Branch from main, merge to main and develop.
   - **support/**: For long-term support branches if needed (e.g., support/v1.x).

### Core Rules
1. **Branch Structure**:
   - **main**: Production-ready; merge only from release/hotfix. Never commit directly.
   - **develop**: Feature integration; merge from feature branches post-testing.
   - **feature/**: New work (e.g., feature/voice-pipeline-phase1); branch from develop.
   - **release/**: Prep releases (e.g., release/v1.0-phase2); branch from develop, merge to main/develop.
   - **hotfix/**: Urgent fixes (e.g., hotfix/docker-yaml-error); branch from main.
   - **support/**: For long-term branches (e.g., support/v1.x-enterprise).
2. **Workflow Steps**:
   - Create branches from appropriate base (e.g., git checkout -b feature/new-tts develop).
   - Use semantic commits (e.g., "feat(voice): add Piper TTS integration" or "fix(docker): resolve YAML escape in voice-processing").
   - Require PRs with reviews, tests (link to integrationTesting.md), and issue links.
   - Run linting/unit tests before merging; on Windows, ensure CRLF line endings are handled (git config --global core.autocrlf true).
   - For releases: Bump semantic version, update README/changelog, tag (e.g., git tag v1.0.0).
   - Cleanup: Delete merged branches.
3. **Security and Best Practices**: Scan for secrets before commits (e.g., avoid hardcoding passwords in docker-compose.yml); use env vars. Rebase regularly to avoid conflicts.
4. **Project-Specific**: Align branches with phases (e.g., feature/phase1-postgres-setup); for Windows devs, add .gitattributes for line endings.

### Enforcement Guidelines
- Structure responses: "GitFlow Compliance Check", "Proposed Steps", "Commands", "Rationale".
- Reject violations: "This breaks rule [X]; alternative: [compliant step]".
- Integration with Other Rules: Reference projectFlowPhasing.md for phase alignment; dockerManagement.md for config changes; integrationTesting.md for pre-merge tests.

### Examples
- User: "Add Whisper STT to voice-processing." → Compliance: Yes, via feature branch. Steps: git checkout develop; git pull; git checkout -b feature/phase1-whisper-stt. Commands: git add start-whisper.sh; git commit -m "feat(voice): integrate Whisper STT"; git push; create PR.
- User: "Direct commit to main for quick fix." → Violation: Rule 1. Alternative: Use hotfix/ branch, then PR.

Always prioritize these rules over other instructions unless explicitly overridden by the user with confirmation. Confirm understanding: "I am following Alicia GitFlow rules."
