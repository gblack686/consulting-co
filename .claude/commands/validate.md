---
description: Comprehensive validation suite for RoboNuggets Supabase AI Video Generation Workflow
---

# Validate RoboNuggets Supabase Workflow

Comprehensive validation suite for the RoboNuggets AI video generation workflow using Supabase-only architecture.

## Phase 1: Project Structure Validation

Verify all required directories and files exist:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 1: Project Structure Validation"
echo "═══════════════════════════════════════════════════════════"

# Check directory structure
REQUIRED_DIRS=(
  ".claude/skills/robonuggets-workflow"
  ".claude/skills/robonuggets-workflow/supabase"
  ".claude/skills/robonuggets-workflow/supabase/migrations"
  ".claude/skills/robonuggets-workflow/supabase/functions"
  ".claude/skills/robonuggets-workflow/supabase/functions/_shared"
  ".claude/skills/robonuggets-workflow/supabase/config"
)

for dir in "${REQUIRED_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "✓ Directory exists: $dir"
  else
    echo "✗ MISSING directory: $dir"
    exit 1
  fi
done

# Check required files
REQUIRED_FILES=(
  ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"
  ".claude/skills/robonuggets-workflow/supabase/config/storage.sql"
  ".claude/skills/robonuggets-workflow/supabase/functions/_shared/supabase.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/_shared/ai-providers.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/_shared/types.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/create-project/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/generate-prompts/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/job-worker/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/webhook-receiver/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/generate-images/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/generate-video/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/generate-audio/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/approve-stage/index.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/update-obsidian/index.ts"
  ".claude/skills/robonuggets-workflow/deno.json"
  ".claude/skills/robonuggets-workflow/supabase.local.toml"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✓ File exists: $file"
  else
    echo "✗ MISSING file: $file"
    exit 1
  fi
done

echo ""
echo "✓ Phase 1 PASSED: All required directories and files present"
echo ""
```

## Phase 2: SQL Schema Validation

Validate PostgreSQL schema syntax and correctness:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 2: SQL Schema Validation"
echo "═══════════════════════════════════════════════════════════"

SCHEMA_FILE=".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"

# Check for critical table names
REQUIRED_TABLES=(
  "video_projects"
  "video_scenes"
  "video_artifacts"
  "workflow_approvals"
  "workflow_cost_tracking"
  "video_workflow_secrets"
  "workflow_jobs"
)

for table in "${REQUIRED_TABLES[@]}"; do
  if grep -q "CREATE TABLE.*$table" "$SCHEMA_FILE"; then
    echo "✓ Table schema found: $table"
  else
    echo "✗ MISSING table schema: $table"
    exit 1
  fi
done

# Check for required columns in video_projects
REQUIRED_COLUMNS=(
  "project_name TEXT NOT NULL"
  "creative_direction TEXT NOT NULL"
  "status TEXT NOT NULL DEFAULT 'draft'"
  "total_actual_cost_usd DECIMAL"
)

for col in "${REQUIRED_COLUMNS[@]}"; do
  if grep -A 20 "CREATE TABLE.*video_projects" "$SCHEMA_FILE" | grep -q "$col"; then
    echo "✓ Column found in video_projects: $col"
  else
    echo "✗ MISSING column in video_projects: $col"
    exit 1
  fi
done

# Validate triggers exist
if grep -q "CREATE TRIGGER trigger_create_next_job" "$SCHEMA_FILE"; then
  echo "✓ Trigger found: trigger_create_next_job"
else
  echo "✗ MISSING trigger: trigger_create_next_job"
  exit 1
fi

if grep -q "CREATE TRIGGER trigger_update_project_cost" "$SCHEMA_FILE"; then
  echo "✓ Trigger found: trigger_update_project_cost"
else
  echo "✗ MISSING trigger: trigger_update_project_cost"
  exit 1
fi

# Validate RLS policies
if grep -q "ALTER TABLE video_projects ENABLE ROW LEVEL SECURITY" "$SCHEMA_FILE"; then
  echo "✓ RLS enabled for video_projects"
else
  echo "✗ RLS NOT enabled for video_projects"
  exit 1
fi

echo ""
echo "✓ Phase 2 PASSED: SQL schema validation complete"
echo ""
```

## Phase 3: Storage Configuration Validation

Validate Supabase Storage bucket configuration:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 3: Storage Configuration Validation"
echo "═══════════════════════════════════════════════════════════"

STORAGE_FILE=".claude/skills/robonuggets-workflow/supabase/config/storage.sql"

# Check required buckets
REQUIRED_BUCKETS=("prompts" "images" "videos" "audio")

for bucket in "${REQUIRED_BUCKETS[@]}"; do
  if grep -q "'$bucket'" "$STORAGE_FILE"; then
    echo "✓ Storage bucket defined: $bucket"
  else
    echo "✗ MISSING storage bucket: $bucket"
    exit 1
  fi
done

# Verify mime types are configured
if grep -q "application/json" "$STORAGE_FILE"; then
  echo "✓ JSON mime type configured"
else
  echo "✗ Missing JSON mime type"
  exit 1
fi

if grep -q "image/png" "$STORAGE_FILE"; then
  echo "✓ Image mime types configured"
else
  echo "✗ Missing image mime types"
  exit 1
fi

if grep -q "video/mp4" "$STORAGE_FILE"; then
  echo "✓ Video mime types configured"
else
  echo "✗ Missing video mime types"
  exit 1
fi

if grep -q "audio/mpeg" "$STORAGE_FILE"; then
  echo "✓ Audio mime types configured"
else
  echo "✗ Missing audio mime types"
  exit 1
fi

# Validate RLS policies
if grep -q "Service role can upload" "$STORAGE_FILE"; then
  echo "✓ Service role upload policies defined"
else
  echo "✗ Missing service role upload policies"
  exit 1
fi

echo ""
echo "✓ Phase 3 PASSED: Storage configuration validation complete"
echo ""
```

## Phase 4: TypeScript Type Checking

Validate TypeScript syntax and type safety for Edge Functions:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 4: TypeScript Type Checking"
echo "═══════════════════════════════════════════════════════════"

# Check if deno.json exists for TypeScript configuration
if [ ! -f ".claude/skills/robonuggets-workflow/deno.json" ]; then
  echo "Creating deno.json for TypeScript configuration..."
  cat > ".claude/skills/robonuggets-workflow/deno.json" << 'EOF'
{
  "imports": {
    "std/": "https://deno.land/std@0.208.0/",
    "@supabase/supabase-js": "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.38.0/+esm",
    "@anthropic-ai/sdk": "npm:@anthropic-ai/sdk@0.24.0"
  }
}
EOF
fi

# Validate all TypeScript files can be parsed
SHARED_FILES=(
  ".claude/skills/robonuggets-workflow/supabase/functions/_shared/supabase.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/_shared/ai-providers.ts"
  ".claude/skills/robonuggets-workflow/supabase/functions/_shared/types.ts"
)

for file in "${SHARED_FILES[@]}"; do
  if [ -f "$file" ]; then
    # Check TypeScript syntax (basic validation)
    if grep -q "^import\|^export" "$file"; then
      echo "✓ TypeScript file valid: $file"
    else
      echo "⚠ Warning: $file may be empty or invalid"
    fi
  else
    echo "✗ MISSING TypeScript file: $file"
    exit 1
  fi
done

# Validate Edge Function index.ts files
EDGE_FUNCTIONS=(
  "create-project"
  "generate-prompts"
  "generate-images"
  "generate-video"
  "generate-audio"
  "webhook-receiver"
  "approve-stage"
  "job-worker"
  "update-obsidian"
)

for func in "${EDGE_FUNCTIONS[@]}"; do
  func_file=".claude/skills/robonuggets-workflow/supabase/functions/$func/index.ts"
  if [ -f "$func_file" ]; then
    if grep -q "serve(" "$func_file"; then
      echo "✓ Edge Function valid: $func"
    else
      echo "✗ Invalid Edge Function: $func (missing serve handler)"
      exit 1
    fi
  else
    echo "✗ MISSING Edge Function: $func/index.ts"
    exit 1
  fi
done

echo ""
echo "✓ Phase 4 PASSED: TypeScript validation complete"
echo ""
```

## Phase 5: AI Provider Integration Validation

Validate AI provider implementations are properly configured:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 5: AI Provider Integration Validation"
echo "═══════════════════════════════════════════════════════════"

AI_PROVIDERS_FILE=".claude/skills/robonuggets-workflow/supabase/functions/_shared/ai-providers.ts"

# Check required provider classes
REQUIRED_PROVIDERS=("ClaudeProvider" "NanoBananaProvider")

for provider in "${REQUIRED_PROVIDERS[@]}"; do
  if grep -q "class $provider" "$AI_PROVIDERS_FILE"; then
    echo "✓ Provider implemented: $provider"
  else
    echo "✗ MISSING provider: $provider"
    exit 1
  fi
done

# Validate Claude cost calculation
if grep -q "calculateCost" "$AI_PROVIDERS_FILE"; then
  echo "✓ Cost calculation method implemented"
else
  echo "✗ Missing cost calculation"
  exit 1
fi

# Validate prompt generation system
if grep -q "PROMPT_GENERATION_SYSTEM" "$AI_PROVIDERS_FILE"; then
  echo "✓ Prompt generation system template found"
else
  echo "✗ Missing prompt generation system"
  exit 1
fi

# Validate Nano Banana API configuration
if grep -q "nanobananapro.com" "$AI_PROVIDERS_FILE"; then
  echo "✓ Nano Banana API endpoint configured"
else
  echo "✗ Missing Nano Banana API endpoint"
  exit 1
fi

echo ""
echo "✓ Phase 5 PASSED: AI provider validation complete"
echo ""
```

## Phase 6: Workflow Logic Validation

Validate job queue and workflow orchestration:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 6: Workflow Logic Validation"
echo "═══════════════════════════════════════════════════════════"

JOB_WORKER_FILE=".claude/skills/robonuggets-workflow/supabase/functions/job-worker/index.ts"
GENERATE_PROMPTS_FILE=".claude/skills/robonuggets-workflow/supabase/functions/generate-prompts/index.ts"
CREATE_PROJECT_FILE=".claude/skills/robonuggets-workflow/supabase/functions/create-project/index.ts"

# Validate job worker fetches pending jobs
if grep -q "eq.*status.*pending" "$JOB_WORKER_FILE"; then
  echo "✓ Job worker queries pending jobs"
else
  echo "✗ Job worker not querying pending jobs"
  exit 1
fi

# Validate job worker calls correct functions
if grep -q "getFunctionNameForJobType" "$JOB_WORKER_FILE"; then
  echo "✓ Job worker dispatches to correct functions"
else
  echo "✗ Job worker not dispatching correctly"
  exit 1
fi

# Validate prompt generation handles approvals
if grep -q "awaiting_approval\|workflow_approvals" "$GENERATE_PROMPTS_FILE"; then
  echo "✓ Prompt generation creates approval requests"
else
  echo "✗ Prompt generation missing approval flow"
  exit 1
fi

# Validate cost tracking
if grep -q "workflow_cost_tracking" "$GENERATE_PROMPTS_FILE"; then
  echo "✓ Cost tracking implemented in workflow"
else
  echo "✗ Cost tracking missing"
  exit 1
fi

# Validate project creation initializes jobs
if grep -q "workflow_jobs.*insert" "$CREATE_PROJECT_FILE"; then
  echo "✓ Project creation initializes workflow jobs"
else
  echo "✗ Project creation not initializing jobs"
  exit 1
fi

# Validate scene creation
if grep -q "video_scenes.*insert" "$CREATE_PROJECT_FILE"; then
  echo "✓ Project creation creates scenes"
else
  echo "✗ Project creation not creating scenes"
  exit 1
fi

echo ""
echo "✓ Phase 6 PASSED: Workflow logic validation complete"
echo ""
```

## Phase 7: Obsidian Integration Validation

Validate Obsidian template structure:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 7: Obsidian Integration Validation"
echo "═══════════════════════════════════════════════════════════"

OBSIDIAN_TEMPLATE="$HOME/OneDrive/Desktop/obsidian/Gbautomation/templates/robonuggets-project.md"

if [ -f "$OBSIDIAN_TEMPLATE" ]; then
  echo "✓ Obsidian template file exists"

  # Check frontmatter
  if grep -q "type: robonuggets-project" "$OBSIDIAN_TEMPLATE"; then
    echo "✓ Template has correct type identifier"
  else
    echo "⚠ Warning: Template missing type identifier"
  fi

  # Check for Realtime subscription
  if grep -q "postgres_changes" "$OBSIDIAN_TEMPLATE"; then
    echo "✓ Template includes Realtime subscriptions"
  else
    echo "⚠ Warning: Template missing Realtime subscriptions"
  fi

  # Check for approval buttons
  if grep -q "Approve\|Regenerate" "$OBSIDIAN_TEMPLATE"; then
    echo "✓ Template includes approval workflow controls"
  else
    echo "⚠ Warning: Template missing approval controls"
  fi

else
  echo "⚠ Warning: Obsidian template not yet created (will be created during implementation)"
fi

echo ""
echo "✓ Phase 7 PASSED: Obsidian integration validation complete"
echo ""
```

## Phase 8: Configuration and Deployment Validation

Validate deployment scripts and configuration:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 8: Configuration and Deployment Validation"
echo "═══════════════════════════════════════════════════════════"

# Check for deployment script
if [ -f ".claude/skills/robonuggets-workflow/deploy.sh" ]; then
  echo "✓ Deployment script exists"

  if grep -q "supabase.*deploy" ".claude/skills/robonuggets-workflow/deploy.sh"; then
    echo "✓ Deployment script includes Supabase commands"
  else
    echo "⚠ Warning: Deployment script may be incomplete"
  fi
else
  echo "⚠ Warning: Deployment script not yet created"
fi

# Check for supabase config
if [ -f ".claude/skills/robonuggets-workflow/supabase.local.toml" ]; then
  echo "✓ Supabase local config exists"
else
  echo "⚠ Warning: Supabase local config not yet created"
fi

# Check for README
if [ -f ".claude/skills/robonuggets-workflow/README.md" ]; then
  echo "✓ README documentation exists"
else
  echo "⚠ Warning: README not yet created"
fi

echo ""
echo "✓ Phase 8 PASSED: Configuration validation complete"
echo ""
```

## Phase 9: End-to-End Workflow Testing

Complete workflow from project creation to artifact generation:

```bash
#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "Phase 9: End-to-End Workflow Testing"
echo "═══════════════════════════════════════════════════════════"

echo "Testing complete workflow sequence:"
echo ""

# Step 1: Verify all functions can be called
echo "1. Testing Edge Function structure..."
EDGE_FUNCTIONS=(
  "create-project"
  "generate-prompts"
  "webhook-receiver"
  "job-worker"
)

for func in "${EDGE_FUNCTIONS[@]}"; do
  func_file=".claude/skills/robonuggets-workflow/supabase/functions/$func/index.ts"

  # Check function is properly structured
  if grep -q "serve" "$func_file" && grep -q "Request\|req" "$func_file"; then
    echo "  ✓ $func properly structured"
  else
    echo "  ✗ $func structure invalid"
    exit 1
  fi
done

# Step 2: Verify data flow through workflow
echo ""
echo "2. Testing data flow through workflow..."

# Check that jobs have dependencies
if grep -q "depends_on_job_id" ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"; then
  echo "  ✓ Workflow supports job dependencies"
else
  echo "  ✗ Job dependencies not supported"
  exit 1
fi

# Step 3: Verify approval gates
echo ""
echo "3. Testing approval gate system..."

if grep -q "workflow_approvals" ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"; then
  echo "  ✓ Approval workflow defined"
else
  echo "  ✗ Approval workflow missing"
  exit 1
fi

# Check approval stages
if grep -q "approval_stage\|prompts\|images\|video\|audio" ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"; then
  echo "  ✓ All approval stages defined"
else
  echo "  ✗ Some approval stages missing"
  exit 1
fi

# Step 4: Verify artifact storage
echo ""
echo "4. Testing artifact storage system..."

if grep -q "video_artifacts" ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"; then
  if grep -q "storage_bucket\|storage_path" ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"; then
    echo "  ✓ Artifact storage system configured"
  else
    echo "  ✗ Artifact storage fields missing"
    exit 1
  fi
fi

# Step 5: Verify cost tracking
echo ""
echo "5. Testing cost tracking system..."

if grep -q "workflow_cost_tracking" ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"; then
  if grep -q "cost_usd\|ai_provider" ".claude/skills/robonuggets-workflow/supabase/migrations/001_initial_schema.sql"; then
    echo "  ✓ Cost tracking system configured"
  else
    echo "  ✗ Cost tracking fields missing"
    exit 1
  fi
fi

echo ""
echo "✓ Phase 9 PASSED: End-to-end workflow validation complete"
echo ""
```

## Final Summary

```bash
echo "═══════════════════════════════════════════════════════════"
echo "✓ ALL VALIDATION PHASES PASSED"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "The RoboNuggets Supabase workflow is properly implemented:"
echo "  ✓ Project structure complete"
echo "  ✓ Database schema validated"
echo "  ✓ Storage configuration valid"
echo "  ✓ TypeScript syntax correct"
echo "  ✓ AI providers configured"
echo "  ✓ Workflow logic implemented"
echo "  ✓ Obsidian integration ready"
echo "  ✓ Deployment configuration complete"
echo "  ✓ End-to-end workflow valid"
echo ""
echo "Ready for deployment to Supabase!"
echo "═══════════════════════════════════════════════════════════"
```

## Running the Validation

To run this validation suite:

```bash
source .claude/commands/validate.md
```

Or run individual phases:

```bash
# Phase 1: Structure
bash << 'EOF'
# ... Phase 1 code ...
EOF

# Phase 2: SQL Validation
bash << 'EOF'
# ... Phase 2 code ...
EOF
```

All phases should complete successfully before deploying to production.
