# Match Semantics

Link code entities to concepts using embeddings and optional LLM validation.

## What This Does

Uses semantic similarity (sentence-transformers) to match:
- **Prompts → Concepts**: Which prompts demonstrate which learning concepts
- **Functions → Concepts**: Which code functions implement which concepts

Creates `DEMONSTRATES_CONCEPT` relationships for the knowledge graph.

## Run

```bash
cd tac-learning-system
python semantic/semantic_matcher.py
```

## Output

Saves to: `tac-learning-system/data/semantic/semantic_matches.json`

## Prerequisites

Must have run:
1. `/parse-prompts` - Prompt entities
2. `/parse-code` - Function entities
3. Concept extraction (from lesson transcripts)

## How It Works

### 1. Embedding Generation
Uses `all-MiniLM-L6-v2` model to create semantic embeddings for:
- Prompt content (name + sections + workflow steps)
- Function content (name + docstring + decorators)
- Concept definitions (name + definition)

### 2. Similarity Calculation
Computes cosine similarity between embeddings:
- **High confidence**: ≥ 0.5 similarity
- **Medium confidence**: 0.3 - 0.5 similarity
- **Low confidence**: < 0.3 (filtered out)

### 3. LLM Validation (Optional)
If `ANTHROPIC_API_KEY` is set:
- Sends top matches to Claude for validation
- Gets yes/no + explanation for each match
- Updates confidence levels

## Expected Results (tac-2)

- Prompt matches: ~2-3
- Function matches: 0-2 (functions are specific, concepts are abstract)
- Typical similarity: 0.3-0.4 (medium confidence)

## Example Output

```json
{
  "metadata": {
    "total_matches": 3,
    "validated_matches": 0,
    "high_confidence": 0,
    "filtered_matches": 2
  },
  "matches": [
    {
      "source_type": "prompt",
      "source_name": "List Built-in Tools",
      "concept_name": "Core Four",
      "similarity_score": 0.319,
      "confidence": "medium",
      "llm_validated": false,
      "llm_explanation": ""
    }
  ]
}
```

## Configuration

### Matching Thresholds

Edit `semantic_matcher.py` to adjust:

```python
# Prompt matching
threshold=0.25  # Minimum similarity score
top_k=3         # Top N concepts per prompt

# Confidence levels
if score >= 0.5: "high"
elif score >= 0.3: "medium"
else: "low"
```

### Enable LLM Validation

```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Then run matcher
python semantic/semantic_matcher.py
```

## Integration with Graph

After running semantic matching, rebuild the graph:

```bash
/build-graph
```

The graph will include new `DEMONSTRATES` edges:
- Prompt → Concept (red edges)
- Function → Concept (red edges)

## Performance

- **Embedding model loading**: ~2-3 seconds
- **Embedding generation**: ~0.5s per 10 entities
- **Similarity calculation**: <0.1s
- **LLM validation**: ~1-2s per 5 matches
- **Total**: ~5-10 seconds (without LLM), ~15-30s (with LLM)

## Tuning Tips

### Too Few Matches?
1. Lower threshold: `threshold=0.2`
2. Increase top_k: `top_k=5`
3. Adjust confidence levels to include more "low" confidence

### Too Many False Positives?
1. Raise threshold: `threshold=0.35`
2. Reduce top_k: `top_k=2`
3. Enable LLM validation
4. Only keep "high" confidence matches

### Improve Match Quality
1. Add more context to prompts (read full content, not just first 500 chars)
2. Use better embedding model: `all-mpnet-base-v2` (slower but more accurate)
3. Enable LLM validation for filtering

## Relationship Types

The semantic matcher creates:
- **DEMONSTRATES**: Code/Prompt → Concept
  - Example: `/prime` → "Context (Core Four)"
  - Example: `upload_file()` → "SDLC: Code"

## Limitations

- **Abstract matching**: TAC concepts are high-level, code is specific
- **Low similarity scores**: 0.3-0.4 is typical (not 0.8+)
- **False negatives**: Some valid matches may score below threshold
- **Context window**: Only uses first 300-500 chars of content

## Next Steps

After semantic matching:
1. `/build-graph` - Add DEMONSTRATES edges to graph
2. View `knowledge_graph.html` - See concept relationships
3. Query graph for learning insights

## Troubleshooting

**No matches found**: Lower threshold or check that concepts.json exists

**Model download fails**: Check internet connection, HuggingFace is accessible

**LLM validation skipped**: Set ANTHROPIC_API_KEY environment variable

**Import error**: `pip install sentence-transformers torch`
