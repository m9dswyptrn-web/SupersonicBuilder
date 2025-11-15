#!/usr/bin/env python3
"""
Wake Word Detection Module
Simulated wake word detection for "Hey Sonic" and custom wake words
"""

import time
import random
from typing import Optional, List, Dict
from datetime import datetime


class WakeWordDetector:
    """Simulated wake word detection system."""
    
    def __init__(self, wake_word: str = "Hey Sonic", sensitivity: float = 0.5):
        """
        Initialize wake word detector.
        
        Args:
            wake_word: The wake word to detect
            sensitivity: Detection sensitivity (0.0 to 1.0)
        """
        self.wake_word = wake_word
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        self.enabled = True
        self.training_samples = []
        self.detection_history = []
        
    def detect(self, audio_input: str) -> Dict:
        """
        Detect wake word in audio input (simulated).
        
        Args:
            audio_input: Simulated audio input text
            
        Returns:
            Detection result with confidence score
        """
        if not self.enabled:
            return {
                'detected': False,
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat(),
                'reason': 'Wake word detection disabled'
            }
        
        audio_lower = audio_input.lower().strip()
        wake_lower = self.wake_word.lower()
        
        detected = False
        confidence = 0.0
        
        if wake_lower in audio_lower:
            confidence = self._calculate_confidence(audio_input)
            
            threshold = 1.0 - self.sensitivity
            detected = confidence >= threshold
        elif self._is_similar(audio_lower, wake_lower):
            confidence = self._calculate_similarity_confidence(audio_lower, wake_lower)
            threshold = 1.0 - (self.sensitivity * 0.8)
            detected = confidence >= threshold
        
        result = {
            'detected': detected,
            'confidence': round(confidence, 3),
            'timestamp': datetime.now().isoformat(),
            'wake_word': self.wake_word,
            'sensitivity': self.sensitivity,
            'input': audio_input
        }
        
        if detected:
            self.detection_history.append(result)
            if len(self.detection_history) > 100:
                self.detection_history = self.detection_history[-100:]
        
        return result
    
    def _calculate_confidence(self, audio_input: str) -> float:
        """Calculate confidence score for exact wake word match."""
        audio_lower = audio_input.lower().strip()
        wake_lower = self.wake_word.lower()
        
        if audio_lower == wake_lower:
            return 0.95 + random.uniform(0, 0.05)
        
        if audio_lower.startswith(wake_lower) or audio_lower.endswith(wake_lower):
            return 0.85 + random.uniform(0, 0.1)
        
        if wake_lower in audio_lower:
            return 0.75 + random.uniform(0, 0.15)
        
        return 0.0
    
    def _is_similar(self, text1: str, text2: str) -> bool:
        """Check if two strings are similar (simple heuristic)."""
        if not text1 or not text2:
            return False
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return False
        
        common = words1 & words2
        similarity = len(common) / max(len(words1), len(words2))
        
        return similarity > 0.5
    
    def _calculate_similarity_confidence(self, text1: str, text2: str) -> float:
        """Calculate confidence based on similarity."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        common = words1 & words2
        similarity = len(common) / max(len(words1), len(words2))
        
        return similarity * 0.7 + random.uniform(0, 0.1)
    
    def train(self, audio_sample: str) -> Dict:
        """
        Add training sample for wake word (simulated).
        
        Args:
            audio_sample: Training audio sample
            
        Returns:
            Training result
        """
        sample = {
            'audio': audio_sample,
            'timestamp': datetime.now().isoformat()
        }
        
        self.training_samples.append(sample)
        
        if len(self.training_samples) > 50:
            self.training_samples = self.training_samples[-50:]
        
        improvement = min(len(self.training_samples) * 0.01, 0.15)
        
        return {
            'ok': True,
            'samples_count': len(self.training_samples),
            'estimated_improvement': round(improvement * 100, 1),
            'message': f'Training sample added. Total samples: {len(self.training_samples)}'
        }
    
    def set_wake_word(self, wake_word: str) -> bool:
        """
        Change the wake word.
        
        Args:
            wake_word: New wake word
            
        Returns:
            Success status
        """
        if not wake_word or len(wake_word.strip()) == 0:
            return False
        
        self.wake_word = wake_word.strip()
        self.training_samples = []
        return True
    
    def set_sensitivity(self, sensitivity: float) -> bool:
        """
        Adjust detection sensitivity.
        
        Args:
            sensitivity: Sensitivity value (0.0 to 1.0)
            
        Returns:
            Success status
        """
        if not 0.0 <= sensitivity <= 1.0:
            return False
        
        self.sensitivity = sensitivity
        return True
    
    def enable(self, enabled: bool = True):
        """Enable or disable wake word detection."""
        self.enabled = enabled
    
    def get_stats(self) -> Dict:
        """Get detection statistics."""
        recent_detections = self.detection_history[-20:] if self.detection_history else []
        
        if recent_detections:
            avg_confidence = sum(d['confidence'] for d in recent_detections) / len(recent_detections)
        else:
            avg_confidence = 0.0
        
        return {
            'wake_word': self.wake_word,
            'sensitivity': self.sensitivity,
            'enabled': self.enabled,
            'training_samples': len(self.training_samples),
            'total_detections': len(self.detection_history),
            'recent_detections': len(recent_detections),
            'avg_confidence': round(avg_confidence, 3)
        }
    
    def get_detection_history(self, limit: int = 20) -> List[Dict]:
        """Get recent detection history."""
        return self.detection_history[-limit:]
    
    def reset_training(self):
        """Reset all training samples."""
        self.training_samples = []
        self.detection_history = []
    
    def test_detection(self, test_phrase: str) -> Dict:
        """
        Test wake word detection with a phrase.
        
        Args:
            test_phrase: Phrase to test
            
        Returns:
            Detection result with recommendation
        """
        result = self.detect(test_phrase)
        
        recommendation = ""
        if result['detected']:
            if result['confidence'] > 0.9:
                recommendation = "Excellent detection! Wake word clearly recognized."
            elif result['confidence'] > 0.7:
                recommendation = "Good detection. Consider adding training samples for better accuracy."
            else:
                recommendation = "Weak detection. Increase sensitivity or add more training samples."
        else:
            if result['confidence'] > 0.5:
                recommendation = "Close! Try increasing sensitivity or speaking more clearly."
            else:
                recommendation = "Not detected. Make sure to say the wake word clearly."
        
        result['recommendation'] = recommendation
        return result
