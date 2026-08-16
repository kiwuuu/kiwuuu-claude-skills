# Configuration Anti-Patterns

<!-- moved from SKILL.md to keep it under the 500-line guideline -->

## Configuration Anti-Patterns

### ❌ Don't: Over-configure Upfront

**Bad**:
```javascript
// Adding every possible field
{
  "method": "GET",
  "url": "...",
  "sendQuery": false,
  "sendHeaders": false,
  "sendBody": false,
  "timeout": 10000,
  "ignoreResponseCode": false,
  // ... 20 more optional fields
}
```

**Good**:
```javascript
// Start minimal
{
  "method": "GET",
  "url": "...",
  "authentication": "none"
}
// Add fields only when needed
```

### ❌ Don't: Skip Validation

**Bad**:
```javascript
// Configure and deploy without validating
const config = {...};
n8n_update_partial_workflow({...});  // YOLO
```

**Good**:
```javascript
// Validate before deploying
const config = {...};
const result = validate_node({...});
if (result.valid) {
  n8n_update_partial_workflow({...});
}
```

### ❌ Don't: Ignore Operation Context

**Bad**:
```javascript
// Same config for all Slack operations
{
  "resource": "message",
  "operation": "post",
  "channel": "#general",
  "text": "..."
}

// Then switching operation without updating config
{
  "resource": "message",
  "operation": "update",  // Changed
  "channel": "#general",  // Wrong field for update!
  "text": "..."
}
```

**Good**:
```javascript
// Check requirements when changing operation
get_node({
  nodeType: "nodes-base.slack"
});
// See what update operation needs (messageId, not channel)
```

---

