"""
Advanced hallucination detection for agentic AI systems.

This module provides comprehensive hallucination detection using multiple approaches:
- Factual consistency checking
- Knowledge base validation  
- Semantic coherence analysis
- Cross-reference verification
- Confidence scoring
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ..core.types import EvaluationResult, TestCase
from ..utils.config import Config


class HallucinationDetector:
    """
    Multi-modal hallucination detection system for AI agent responses.
    
    Uses various techniques to identify when an AI agent generates
    false, inconsistent, or fabricated information.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the hallucination detector."""
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Load semantic similarity model
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.warning(f"Failed to load sentence transformer: {e}")
            self.sentence_model = None
        
        # Knowledge base patterns for hospitality domain
        self.hotel_knowledge_patterns = {
            "room_types": {
                "standard", "deluxe", "suite", "presidential", "executive", 
                "junior_suite", "penthouse", "villa", "cottage"
            },
            "amenities": {
                "wifi", "spa", "pool", "gym", "restaurant", "bar", "concierge",
                "valet", "room_service", "business_center", "conference_room"
            },
            "departments": {
                "front_desk", "housekeeping", "maintenance", "security", 
                "food_beverage", "spa", "concierge", "management"
            },
            "systems": {
                "pms", "pos", "key_card", "security", "fire_safety",
                "hvac", "lighting", "network", "payment_gateway"
            }
        }
        
        # Common hallucination patterns
        self.hallucination_indicators = [
            # Overly specific without context
            r'\b\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\b',  # Specific timestamps
            r'\b\d+\.\d{2}\%\b',  # Precise percentages
            r'\bticket\s*#?\d{6,}\b',  # Specific ticket numbers
            r'\bcase\s*#?\d{6,}\b',  # Specific case numbers
            
            # Fabricated technical details
            r'\bversion\s+\d+\.\d+\.\d+\b',  # Software versions
            r'\bIP\s+\d+\.\d+\.\d+\.\d+\b',  # Specific IP addresses
            r'\bport\s+\d{4,5}\b',  # Network ports
            
            # Absolute statements without evidence
            r'\balways\s+(?:results?|causes?|leads?)\b',
            r'\bnever\s+(?:happens?|occurs?|results?)\b',
            r'\bguaranteed?\s+to\b',
            r'\b100%\s+(?:certain|sure|accurate)\b',
        ]
        
        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                for pattern in self.hallucination_indicators]
    
    def detect_hallucinations(
        self,
        test_case: TestCase,
        actual_output: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive hallucination detection for a single test case.
        
        Args:
            test_case: The test case with input and expected output
            actual_output: The agent's actual response
            metadata: Additional context from the execution
            
        Returns:
            Dictionary with hallucination analysis results
        """
        metadata = metadata or {}
        
        # Extract text from response
        response_text = self._extract_response_text(actual_output)
        input_text = self._extract_input_text(test_case.input_data)
        expected_text = self._extract_response_text(test_case.expected_output)
        
        hallucination_results = {
            "overall_score": 0.0,
            "confidence": 0.0,
            "detected_issues": [],
            "analysis": {},
        }
        
        # Run multiple detection methods
        analyses = []
        
        # 1. Factual consistency check
        factual_analysis = self._check_factual_consistency(
            input_text, response_text, expected_text
        )
        analyses.append(("factual_consistency", factual_analysis))
        
        # 2. Knowledge base validation
        knowledge_analysis = self._validate_against_knowledge_base(
            response_text, test_case.task_type.value
        )
        analyses.append(("knowledge_validation", knowledge_analysis))
        
        # 3. Fabrication detection
        fabrication_analysis = self._detect_fabricated_content(
            input_text, response_text
        )
        analyses.append(("fabrication_detection", fabrication_analysis))
        
        # 4. Logical consistency check
        logical_analysis = self._check_logical_consistency(response_text)
        analyses.append(("logical_consistency", logical_analysis))
        
        # 5. Semantic coherence analysis
        if self.sentence_model:
            coherence_analysis = self._analyze_semantic_coherence(
                input_text, response_text, expected_text
            )
            analyses.append(("semantic_coherence", coherence_analysis))
        
        # 6. Overconfidence detection
        confidence_analysis = self._detect_overconfidence(
            response_text, actual_output
        )
        analyses.append(("overconfidence_detection", confidence_analysis))
        
        # Aggregate results
        hallucination_scores = []
        all_issues = []
        
        for analysis_name, analysis_result in analyses:
            score = analysis_result.get("hallucination_score", 0.0)
            hallucination_scores.append(score)
            
            issues = analysis_result.get("issues", [])
            for issue in issues:
                issue["analysis_type"] = analysis_name
                all_issues.append(issue)
            
            hallucination_results["analysis"][analysis_name] = analysis_result
        
        # Calculate overall hallucination score (weighted average)
        weights = [0.25, 0.20, 0.20, 0.15, 0.15, 0.05]  # Based on reliability
        if len(hallucination_scores) < len(weights):
            weights = weights[:len(hallucination_scores)]
        
        overall_score = np.average(hallucination_scores, weights=weights)
        hallucination_results["overall_score"] = float(overall_score)
        hallucination_results["detected_issues"] = all_issues
        
        # Calculate confidence based on agreement between methods
        score_variance = np.var(hallucination_scores)
        confidence = max(0.0, 1.0 - score_variance)
        hallucination_results["confidence"] = float(confidence)
        
        return hallucination_results
    
    def detect_batch(
        self, 
        results: List[EvaluationResult], 
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Detect hallucinations across multiple evaluation results.
        
        Args:
            results: List of evaluation results to analyze
            threshold: Hallucination detection threshold
            
        Returns:
            Batch analysis results
        """
        batch_analysis = {
            "total_results": len(results),
            "hallucination_detections": 0,
            "average_hallucination_score": 0.0,
            "high_risk_cases": [],
            "patterns": {},
            "agent_analysis": {},
        }
        
        all_scores = []
        agent_scores = {}
        pattern_counts = {}
        
        for result in results:
            # Skip failed evaluations
            if result.status.value != "completed":
                continue
            
            # Get hallucination metric if available
            hallucination_metric = result.get_metric("hallucination")
            if not hallucination_metric:
                continue
            
            score = hallucination_metric.value
            all_scores.append(score)
            
            # Track by agent
            agent_name = result.agent_name
            if agent_name not in agent_scores:
                agent_scores[agent_name] = []
            agent_scores[agent_name].append(score)
            
            # Check if above threshold (higher scores indicate more hallucination)
            if score > threshold:
                batch_analysis["hallucination_detections"] += 1
                
                high_risk_case = {
                    "test_case_id": result.test_case_id,
                    "agent_name": agent_name,
                    "hallucination_score": score,
                    "timestamp": result.timestamp,
                }
                
                # Add details if available
                if hasattr(hallucination_metric, 'details') and hallucination_metric.details:
                    high_risk_case["details"] = hallucination_metric.details
                
                batch_analysis["high_risk_cases"].append(high_risk_case)
            
            # Extract patterns from metric details
            if hasattr(hallucination_metric, 'details') and hallucination_metric.details:
                details = hallucination_metric.details
                if "hallucination_types" in details:
                    for pattern in details["hallucination_types"]:
                        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Calculate statistics
        if all_scores:
            batch_analysis["average_hallucination_score"] = float(np.mean(all_scores))
            batch_analysis["hallucination_rate"] = (
                batch_analysis["hallucination_detections"] / len(all_scores)
            )
        
        # Agent-specific analysis
        for agent_name, scores in agent_scores.items():
            agent_analysis = {
                "evaluations": len(scores),
                "average_score": float(np.mean(scores)),
                "max_score": float(max(scores)),
                "min_score": float(min(scores)),
                "hallucination_rate": sum(1 for s in scores if s > threshold) / len(scores),
            }
            batch_analysis["agent_analysis"][agent_name] = agent_analysis
        
        # Pattern analysis
        batch_analysis["patterns"] = dict(
            sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        )
        
        return batch_analysis
    
    def _extract_response_text(self, data: Dict[str, Any]) -> str:
        """Extract text content from response data."""
        if isinstance(data, str):
            return data
        
        # Try common response fields
        for field in ["response", "answer", "result", "output", "content", "message"]:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict):
                    return json.dumps(value)
        
        # Fallback to string representation
        return str(data)
    
    def _extract_input_text(self, data: Dict[str, Any]) -> str:
        """Extract text content from input data."""
        if isinstance(data, str):
            return data
        
        # Try common input fields
        for field in ["input", "query", "question", "details", "description"]:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict):
                    return json.dumps(value)
        
        # Fallback to string representation
        return str(data)
    
    def _check_factual_consistency(
        self, input_text: str, response_text: str, expected_text: str
    ) -> Dict[str, Any]:
        """Check for factual inconsistencies in the response."""
        analysis = {
            "hallucination_score": 0.0,
            "issues": [],
            "confidence": 0.8,
        }
        
        issues = []
        
        # Check for contradictions with input
        input_facts = self._extract_facts(input_text)
        response_facts = self._extract_facts(response_text)
        
        contradictions = 0
        total_facts = len(response_facts)
        
        for response_fact in response_facts:
            if self._contradicts_facts(response_fact, input_facts):
                contradictions += 1
                issues.append({
                    "type": "factual_contradiction",
                    "description": f"Response fact contradicts input: {response_fact}",
                    "severity": "high",
                    "location": response_text.find(response_fact),
                })
        
        # Check for unsupported claims
        unsupported_claims = self._find_unsupported_claims(input_text, response_text)
        for claim in unsupported_claims:
            issues.append({
                "type": "unsupported_claim",
                "description": f"Claim not supported by input: {claim}",
                "severity": "medium",
                "location": response_text.find(claim),
            })
        
        # Calculate hallucination score
        if total_facts > 0:
            contradiction_ratio = contradictions / total_facts
            unsupported_ratio = len(unsupported_claims) / max(total_facts, 1)
            hallucination_score = min(1.0, contradiction_ratio + 0.5 * unsupported_ratio)
        else:
            hallucination_score = 0.0
        
        analysis["hallucination_score"] = hallucination_score
        analysis["issues"] = issues
        analysis["stats"] = {
            "total_facts": total_facts,
            "contradictions": contradictions,
            "unsupported_claims": len(unsupported_claims),
        }
        
        return analysis
    
    def _validate_against_knowledge_base(
        self, response_text: str, task_type: str
    ) -> Dict[str, Any]:
        """Validate response against domain knowledge base."""
        analysis = {
            "hallucination_score": 0.0,
            "issues": [],
            "confidence": 0.7,
        }
        
        issues = []
        invalid_terms = 0
        total_terms = 0
        
        # Extract domain-specific terms
        domain_terms = self._extract_domain_terms(response_text, task_type)
        total_terms = len(domain_terms)
        
        for term in domain_terms:
            if not self._is_valid_domain_term(term, task_type):
                invalid_terms += 1
                issues.append({
                    "type": "invalid_domain_term",
                    "description": f"Unknown or invalid term for {task_type}: {term}",
                    "severity": "medium",
                    "location": response_text.lower().find(term.lower()),
                })
        
        # Check for impossible combinations
        impossible_combinations = self._find_impossible_combinations(response_text)
        for combination in impossible_combinations:
            issues.append({
                "type": "impossible_combination",
                "description": f"Logically impossible combination: {combination}",
                "severity": "high",
                "location": 0,  # Would need more sophisticated location tracking
            })
        
        # Calculate score
        if total_terms > 0:
            hallucination_score = invalid_terms / total_terms
        else:
            hallucination_score = 0.0
        
        # Add penalty for impossible combinations
        hallucination_score += min(0.5, len(impossible_combinations) * 0.2)
        
        analysis["hallucination_score"] = min(1.0, hallucination_score)
        analysis["issues"] = issues
        analysis["stats"] = {
            "total_terms": total_terms,
            "invalid_terms": invalid_terms,
            "impossible_combinations": len(impossible_combinations),
        }
        
        return analysis
    
    def _detect_fabricated_content(
        self, input_text: str, response_text: str
    ) -> Dict[str, Any]:
        """Detect fabricated or made-up content in the response."""
        analysis = {
            "hallucination_score": 0.0,
            "issues": [],
            "confidence": 0.85,
        }
        
        issues = []
        fabrication_indicators = 0
        
        # Check for overly specific details not in input
        specific_patterns = [
            (r'\b\d{4}-\d{2}-\d{2}\b', "specific_date"),  # Specific dates
            (r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)\b', "specific_time"),  # Times
            (r'\b\$\d+(?:\.\d{2})?\b', "specific_amount"),  # Money amounts
            (r'\b\d+\.\d+%\b', "specific_percentage"),  # Percentages
            (r'\broom\s+\d{3,4}\b', "specific_room"),  # Room numbers
            (r'\bticket\s*#?\d+\b', "ticket_number"),  # Ticket numbers
        ]
        
        for pattern, pattern_type in specific_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                if match not in input_text:
                    fabrication_indicators += 1
                    issues.append({
                        "type": "fabricated_detail",
                        "subtype": pattern_type,
                        "description": f"Specific detail not in input: {match}",
                        "severity": "medium",
                        "content": match,
                    })
        
        # Check for made-up names/entities
        fake_entities = self._detect_fake_entities(input_text, response_text)
        fabrication_indicators += len(fake_entities)
        
        for entity in fake_entities:
            issues.append({
                "type": "fabricated_entity", 
                "description": f"Potentially fabricated entity: {entity}",
                "severity": "high",
                "content": entity,
            })
        
        # Check for pattern-based hallucination indicators
        for pattern in self.compiled_patterns:
            matches = pattern.findall(response_text)
            for match in matches:
                if match not in input_text:
                    fabrication_indicators += 1
                    issues.append({
                        "type": "suspicious_pattern",
                        "description": f"Suspicious specific detail: {match}",
                        "severity": "medium",
                        "content": match,
                    })
        
        # Calculate hallucination score based on response length and fabrication count
        response_length = len(response_text.split())
        if response_length > 0:
            fabrication_density = fabrication_indicators / response_length
            # Scale to 0-1 range (threshold of 0.1 density = 1.0 score)
            hallucination_score = min(1.0, fabrication_density * 10)
        else:
            hallucination_score = 0.0
        
        analysis["hallucination_score"] = hallucination_score
        analysis["issues"] = issues
        analysis["stats"] = {
            "fabrication_indicators": fabrication_indicators,
            "response_length": response_length,
            "fabrication_density": fabrication_density if response_length > 0 else 0.0,
        }
        
        return analysis
    
    def _check_logical_consistency(self, response_text: str) -> Dict[str, Any]:
        """Check for logical inconsistencies within the response."""
        analysis = {
            "hallucination_score": 0.0,
            "issues": [],
            "confidence": 0.6,
        }
        
        issues = []
        inconsistencies = 0
        
        # Check for contradictory statements
        contradictory_pairs = [
            (r'\b(?:secure|safe|protected)\b', r'\b(?:vulnerable|unsafe|exposed)\b'),
            (r'\b(?:compliant|follows)\b', r'\b(?:violates|non-compliant)\b'),
            (r'\b(?:authorized|permitted)\b', r'\b(?:unauthorized|forbidden)\b'),
            (r'\b(?:high|critical)\s+(?:priority|severity)\b', r'\b(?:low|minor)\s+(?:priority|severity)\b'),
            (r'\b(?:immediate|urgent)\b', r'\b(?:delayed|postponed)\b'),
        ]
        
        for positive_pattern, negative_pattern in contradictory_pairs:
            pos_matches = re.search(positive_pattern, response_text, re.IGNORECASE)
            neg_matches = re.search(negative_pattern, response_text, re.IGNORECASE)
            
            if pos_matches and neg_matches:
                inconsistencies += 1
                issues.append({
                    "type": "logical_contradiction",
                    "description": f"Contradictory statements: '{pos_matches.group()}' and '{neg_matches.group()}'",
                    "severity": "high",
                    "positive": pos_matches.group(),
                    "negative": neg_matches.group(),
                })
        
        # Check for temporal inconsistencies
        temporal_issues = self._find_temporal_inconsistencies(response_text)
        inconsistencies += len(temporal_issues)
        issues.extend(temporal_issues)
        
        # Check for impossible sequences
        sequence_issues = self._find_impossible_sequences(response_text)
        inconsistencies += len(sequence_issues)
        issues.extend(sequence_issues)
        
        # Calculate score based on inconsistency density
        response_sentences = len(re.split(r'[.!?]+', response_text))
        if response_sentences > 0:
            inconsistency_rate = inconsistencies / response_sentences
            hallucination_score = min(1.0, inconsistency_rate * 5)  # Scale appropriately
        else:
            hallucination_score = 0.0
        
        analysis["hallucination_score"] = hallucination_score
        analysis["issues"] = issues
        analysis["stats"] = {
            "inconsistencies": inconsistencies,
            "response_sentences": response_sentences,
        }
        
        return analysis
    
    def _analyze_semantic_coherence(
        self, input_text: str, response_text: str, expected_text: str
    ) -> Dict[str, Any]:
        """Analyze semantic coherence using sentence embeddings."""
        analysis = {
            "hallucination_score": 0.0,
            "issues": [],
            "confidence": 0.7,
        }
        
        if not self.sentence_model:
            analysis["confidence"] = 0.0
            return analysis
        
        try:
            # Generate embeddings
            input_embedding = self.sentence_model.encode([input_text])
            response_embedding = self.sentence_model.encode([response_text])
            
            # Calculate semantic similarity
            similarity = cosine_similarity(input_embedding, response_embedding)[0][0]
            
            # Low similarity might indicate hallucination or irrelevant response
            if similarity < 0.3:
                analysis["issues"].append({
                    "type": "semantic_incoherence",
                    "description": f"Response semantically distant from input (similarity: {similarity:.3f})",
                    "severity": "medium",
                    "similarity_score": float(similarity),
                })
            
            # Compare with expected output if available
            if expected_text:
                expected_embedding = self.sentence_model.encode([expected_text])
                expected_similarity = cosine_similarity(response_embedding, expected_embedding)[0][0]
                
                # Significant deviation from expected might indicate hallucination
                if expected_similarity < 0.4:
                    analysis["issues"].append({
                        "type": "expected_deviation",
                        "description": f"Response deviates significantly from expected (similarity: {expected_similarity:.3f})",
                        "severity": "medium",
                        "expected_similarity": float(expected_similarity),
                    })
                
                # Hallucination score based on expected deviation
                analysis["hallucination_score"] = max(0.0, 1.0 - expected_similarity)
            else:
                # Fallback: use input similarity
                analysis["hallucination_score"] = max(0.0, 1.0 - similarity)
            
            analysis["stats"] = {
                "input_similarity": float(similarity),
                "expected_similarity": float(expected_similarity) if expected_text else None,
            }
            
        except Exception as e:
            self.logger.warning(f"Semantic analysis failed: {e}")
            analysis["confidence"] = 0.0
        
        return analysis
    
    def _detect_overconfidence(
        self, response_text: str, actual_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect overconfidence or inappropriate certainty."""
        analysis = {
            "hallucination_score": 0.0,
            "issues": [],
            "confidence": 0.8,
        }
        
        issues = []
        overconfidence_indicators = 0
        
        # Look for absolute language
        absolute_patterns = [
            r'\b(?:definitely|certainly|absolutely|guaranteed|always|never)\b',
            r'\b100%\s*(?:certain|sure|confident)\b',
            r'\bwithout\s+(?:a\s+)?doubt\b',
            r'\bimpossible\s+to\b',
            r'\bguaranteed?\s+to\b',
        ]
        
        for pattern in absolute_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            overconfidence_indicators += len(matches)
            
            for match in matches:
                issues.append({
                    "type": "overconfidence",
                    "description": f"Overly confident language: '{match}'",
                    "severity": "low",
                    "content": match,
                })
        
        # Check explicit confidence scores
        explicit_confidence = actual_output.get("confidence")
        if explicit_confidence and isinstance(explicit_confidence, (int, float)):
            if explicit_confidence >= 0.95:
                # Very high confidence might indicate overconfidence
                overconfidence_indicators += 1
                issues.append({
                    "type": "high_confidence_score",
                    "description": f"Unusually high confidence score: {explicit_confidence}",
                    "severity": "low",
                    "confidence_value": explicit_confidence,
                })
        
        # Calculate score
        text_length = len(response_text.split())
        if text_length > 0:
            overconfidence_density = overconfidence_indicators / text_length
            hallucination_score = min(0.5, overconfidence_density * 20)  # Cap at 0.5
        else:
            hallucination_score = 0.0
        
        analysis["hallucination_score"] = hallucination_score
        analysis["issues"] = issues
        analysis["stats"] = {
            "overconfidence_indicators": overconfidence_indicators,
            "text_length": text_length,
            "explicit_confidence": explicit_confidence,
        }
        
        return analysis
    
    # Helper methods for content analysis
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extract factual statements from text."""
        # Simple fact extraction - in practice, could use more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        facts = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Minimum length for meaningful fact
                facts.append(sentence)
        
        return facts
    
    def _contradicts_facts(self, response_fact: str, input_facts: List[str]) -> bool:
        """Check if a response fact contradicts input facts."""
        response_lower = response_fact.lower()
        
        # Simple contradiction detection
        contradiction_patterns = [
            ("not", "is"), ("false", "true"), ("no", "yes"),
            ("low", "high"), ("safe", "dangerous"), ("secure", "vulnerable")
        ]
        
        for input_fact in input_facts:
            input_lower = input_fact.lower()
            
            for neg_word, pos_word in contradiction_patterns:
                if (neg_word in response_lower and pos_word in input_lower) or \
                   (pos_word in response_lower and neg_word in input_lower):
                    return True
        
        return False
    
    def _find_unsupported_claims(self, input_text: str, response_text: str) -> List[str]:
        """Find claims in response not supported by input."""
        # Identify specific claims that would need support
        claim_patterns = [
            r'according to [^,\.]+',
            r'studies show that [^,\.]+',
            r'research indicates [^,\.]+',
            r'it is proven that [^,\.]+',
        ]
        
        unsupported_claims = []
        input_lower = input_text.lower()
        
        for pattern in claim_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                # Check if any supporting evidence exists in input
                if not any(word in input_lower for word in match.lower().split()[2:]):
                    unsupported_claims.append(match)
        
        return unsupported_claims
    
    def _extract_domain_terms(self, text: str, task_type: str) -> List[str]:
        """Extract domain-specific terms from text."""
        text_lower = text.lower()
        terms = []
        
        # Extract terms based on task type
        if task_type in ["security_triage", "threat_detection"]:
            patterns = self.hotel_knowledge_patterns["systems"]
            patterns.update({"malware", "breach", "vulnerability", "threat", "incident"})
        elif task_type == "guest_service":
            patterns = self.hotel_knowledge_patterns["amenities"]
            patterns.update(self.hotel_knowledge_patterns["room_types"])
        else:
            patterns = set()
            for category in self.hotel_knowledge_patterns.values():
                patterns.update(category)
        
        for term in patterns:
            if term in text_lower:
                terms.append(term)
        
        return terms
    
    def _is_valid_domain_term(self, term: str, task_type: str) -> bool:
        """Check if a term is valid for the domain."""
        term_lower = term.lower()
        
        # Check against all knowledge patterns
        for category in self.hotel_knowledge_patterns.values():
            if term_lower in category:
                return True
        
        # Additional validation could include external knowledge bases
        return False
    
    def _find_impossible_combinations(self, text: str) -> List[str]:
        """Find logically impossible combinations in text."""
        impossible_combinations = []
        text_lower = text.lower()
        
        # Define impossible combinations for hospitality context
        impossible_pairs = [
            ("checkout", "checkin"),  # Same time
            ("vacant", "occupied"),  # Room status
            ("guest", "no guest"),  # Guest presence
            ("online", "offline"),  # System status
        ]
        
        for term1, term2 in impossible_pairs:
            if term1 in text_lower and term2 in text_lower:
                # Check if they appear in close proximity (might indicate simultaneity)
                term1_pos = text_lower.find(term1)
                term2_pos = text_lower.find(term2)
                
                if abs(term1_pos - term2_pos) < 100:  # Within 100 characters
                    impossible_combinations.append(f"{term1} and {term2}")
        
        return impossible_combinations
    
    def _detect_fake_entities(self, input_text: str, response_text: str) -> List[str]:
        """Detect potentially fabricated entities (names, places, etc.)."""
        fake_entities = []
        
        # Simple approach: find proper nouns not in input
        import re
        
        # Extract proper nouns from response
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', response_text)
        
        input_lower = input_text.lower()
        
        for noun in proper_nouns:
            if noun.lower() not in input_lower:
                # Additional checks to avoid false positives
                if len(noun) > 2 and noun not in ["The", "This", "That", "When", "Where"]:
                    fake_entities.append(noun)
        
        return fake_entities
    
    def _find_temporal_inconsistencies(self, text: str) -> List[Dict[str, Any]]:
        """Find temporal inconsistencies in the text."""
        issues = []
        
        # Extract time-related expressions
        time_patterns = [
            (r'\b(?:before|after)\s+\d{1,2}:\d{2}\b', "time_reference"),
            (r'\b(?:yesterday|today|tomorrow)\b', "day_reference"),
            (r'\b\d{1,2}\s+(?:hours?|minutes?|seconds?)\s+(?:ago|later)\b', "duration"),
        ]
        
        time_references = []
        for pattern, ref_type in time_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                time_references.append({
                    "text": match.group(),
                    "type": ref_type,
                    "position": match.start(),
                })
        
        # Simple consistency check (could be enhanced)
        if len(time_references) > 1:
            # Check for obvious conflicts
            day_refs = [ref for ref in time_references if ref["type"] == "day_reference"]
            if len(set(ref["text"].lower() for ref in day_refs)) > 1:
                issues.append({
                    "type": "temporal_inconsistency",
                    "description": "Multiple conflicting day references",
                    "severity": "medium",
                    "references": [ref["text"] for ref in day_refs],
                })
        
        return issues
    
    def _find_impossible_sequences(self, text: str) -> List[Dict[str, Any]]:
        """Find impossible action sequences."""
        issues = []
        
        # Look for impossible sequences in security context
        sequence_patterns = [
            (r'after\s+(?:login|access)', r'before\s+(?:authentication|verification)'),
            (r'evacuat\w+', r'(?:enter|access)'),  # Evacuate then enter
            (r'disable\w*', r'activate\w*'),  # Disable then activate same thing
        ]
        
        for first_pattern, second_pattern in sequence_patterns:
            first_match = re.search(first_pattern, text, re.IGNORECASE)
            second_match = re.search(second_pattern, text, re.IGNORECASE)
            
            if first_match and second_match:
                # Check if second action comes after first (rough check)
                if first_match.end() < second_match.start():
                    issues.append({
                        "type": "impossible_sequence",
                        "description": f"Impossible sequence: '{first_match.group()}' followed by '{second_match.group()}'",
                        "severity": "high",
                        "first_action": first_match.group(),
                        "second_action": second_match.group(),
                    })
        
        return issues