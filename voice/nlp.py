#!/usr/bin/env python3
"""
Natural Language Processing Module
Parse voice commands, extract intent and entities
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class NaturalLanguageProcessor:
    """NLP engine for voice command processing."""
    
    def __init__(self):
        """Initialize NLP processor with command patterns."""
        self.command_patterns = self._init_command_patterns()
        self.context_history = []
        self.max_context_history = 10
    
    def _init_command_patterns(self) -> List[Dict]:
        """Initialize command patterns for intent recognition."""
        return [
            {
                'intent': 'play_music',
                'patterns': [
                    r'play\s+(?:my\s+)?(.+?)\s+playlist',
                    r'play\s+(.+)',
                    r'start\s+playing\s+(.+)',
                    r'put\s+on\s+(.+)'
                ],
                'entity': 'playlist_name',
                'service': 'media',
                'variations': ['play', 'start playing', 'put on']
            },
            {
                'intent': 'navigate',
                'patterns': [
                    r'navigate\s+to\s+(.+)',
                    r'take\s+me\s+to\s+(.+)',
                    r'directions\s+to\s+(.+)',
                    r'show\s+me\s+(?:the\s+)?(?:nearest\s+)?(.+)',
                    r'find\s+(?:the\s+)?(?:nearest\s+)?(.+)'
                ],
                'entity': 'location',
                'service': 'navigation',
                'variations': ['navigate to', 'take me to', 'show me', 'find']
            },
            {
                'intent': 'adjust_bass',
                'patterns': [
                    r'turn\s+(?:up|down|increase|decrease)\s+(?:the\s+)?bass',
                    r'(?:boost|lower|raise|reduce)\s+(?:the\s+)?bass',
                    r'bass\s+(?:up|down)',
                    r'(?:more|less)\s+bass'
                ],
                'entity': 'adjustment',
                'service': 'dsp',
                'variations': ['turn up', 'turn down', 'boost', 'lower', 'increase', 'decrease']
            },
            {
                'intent': 'adjust_audio',
                'patterns': [
                    r'(?:turn|set)\s+volume\s+to\s+(\d+)',
                    r'volume\s+(\d+)',
                    r'(?:mute|unmute)',
                    r'(?:turn\s+)?(?:up|down)\s+(?:the\s+)?volume'
                ],
                'entity': 'volume_level',
                'service': 'dsp',
                'variations': ['volume', 'mute', 'unmute']
            },
            {
                'intent': 'lighting_control',
                'patterns': [
                    r'enable\s+night\s+mode\s+lighting',
                    r'turn\s+(?:on|off)\s+(?:the\s+)?lights?',
                    r'set\s+lights?\s+to\s+(.+)',
                    r'change\s+(?:the\s+)?(?:light\s+)?color\s+to\s+(.+)',
                    r'(?:dim|brighten)\s+(?:the\s+)?lights?'
                ],
                'entity': 'lighting_setting',
                'service': 'lighting',
                'variations': ['turn on', 'turn off', 'set', 'change color', 'dim', 'brighten']
            },
            {
                'intent': 'check_tpms',
                'patterns': [
                    r'what(?:\'?s|\s+is)\s+my\s+tire\s+pressure',
                    r'check\s+tire\s+pressure',
                    r'tire\s+pressure\s+(?:status|reading)',
                    r'how\s+are\s+my\s+tires'
                ],
                'entity': None,
                'service': 'tpms',
                'variations': ["what's my tire pressure", 'check tire pressure']
            },
            {
                'intent': 'climate_control',
                'patterns': [
                    r'set\s+temperature\s+to\s+(\d+)',
                    r'(?:make\s+it\s+)?(?:warmer|cooler|hotter|colder)',
                    r'turn\s+(?:on|off)\s+(?:the\s+)?(?:ac|air\s+conditioning|heat|heating)',
                    r'(?:increase|decrease)\s+(?:the\s+)?temperature'
                ],
                'entity': 'temperature',
                'service': 'climate',
                'variations': ['set temperature', 'warmer', 'cooler', 'ac on', 'ac off']
            },
            {
                'intent': 'make_call',
                'patterns': [
                    r'call\s+(.+)',
                    r'phone\s+(.+)',
                    r'dial\s+(.+)'
                ],
                'entity': 'contact_name',
                'service': 'phone',
                'variations': ['call', 'phone', 'dial']
            },
            {
                'intent': 'launch_app',
                'patterns': [
                    r'open\s+(.+)',
                    r'launch\s+(.+)',
                    r'start\s+(.+)\s+app'
                ],
                'entity': 'app_name',
                'service': 'apps',
                'variations': ['open', 'launch', 'start']
            },
            {
                'intent': 'navigation_home',
                'patterns': [
                    r'navigate\s+(?:to\s+)?home',
                    r'take\s+me\s+home',
                    r'directions\s+home',
                    r'go\s+home'
                ],
                'entity': None,
                'service': 'navigation',
                'variations': ['navigate home', 'take me home', 'go home']
            }
        ]
    
    def parse_command(self, command: str) -> Dict:
        """
        Parse voice command to extract intent and entities.
        
        Args:
            command: Voice command text
            
        Returns:
            Parsed command with intent, entities, and service
        """
        command_lower = command.lower().strip()
        
        for pattern_group in self.command_patterns:
            for pattern in pattern_group['patterns']:
                match = re.search(pattern, command_lower)
                if match:
                    entities = {}
                    
                    if pattern_group['entity'] and match.groups():
                        entity_value = match.group(1).strip()
                        entities[pattern_group['entity']] = entity_value
                    
                    if pattern_group['intent'] == 'adjust_bass':
                        if 'up' in command_lower or 'boost' in command_lower or 'increase' in command_lower or 'more' in command_lower:
                            entities['direction'] = 'increase'
                        elif 'down' in command_lower or 'lower' in command_lower or 'decrease' in command_lower or 'less' in command_lower:
                            entities['direction'] = 'decrease'
                        else:
                            entities['direction'] = 'increase'
                    
                    if pattern_group['intent'] == 'lighting_control':
                        if 'night mode' in command_lower:
                            entities['mode'] = 'night'
                        elif 'off' in command_lower:
                            entities['action'] = 'off'
                        elif 'on' in command_lower:
                            entities['action'] = 'on'
                        elif 'dim' in command_lower:
                            entities['action'] = 'dim'
                        elif 'brighten' in command_lower:
                            entities['action'] = 'brighten'
                    
                    if pattern_group['intent'] == 'climate_control':
                        if 'warmer' in command_lower or 'hotter' in command_lower or 'increase' in command_lower:
                            entities['adjustment'] = 'increase'
                        elif 'cooler' in command_lower or 'colder' in command_lower or 'decrease' in command_lower:
                            entities['adjustment'] = 'decrease'
                        elif 'on' in command_lower:
                            entities['action'] = 'on'
                        elif 'off' in command_lower:
                            entities['action'] = 'off'
                    
                    result = {
                        'intent': pattern_group['intent'],
                        'entities': entities,
                        'service': pattern_group['service'],
                        'confidence': 0.9,
                        'raw_command': command,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self._add_to_context(result)
                    return result
        
        result = {
            'intent': 'unknown',
            'entities': {},
            'service': None,
            'confidence': 0.0,
            'raw_command': command,
            'timestamp': datetime.now().isoformat(),
            'error': 'Command not recognized'
        }
        
        return result
    
    def _add_to_context(self, parsed_command: Dict):
        """Add parsed command to context history."""
        self.context_history.append(parsed_command)
        if len(self.context_history) > self.max_context_history:
            self.context_history = self.context_history[-self.max_context_history:]
    
    def parse_with_context(self, command: str) -> Dict:
        """
        Parse command with context awareness.
        
        Args:
            command: Voice command text
            
        Returns:
            Parsed command with context
        """
        command_lower = command.lower().strip()
        
        if command_lower.startswith('and also'):
            command_lower = command_lower.replace('and also', '', 1).strip()
            command = command.replace('and also', '', 1).strip()
        
        parsed = self.parse_command(command)
        
        if self.context_history:
            last_cmd = self.context_history[-1]
            parsed['previous_intent'] = last_cmd.get('intent')
            parsed['previous_service'] = last_cmd.get('service')
            
            if parsed['intent'] == 'unknown' and self.context_history:
                last_service = self.context_history[-1].get('service')
                if last_service:
                    parsed['suggested_service'] = last_service
        
        return parsed
    
    def extract_entities(self, command: str, entity_types: List[str]) -> Dict:
        """
        Extract specific entities from command.
        
        Args:
            command: Voice command text
            entity_types: List of entity types to extract
            
        Returns:
            Extracted entities
        """
        entities = {}
        command_lower = command.lower()
        
        if 'number' in entity_types:
            numbers = re.findall(r'\d+', command)
            if numbers:
                entities['numbers'] = [int(n) for n in numbers]
        
        if 'location' in entity_types:
            location_keywords = ['to', 'at', 'near', 'in']
            for keyword in location_keywords:
                pattern = f'{keyword}\\s+(.+?)(?:\\s+(?:please|now|asap))?$'
                match = re.search(pattern, command_lower)
                if match:
                    entities['location'] = match.group(1).strip()
                    break
        
        if 'contact' in entity_types:
            contact_pattern = r'call\s+(.+?)(?:\s+(?:please|now))?$'
            match = re.search(contact_pattern, command_lower)
            if match:
                entities['contact'] = match.group(1).strip()
        
        return entities
    
    def handle_variations(self, command: str) -> List[str]:
        """
        Generate command variations to improve matching.
        
        Args:
            command: Original command
            
        Returns:
            List of command variations
        """
        variations = [command]
        
        synonyms = {
            'boost': ['increase', 'raise', 'turn up'],
            'lower': ['decrease', 'reduce', 'turn down'],
            'show': ['display', 'find', 'locate'],
            'play': ['start', 'begin'],
            'set': ['adjust', 'change']
        }
        
        for original, replacements in synonyms.items():
            if original in command.lower():
                for replacement in replacements:
                    new_command = re.sub(
                        r'\b' + original + r'\b',
                        replacement,
                        command,
                        flags=re.IGNORECASE
                    )
                    if new_command not in variations:
                        variations.append(new_command)
        
        return variations
    
    def get_context_history(self, limit: int = 5) -> List[Dict]:
        """Get recent command context history."""
        return self.context_history[-limit:]
    
    def clear_context(self):
        """Clear context history."""
        self.context_history = []
    
    def suggest_commands(self, partial_command: str) -> List[str]:
        """
        Suggest commands based on partial input.
        
        Args:
            partial_command: Partial command text
            
        Returns:
            List of suggested commands
        """
        suggestions = []
        partial_lower = partial_command.lower()
        
        common_commands = [
            "Play my rock playlist",
            "Navigate to home",
            "What's my tire pressure?",
            "Turn up the bass",
            "Enable night mode lighting",
            "Set temperature to 72",
            "Call Mom",
            "Show me the nearest gas station"
        ]
        
        for cmd in common_commands:
            if partial_lower in cmd.lower():
                suggestions.append(cmd)
        
        return suggestions[:5]
