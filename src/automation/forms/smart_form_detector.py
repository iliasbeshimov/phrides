"""
Smart form detector that learns from successful URL patterns.
"""

import json
import os
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
import re

@dataclass
class UrlPattern:
    """Represents a learned URL pattern"""
    pattern: str
    success_count: int = 0
    total_attempts: int = 0
    confidence: float = 0.0
    
    def update_success(self):
        """Record a successful detection"""
        self.success_count += 1
        self.total_attempts += 1
        self.confidence = self.success_count / self.total_attempts
    
    def update_failure(self):
        """Record a failed detection"""
        self.total_attempts += 1
        self.confidence = self.success_count / self.total_attempts


class SmartUrlGenerator:
    """Generates URLs based on learned patterns and common conventions"""
    
    def __init__(self, knowledge_file: str = "url_patterns.json"):
        self.knowledge_file = knowledge_file
        self.patterns: Dict[str, UrlPattern] = {}
        self.load_knowledge()
        
        # Base patterns to start with (before learning)
        self.base_patterns = [
            "/contact-us/",
            "/contact-us", 
            "/contact",
            "/get-quote",
            "/request-quote",
            "/schedule-service",
            "/inquiry",
            "/contactus",
            "/contact_us",
            "/request-info",
            "/lead-form",
            "/contact-form",
            "/get-started"
        ]
    
    def load_knowledge(self):
        """Load learned patterns from file"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r') as f:
                    data = json.load(f)
                    for pattern, stats in data.items():
                        self.patterns[pattern] = UrlPattern(
                            pattern=pattern,
                            success_count=stats['success_count'],
                            total_attempts=stats['total_attempts'],
                            confidence=stats['confidence']
                        )
            except Exception as e:
                print(f"Warning: Could not load URL patterns: {e}")
    
    def save_knowledge(self):
        """Save learned patterns to file"""
        try:
            data = {}
            for pattern, stats in self.patterns.items():
                data[pattern] = {
                    'success_count': stats.success_count,
                    'total_attempts': stats.total_attempts,
                    'confidence': stats.confidence
                }
            with open(self.knowledge_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save URL patterns: {e}")
    
    def record_success(self, successful_url: str):
        """Record a successful URL pattern"""
        pattern = self._extract_pattern(successful_url)
        if pattern:
            if pattern not in self.patterns:
                self.patterns[pattern] = UrlPattern(pattern=pattern)
            self.patterns[pattern].update_success()
            self.save_knowledge()
    
    def record_failure(self, failed_url: str):
        """Record a failed URL pattern"""
        pattern = self._extract_pattern(failed_url)
        if pattern:
            if pattern not in self.patterns:
                self.patterns[pattern] = UrlPattern(pattern=pattern)
            self.patterns[pattern].update_failure()
            self.save_knowledge()
    
    def _extract_pattern(self, url: str) -> Optional[str]:
        """Extract the path pattern from a URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path.rstrip('/')
            if not path:
                return "/"
            return path
        except:
            return None
    
    def generate_urls(self, base_website: str, limit: int = 8) -> List[str]:
        """Generate prioritized URLs based on learned patterns"""
        if not base_website.startswith('http'):
            base_website = 'https://' + base_website
        base_website = base_website.rstrip('/')
        
        urls = [base_website]  # Always try homepage first
        
        # Sort patterns by confidence (learned patterns first)
        learned_patterns = sorted(
            [(p.pattern, p.confidence) for p in self.patterns.values() if p.confidence > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Add high-confidence learned patterns
        for pattern, confidence in learned_patterns[:limit//2]:
            urls.append(base_website + pattern)
        
        # Fill remaining with base patterns
        for pattern in self.base_patterns:
            if len(urls) >= limit:
                break
            test_url = base_website + pattern
            if test_url not in urls:
                urls.append(test_url)
        
        return urls[:limit]
    
    def get_stats(self) -> Dict:
        """Get learning statistics"""
        if not self.patterns:
            return {"total_patterns": 0, "successful_patterns": 0}
        
        successful = [p for p in self.patterns.values() if p.success_count > 0]
        return {
            "total_patterns": len(self.patterns),
            "successful_patterns": len(successful),
            "avg_confidence": sum(p.confidence for p in successful) / len(successful) if successful else 0,
            "top_patterns": sorted(
                [(p.pattern, p.confidence, p.success_count) for p in successful],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


class SmartFormDetector:
    """Form detector that learns from successful URL patterns"""
    
    def __init__(self, knowledge_file: str = "form_patterns.json"):
        self.url_generator = SmartUrlGenerator(knowledge_file)
        
        # Quick selectors for fast detection
        self.quick_selectors = [
            "form input[type='email']",
            "form input[name*='email' i]",
            "form input[name*='phone' i]", 
            "form textarea",
            "input[type='email']",
            "input[name*='email' i]",
            "input[name*='contact' i]",
            "textarea[name*='message' i]"
        ]
    
    async def has_contact_form_quickly(self, page) -> bool:
        """Quick check if page has a contact form"""
        try:
            # Quick selector-based detection
            for selector in self.quick_selectors:
                elements = page.locator(selector)
                count = await elements.count()
                if count > 0:
                    return True
            return False
        except:
            return False
    
    def record_success(self, url: str):
        """Record successful form detection"""
        self.url_generator.record_success(url)
    
    def record_failure(self, url: str):
        """Record failed form detection"""
        self.url_generator.record_failure(url)
    
    def generate_urls(self, base_website: str) -> List[str]:
        """Generate smart URL list"""
        return self.url_generator.generate_urls(base_website)
    
    def get_learning_stats(self) -> Dict:
        """Get current learning statistics"""
        return self.url_generator.get_stats()