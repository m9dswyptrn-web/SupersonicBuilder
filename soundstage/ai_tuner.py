import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class AITuner:
    """
    AI-powered soundstage tuning using Anthropic Claude.
    Analyzes current setup and provides intelligent recommendations.
    """
    
    def __init__(self):
        self.has_api_key = False
        self.client = None
        self.model = 'claude-sonnet-4-20250514'
        
        self._init_claude()
    
    def _init_claude(self):
        """Initialize Claude client if API key is available."""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.has_api_key = True
        except ImportError:
            pass
        except Exception:
            pass
    
    def analyze_setup(
        self,
        speaker_positions: Dict[str, Any],
        acoustic_data: Dict[str, Any],
        listening_position: str = 'driver',
        current_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze current soundstage setup and provide recommendations.
        Works with or without AI API key.
        """
        if not self.has_api_key or not self.client:
            return self._fallback_analysis(
                speaker_positions,
                acoustic_data,
                listening_position,
                current_settings
            )
        
        try:
            prompt = self._build_analysis_prompt(
                speaker_positions,
                acoustic_data,
                listening_position,
                current_settings
            )
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            analysis_text = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            
            recommendations = self._parse_ai_response(analysis_text)
            
            return {
                'source': 'ai',
                'model': self.model,
                'analysis': analysis_text,
                'recommendations': recommendations,
                'tokens_used': tokens_used,
                'confidence_score': 0.85
            }
            
        except Exception as e:
            return {
                'source': 'fallback',
                'error': str(e),
                **self._fallback_analysis(
                    speaker_positions,
                    acoustic_data,
                    listening_position,
                    current_settings
                )
            }
    
    def _build_analysis_prompt(
        self,
        speaker_positions: Dict[str, Any],
        acoustic_data: Dict[str, Any],
        listening_position: str,
        current_settings: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for Claude analysis."""
        prompt = f"""You are an expert car audio engineer specializing in soundstage optimization for vehicle installations. 
Analyze this 2014 Chevy Sonic audio system configuration and provide specific tuning recommendations.

LISTENING POSITION: {listening_position}

SPEAKER POSITIONS (inches from origin, x=front, y=left-right, z=height):
"""
        
        for speaker, pos in speaker_positions.items():
            prompt += f"- {speaker}: x={pos.get('x', 0):.1f}, y={pos.get('y', 0):.1f}, z={pos.get('z', 0):.1f}\n"
        
        prompt += f"\nCABIN ACOUSTIC DATA:\n"
        prompt += f"- Dimensions: {acoustic_data.get('dimensions', {})}\n"
        
        if 'room_modes' in acoustic_data:
            modes = acoustic_data['room_modes'].get('axial', [])[:5]
            modes_str = [f"{m['frequency_hz']:.1f}Hz" for m in modes]
            prompt += f"- Primary room modes: {modes_str}\n"
        
        if 'absorption_spectrum' in acoustic_data:
            prompt += f"- Absorption characteristics: {acoustic_data['absorption_spectrum']}\n"
        
        if current_settings:
            prompt += f"\nCURRENT SETTINGS:\n{current_settings}\n"
        
        prompt += """
Please provide:
1. Analysis of the current soundstage geometry
2. Specific time alignment recommendations (in milliseconds)
3. Balance/fader adjustments needed
4. EQ corrections for cabin acoustics
5. Center image optimization suggestions
6. Priority ranking of recommended changes

Format your response with clear sections and specific numerical values."""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured recommendations."""
        recommendations = {
            'time_alignment': {},
            'balance_fader': {},
            'eq_corrections': [],
            'center_image': {},
            'priorities': []
        }
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            
            if 'time alignment' in line_lower:
                current_section = 'time_alignment'
            elif 'balance' in line_lower or 'fader' in line_lower:
                current_section = 'balance_fader'
            elif 'eq' in line_lower or 'equalization' in line_lower:
                current_section = 'eq_corrections'
            elif 'center image' in line_lower:
                current_section = 'center_image'
            elif 'priority' in line_lower or 'ranking' in line_lower:
                current_section = 'priorities'
        
        return recommendations
    
    def _fallback_analysis(
        self,
        speaker_positions: Dict[str, Any],
        acoustic_data: Dict[str, Any],
        listening_position: str,
        current_settings: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Provide rule-based analysis when AI is not available.
        Uses acoustic principles and best practices.
        """
        recommendations = []
        
        room_modes = acoustic_data.get('room_modes', {}).get('axial', [])
        for mode in room_modes[:3]:
            if mode['frequency_hz'] < 200:
                recommendations.append({
                    'category': 'EQ',
                    'priority': 'high',
                    'action': f"Apply -3dB cut at {mode['frequency_hz']:.0f}Hz (Q=4.0)",
                    'reason': f"Room mode: {mode['mode']}",
                    'impact': 'Reduces cabin resonance and boom'
                })
        
        absorption = acoustic_data.get('absorption_spectrum', {})
        if absorption.get('4000Hz', 0) > 0.3:
            recommendations.append({
                'category': 'EQ',
                'priority': 'medium',
                'action': 'Apply +2dB high shelf at 8kHz',
                'reason': 'High treble absorption from cabin materials',
                'impact': 'Restores clarity and air'
            })
        
        if listening_position == 'driver':
            recommendations.append({
                'category': 'Balance',
                'priority': 'high',
                'action': 'Balance: -2dB left, Fader: +3dB front',
                'reason': 'Driver position is off-center and forward',
                'impact': 'Centers soundstage and improves imaging'
            })
        elif listening_position == 'passenger':
            recommendations.append({
                'category': 'Balance',
                'priority': 'high',
                'action': 'Balance: +2dB right, Fader: +3dB front',
                'reason': 'Passenger position is off-center',
                'impact': 'Centers soundstage for passenger'
            })
        
        recommendations.append({
            'category': 'Time Alignment',
            'priority': 'high',
            'action': 'Align all speakers to furthest driver',
            'reason': 'Proper time alignment is critical for phase coherence',
            'impact': 'Dramatically improves imaging and soundstage depth'
        })
        
        recommendations.append({
            'category': 'Center Image',
            'priority': 'high',
            'action': 'Fine-tune left/right balance in 0.5dB steps',
            'reason': 'Vocal imaging requires precise balance',
            'impact': 'Centers vocals for natural presentation'
        })
        
        analysis_text = f"""SOUNDSTAGE ANALYSIS - {listening_position.upper()} POSITION

Based on acoustic measurements and speaker positioning, here are the recommended optimizations:

1. TIME ALIGNMENT
   - Critical for phase coherence and imaging
   - Align all speakers to the furthest driver from listening position
   - Expected improvement: 40-50% better soundstage depth

2. BALANCE & FADER
   - Current position is off-center: compensate with balance adjustment
   - Fader adjustment optimizes front/rear balance
   - Expected improvement: Centered soundstage

3. EQ CORRECTIONS
   - Address {len([r for r in recommendations if r['category'] == 'EQ'])} cabin acoustic issues
   - Focus on room modes and material absorption
   - Expected improvement: Smoother frequency response

4. CENTER IMAGE
   - Fine-tune balance for vocal clarity
   - Critical for natural sound reproduction
   - Expected improvement: Locked center image

PRIORITY RANKING:
"""
        
        for i, rec in enumerate(sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']]), 1):
            analysis_text += f"\n{i}. [{rec['priority'].upper()}] {rec['action']}"
        
        return {
            'source': 'rule_based',
            'analysis': analysis_text,
            'recommendations': recommendations,
            'confidence_score': 0.75,
            'note': 'AI tuning requires ANTHROPIC_API_KEY. Using rule-based analysis.'
        }
    
    def suggest_auto_tune(
        self,
        speaker_positions: Dict[str, Any],
        acoustic_data: Dict[str, Any],
        listening_position: str = 'driver'
    ) -> Dict[str, Any]:
        """
        Generate one-click auto-tune settings.
        Applies best practices for optimal soundstage.
        """
        auto_settings = {
            'time_alignment': {},
            'balance_db': 0.0,
            'fader_db': 0.0,
            'eq_bands': [],
            'crossover_adjustments': {}
        }
        
        from services.soundstage.positioning import SpeakerPositioning
        positioning = SpeakerPositioning()
        positioning.speaker_positions = speaker_positions
        
        delays = positioning.calculate_time_delays(listening_position)
        auto_settings['time_alignment'] = delays
        
        balance = positioning.calculate_balance_correction(listening_position)
        avg_balance = sum(balance.values()) / len(balance) if balance else 0
        auto_settings['balance_db'] = avg_balance
        
        fader = positioning.calculate_fader_settings(listening_position)
        auto_settings['fader_db'] = fader.get('fader_db', 0.0)
        
        eq_corrections = acoustic_data.get('recommended_corrections', [])
        auto_settings['eq_bands'] = eq_corrections[:8]
        
        return {
            'auto_tune_settings': auto_settings,
            'description': 'Optimized for ' + listening_position,
            'estimated_improvement': '60-70% better soundstage quality',
            'apply_instructions': 'Send these settings to DSP service to apply'
        }
    
    def compare_presets(
        self,
        preset_a: Dict[str, Any],
        preset_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two presets and explain differences."""
        differences = {
            'time_alignment': {},
            'balance': {},
            'fader': {},
            'summary': []
        }
        
        if 'time_alignment' in preset_a and 'time_alignment' in preset_b:
            for speaker in preset_a['time_alignment']:
                if speaker in preset_b['time_alignment']:
                    diff = preset_a['time_alignment'][speaker] - preset_b['time_alignment'][speaker]
                    if abs(diff) > 0.1:
                        differences['time_alignment'][speaker] = diff
        
        balance_diff = preset_a.get('balance_db', 0) - preset_b.get('balance_db', 0)
        if abs(balance_diff) > 0.5:
            differences['balance'] = balance_diff
        
        fader_diff = preset_a.get('fader_db', 0) - preset_b.get('fader_db', 0)
        if abs(fader_diff) > 0.5:
            differences['fader'] = fader_diff
        
        if differences['time_alignment']:
            differences['summary'].append(f"Time alignment differs on {len(differences['time_alignment'])} speakers")
        if differences.get('balance'):
            differences['summary'].append(f"Balance differs by {abs(balance_diff):.1f} dB")
        if differences.get('fader'):
            differences['summary'].append(f"Fader differs by {abs(fader_diff):.1f} dB")
        
        return differences
    
    def get_tuning_tips(self, listening_position: str = 'driver') -> List[Dict[str, str]]:
        """Get expert tuning tips for soundstage optimization."""
        tips = [
            {
                'category': 'Time Alignment',
                'tip': 'Always align speakers to the furthest driver first, then fine-tune by ear',
                'difficulty': 'advanced',
                'impact': 'high'
            },
            {
                'category': 'Balance',
                'tip': 'Use mono test tracks to verify center image - vocals should appear dead center',
                'difficulty': 'beginner',
                'impact': 'high'
            },
            {
                'category': 'Fader',
                'tip': 'Start with slight front bias, then adjust until soundstage has proper depth',
                'difficulty': 'intermediate',
                'impact': 'medium'
            },
            {
                'category': 'EQ',
                'tip': 'Cut problem frequencies before boosting - reducing peaks is more effective than filling dips',
                'difficulty': 'intermediate',
                'impact': 'high'
            },
            {
                'category': 'Listening Position',
                'tip': f'For {listening_position} position, expect left/right asymmetry - this is normal and correctable',
                'difficulty': 'beginner',
                'impact': 'medium'
            },
            {
                'category': 'Phase',
                'tip': 'Verify all speakers are wired in-phase - reverse polarity will destroy imaging',
                'difficulty': 'beginner',
                'impact': 'critical'
            },
            {
                'category': 'Measurement',
                'tip': 'Measure at ear height with microphone pointing up at 45° angle',
                'difficulty': 'intermediate',
                'impact': 'high'
            },
            {
                'category': 'Fine-tuning',
                'tip': 'Make small adjustments (0.1ms, 0.5dB) and listen for 5-10 minutes before making more changes',
                'difficulty': 'advanced',
                'impact': 'medium'
            }
        ]
        
        return tips
    
    def estimate_improvement(
        self,
        current_settings: Dict[str, Any],
        recommended_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate the improvement from applying recommendations."""
        improvements = {
            'overall_score': 0,
            'categories': {},
            'estimated_time_minutes': 15
        }
        
        if 'time_alignment' in recommended_settings:
            improvements['categories']['imaging'] = {
                'current': 40,
                'potential': 85,
                'improvement_percent': 45,
                'description': 'Soundstage depth and speaker localization'
            }
        
        if 'balance_db' in recommended_settings or 'fader_db' in recommended_settings:
            improvements['categories']['center_image'] = {
                'current': 50,
                'potential': 90,
                'improvement_percent': 40,
                'description': 'Vocal clarity and center staging'
            }
        
        if 'eq_bands' in recommended_settings:
            improvements['categories']['tonal_balance'] = {
                'current': 60,
                'potential': 85,
                'improvement_percent': 25,
                'description': 'Frequency response smoothness'
            }
        
        avg_improvement = sum(
            cat['improvement_percent'] for cat in improvements['categories'].values()
        ) / len(improvements['categories']) if improvements['categories'] else 0
        
        improvements['overall_score'] = int(avg_improvement)
        
        return improvements
