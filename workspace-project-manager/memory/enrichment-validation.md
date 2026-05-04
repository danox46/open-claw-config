# Enrichment Validation Guide

## Issue Resolved
**Problem**: `enrich_task` succeeded but returned no usable enriched prompt or criteria  
**Root Cause**: The enrichment tool was executing without errors but not producing structured output in the expected format  
**Solution**: Created standalone valid-enriched-task.json with properly structured task object

## Validation Process

### 1. Check JSON Structure
The enriched task must contain the following required fields:
- `localId`: Unique task identifier (e.g., "task-1")
- `intent`: Task intent type (e.g., "generate_scaffold", "implement_feature")
- `target`: Target agent object (e.g., `{ "agentId": "implementer" }`)
- `inputs`: Object containing:
  - `prompt`: Detailed task instructions
  - `testingCriteria`: Array of verification points
  - `acceptanceCriteria`: Array of completion conditions
- `dependsOn`: Array of dependency localIds

### 2. Validate Required Fields
```json
{
  "required": [
    "localId",
    "intent", 
    "target",
    "inputs",
    "inputs.prompt",
    "inputs.testingCriteria",
    "inputs.acceptanceCriteria",
    "dependsOn"
  ]
}
```

### 3. Validate Array Types
- `inputs.testingCriteria` must be a non-empty array of strings
- `inputs.acceptanceCriteria` must be a non-empty array of strings
- `dependsOn` must be an array of strings (localIds)

### 4. Validate Prompt Content
The `inputs.prompt` must contain:
- Clear, actionable instructions
- Step-by-step procedures
- Specific file paths and commands
- Error handling patterns
- Project context

### 5. Validate Criteria Content
Each criterion must be:
- Specific and measurable
- Testable by QA
- Observable and verifiable
- Not subjective or vague

## Files Location

1. **valid-enriched-task.json** (`/home/danox/.openclaw/workspace-shared/Test Internal App/.openclaw/`)
   - Standalone validated task structure
   - Can be used directly by implementer agent
   - Properly formatted with all required fields

2. **ENRICHED_TASKS.json** (`/home/danox/.openclaw/workspace-shared/Test Internal App/.openclaw/`)
   - Contains multiple enriched tasks
   - Follows same structure as valid-enriched-task.json
   - Can be parsed and validated

3. **enriched-task-*.md** (`/home/danox/.openclaw/workspace-project-manager/memory/`)
   - Markdown documentation of enriched tasks
   - Contains full context and error handling patterns
   - Reference for implementer agent

## Usage

### For Implementer Agent
1. Read `valid-enriched-task.json`
2. Extract the task object from `tasks[0]`
3. Use `inputs.prompt` for execution instructions
4. Verify against `inputs.testingCriteria`
5. Confirm completion against `inputs.acceptanceCriteria`

### For Project Manager
1. Validate enriched task structure using validation rules
2. Ensure all required fields are present
3. Check that criteria are specific and measurable
4. Review prompt for clarity and completeness
5. Assign to implementer agent once validated

## Error Handling

If `enrich_task` returns no usable output:
1. Check if the output contains all required fields
2. Verify that `inputs.prompt` is not empty
3. Ensure `inputs.testingCriteria` is an array with items
4. Confirm `inputs.acceptanceCriteria` is an array with items
5. If validation fails, regenerate the enriched task

## Success Criteria

✅ Enriched task contains all required fields  
✅ `inputs.prompt` is detailed and actionable  
✅ `inputs.testingCriteria` has at least 10 items  
✅ `inputs.acceptanceCriteria` has at least 8 items  
✅ `dependsOn` correctly references task dependencies  
✅ All criteria are specific and measurable  
✅ Prompt includes error handling patterns  
✅ Prompt includes project context  

---

**Status**: Validation guide COMPLETE  
**Date**: 2025-01-XX  
**Project**: Test Internal App  
**Phase**: Test Infrastructure and Configuration  
**Issue Fixed**: enrich_task returned no usable output
