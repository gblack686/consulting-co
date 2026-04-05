"""
Semantic matcher for linking prompts/code to concepts using embeddings and LLM annotation.

Uses:
- sentence-transformers for embedding generation
- cosine similarity for matching
- Anthropic Claude for validation and enrichment
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer, util
from anthropic import Anthropic


@dataclass
class SemanticMatch:
    """Represents a semantic match between code and concept"""
    source_type: str  # prompt, function, class, etc.
    source_name: str
    source_content: str
    concept_name: str
    concept_definition: str
    similarity_score: float
    llm_validated: bool = False
    llm_explanation: str = ""
    confidence: str = "low"  # low, medium, high


class SemanticMatcher:
    """Match code entities to concepts using embeddings and LLM"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize semantic matcher.

        Args:
            model_name: HuggingFace model for embeddings (default: fast, lightweight)
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)

        # Initialize Anthropic client if API key available
        self.anthropic_client = None
        if os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        else:
            print("⚠️  ANTHROPIC_API_KEY not found - LLM validation disabled")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        return self.model.encode(texts, convert_to_tensor=False)

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        similarity = util.cos_sim(embedding1, embedding2)
        return float(similarity[0][0])

    def match_prompts_to_concepts(
        self,
        prompts: List[Dict[str, Any]],
        concepts: List[Dict[str, Any]],
        top_k: int = 3,
        threshold: float = 0.25
    ) -> List[SemanticMatch]:
        """
        Match prompts to concepts based on semantic similarity.

        Args:
            prompts: List of prompt entities
            concepts: List of concept entities
            top_k: Number of top matches per prompt
            threshold: Minimum similarity score (0-1)

        Returns:
            List of semantic matches
        """
        matches = []

        # Prepare prompt texts (use content + sections)
        prompt_texts = []
        for prompt in prompts:
            text = f"{prompt['name']}\n"
            text += prompt.get('content', '')[:500]  # First 500 chars
            # Add section context
            for section_name, section_content in prompt.get('sections', {}).items():
                text += f"\n{section_name}: {section_content[:200]}"
            prompt_texts.append(text)

        # Prepare concept texts (use name + definition)
        concept_texts = []
        for concept in concepts:
            text = f"{concept['name']}: {concept.get('definition', '')}"
            concept_texts.append(text)

        print(f"Embedding {len(prompt_texts)} prompts...")
        prompt_embeddings = self.embed_texts(prompt_texts)

        print(f"Embedding {len(concept_texts)} concepts...")
        concept_embeddings = self.embed_texts(concept_texts)

        print(f"Calculating similarity scores...")
        # For each prompt, find top-k matching concepts
        for i, prompt in enumerate(prompts):
            prompt_emb = prompt_embeddings[i]

            # Calculate similarity to all concepts
            similarities = []
            for j, concept in enumerate(concepts):
                concept_emb = concept_embeddings[j]
                score = self.calculate_similarity(prompt_emb, concept_emb)
                similarities.append((score, concept, j))

            # Sort by similarity (descending)
            similarities.sort(reverse=True, key=lambda x: x[0])

            # Take top-k matches above threshold
            for score, concept, _ in similarities[:top_k]:
                if score >= threshold:
                    match = SemanticMatch(
                        source_type='prompt',
                        source_name=prompt['name'],
                        source_content=prompt_texts[i][:300],
                        concept_name=concept['name'],
                        concept_definition=concept.get('definition', ''),
                        similarity_score=round(score, 3),
                        confidence=self._score_to_confidence(score)
                    )
                    matches.append(match)

        print(f"✅ Found {len(matches)} semantic matches")
        return matches

    def match_functions_to_concepts(
        self,
        functions: List[Dict[str, Any]],
        concepts: List[Dict[str, Any]],
        top_k: int = 2,
        threshold: float = 0.35
    ) -> List[SemanticMatch]:
        """
        Match code functions to concepts.

        Args:
            functions: List of function entities from code_entities.json
            concepts: List of concept entities
            top_k: Number of top matches per function
            threshold: Minimum similarity score

        Returns:
            List of semantic matches
        """
        matches = []

        # Prepare function texts (name + docstring + decorators)
        function_texts = []
        for func in functions:
            text = f"{func['name']}\n"
            if func.get('docstring'):
                text += func['docstring']
            if func.get('decorators'):
                text += f"\nDecorators: {', '.join(func['decorators'])}"
            function_texts.append(text)

        # Prepare concept texts
        concept_texts = [f"{c['name']}: {c.get('definition', '')}" for c in concepts]

        print(f"Embedding {len(function_texts)} functions...")
        function_embeddings = self.embed_texts(function_texts)

        print(f"Embedding {len(concept_texts)} concepts...")
        concept_embeddings = self.embed_texts(concept_texts)

        print(f"Calculating similarity scores...")
        # For each function, find top-k matching concepts
        for i, func in enumerate(functions):
            func_emb = function_embeddings[i]

            similarities = []
            for j, concept in enumerate(concepts):
                concept_emb = concept_embeddings[j]
                score = self.calculate_similarity(func_emb, concept_emb)
                similarities.append((score, concept, j))

            similarities.sort(reverse=True, key=lambda x: x[0])

            for score, concept, _ in similarities[:top_k]:
                if score >= threshold:
                    match = SemanticMatch(
                        source_type='function',
                        source_name=func['name'],
                        source_content=function_texts[i][:300],
                        concept_name=concept['name'],
                        concept_definition=concept.get('definition', ''),
                        similarity_score=round(score, 3),
                        confidence=self._score_to_confidence(score)
                    )
                    matches.append(match)

        print(f"✅ Found {len(matches)} function-concept matches")
        return matches

    def validate_with_llm(self, matches: List[SemanticMatch], batch_size: int = 5) -> List[SemanticMatch]:
        """
        Validate matches using Claude API.

        Args:
            matches: List of semantic matches to validate
            batch_size: Number of matches to validate per API call

        Returns:
            Matches with LLM validation and explanations
        """
        if not self.anthropic_client:
            print("⚠️  Skipping LLM validation (no API key)")
            return matches

        print(f"Validating {len(matches)} matches with Claude...")

        # Process in batches
        validated_matches = []
        for i in range(0, len(matches), batch_size):
            batch = matches[i:i+batch_size]

            # Build prompt for validation
            prompt = self._build_validation_prompt(batch)

            try:
                response = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                # Parse response and update matches
                result_text = response.content[0].text
                validated_batch = self._parse_validation_response(batch, result_text)
                validated_matches.extend(validated_batch)

            except Exception as e:
                print(f"⚠️  LLM validation error: {e}")
                # Return unvalidated matches
                validated_matches.extend(batch)

        validated_count = sum(1 for m in validated_matches if m.llm_validated)
        print(f"✅ LLM validated {validated_count}/{len(matches)} matches")

        return validated_matches

    def _build_validation_prompt(self, matches: List[SemanticMatch]) -> str:
        """Build prompt for LLM validation"""
        prompt = """You are validating semantic matches between code entities and learning concepts.

For each match below, determine:
1. Is the match valid? (yes/no)
2. Brief explanation (1 sentence)
3. Confidence level (high/medium/low)

Format your response as JSON array:
[
  {"match_id": 0, "valid": true, "explanation": "...", "confidence": "high"},
  {"match_id": 1, "valid": false, "explanation": "...", "confidence": "low"},
  ...
]

Matches to validate:

"""
        for i, match in enumerate(matches):
            prompt += f"\nMatch {i}:\n"
            prompt += f"Source: {match.source_type} '{match.source_name}'\n"
            prompt += f"Content: {match.source_content[:200]}...\n"
            prompt += f"Concept: {match.concept_name}\n"
            prompt += f"Definition: {match.concept_definition}\n"
            prompt += f"Similarity Score: {match.similarity_score}\n"
            prompt += "-" * 60 + "\n"

        return prompt

    def _parse_validation_response(
        self,
        matches: List[SemanticMatch],
        response_text: str
    ) -> List[SemanticMatch]:
        """Parse LLM validation response and update matches"""
        try:
            # Extract JSON from response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start == -1 or end == 0:
                print("⚠️  Could not parse LLM response")
                return matches

            json_text = response_text[start:end]
            validations = json.loads(json_text)

            # Update matches with validation results
            for validation in validations:
                match_id = validation.get('match_id', -1)
                if 0 <= match_id < len(matches):
                    match = matches[match_id]
                    match.llm_validated = validation.get('valid', False)
                    match.llm_explanation = validation.get('explanation', '')
                    match.confidence = validation.get('confidence', match.confidence)

            return matches

        except Exception as e:
            print(f"⚠️  Error parsing validation: {e}")
            return matches

    def _score_to_confidence(self, score: float) -> str:
        """Convert similarity score to confidence level"""
        if score >= 0.5:
            return 'high'
        elif score >= 0.3:
            return 'medium'
        else:
            return 'low'


def match_all_entities(data_dir: Path, output_dir: Path, use_llm: bool = True) -> Dict[str, Any]:
    """
    Run semantic matching on all entities.

    Args:
        data_dir: Directory with extracted entities
        output_dir: Where to save matches
        use_llm: Whether to use LLM validation

    Returns:
        Dictionary with all matches
    """
    matcher = SemanticMatcher()

    # Load prompts
    prompts_file = data_dir / "tac-2" / "prompts.json"
    prompts = json.loads(prompts_file.read_text()) if prompts_file.exists() else []

    # Load code entities
    code_file = data_dir / "tac-2" / "code_entities.json"
    code_data = json.loads(code_file.read_text()) if code_file.exists() else {}

    # Load concepts
    concepts_file = data_dir / "lesson-2" / "concepts.json"
    concepts_data = json.loads(concepts_file.read_text()) if concepts_file.exists() else {}
    concepts = concepts_data.get('concepts', [])

    print(f"Loaded {len(prompts)} prompts, {len(concepts)} concepts")

    all_matches = []

    # Match prompts to concepts
    if prompts and concepts:
        print("\n🔍 Matching prompts to concepts...")
        prompt_matches = matcher.match_prompts_to_concepts(prompts, concepts)
        all_matches.extend(prompt_matches)

    # Match functions to concepts
    if code_data.get('modules') and concepts:
        print("\n🔍 Matching functions to concepts...")
        # Extract all functions from modules
        functions = []
        for module in code_data['modules']:
            for func in module.get('functions', []):
                func['module'] = module['name']
                functions.append(func)

        if functions:
            function_matches = matcher.match_functions_to_concepts(functions, concepts)
            all_matches.extend(function_matches)

    # LLM validation (optional)
    if use_llm and all_matches:
        print("\n🤖 Running LLM validation...")
        all_matches = matcher.validate_with_llm(all_matches)

    # Filter to validated OR medium+ confidence matches
    # (keep all if no LLM validation was done)
    if use_llm and any(m.llm_validated for m in all_matches):
        filtered_matches = [
            m for m in all_matches
            if m.llm_validated or m.confidence in ['high', 'medium']
        ]
    else:
        # No LLM validation - keep medium+ confidence
        filtered_matches = [
            m for m in all_matches
            if m.confidence in ['high', 'medium']
        ]

    # Convert to serializable format
    matches_data = {
        "metadata": {
            "total_matches": len(all_matches),
            "validated_matches": sum(1 for m in all_matches if m.llm_validated),
            "high_confidence": sum(1 for m in all_matches if m.confidence == 'high'),
            "filtered_matches": len(filtered_matches)
        },
        "matches": [
            {
                "source_type": m.source_type,
                "source_name": m.source_name,
                "concept_name": m.concept_name,
                "similarity_score": m.similarity_score,
                "confidence": m.confidence,
                "llm_validated": m.llm_validated,
                "llm_explanation": m.llm_explanation
            }
            for m in filtered_matches
        ]
    }

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "semantic_matches.json"
    output_file.write_text(json.dumps(matches_data, indent=2))

    print(f"\n✅ Semantic matching complete!")
    print(f"✅ Total matches: {len(all_matches)}")
    print(f"✅ Validated matches: {matches_data['metadata']['validated_matches']}")
    print(f"✅ High confidence: {matches_data['metadata']['high_confidence']}")
    print(f"✅ Saved to: {output_file}")

    return matches_data


if __name__ == "__main__":
    # Run semantic matching
    data_dir = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data")
    output_dir = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data\semantic")

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n⚠️  Set ANTHROPIC_API_KEY environment variable to enable LLM validation")
        print("Running without LLM validation...\n")

    matches = match_all_entities(data_dir, output_dir, use_llm=True)

    # Print summary
    print("\n" + "="*60)
    print("SEMANTIC MATCHING SUMMARY")
    print("="*60)

    if matches['matches']:
        print("\nTop Matches:")
        for match in matches['matches'][:10]:
            print(f"\n  {match['source_type'].upper()}: {match['source_name']}")
            print(f"  → Concept: {match['concept_name']}")
            print(f"  Similarity: {match['similarity_score']} ({match['confidence']} confidence)")
            if match['llm_validated']:
                print(f"  ✓ Validated: {match['llm_explanation']}")
