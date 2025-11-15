#!/usr/bin/env python3
"""
Test Script for Advanced DSP Control Center
Verifies all features are functional
"""

import requests
import json
import time

BASE_URL = "http://localhost:8100"

def test_health():
    """Test health endpoint."""
    print("🧪 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    assert data['ok'] == True
    assert data['service'] == 'advanced_dsp_control_center'
    assert data['port'] == 8100
    print("✅ Health endpoint OK")
    return data

def test_eq_info():
    """Test EQ band information."""
    print("\n🧪 Testing EQ band info...")
    response = requests.get(f"{BASE_URL}/api/eq/info")
    data = response.json()
    assert data['ok'] == True
    assert data['total_bands'] == 31
    print(f"✅ EQ Info OK - {data['total_bands']} bands available")
    return data

def test_eq_create():
    """Test EQ curve creation."""
    print("\n🧪 Testing EQ curve creation...")
    payload = {
        'gains': {
            '63': 3.0,
            '125': 2.0,
            '1000': -1.0,
            '8000': 2.5
        },
        'q_factor': 1.41,
        'channel': 'all'
    }
    response = requests.post(f"{BASE_URL}/api/eq/create", json=payload)
    data = response.json()
    assert data['ok'] == True
    assert len(data['eq_curve']) > 0
    print(f"✅ EQ Creation OK - {len(data['eq_curve'])} bands configured")
    print(f"   Headroom recommendation: {data['headroom_recommendation']['reduce_master_volume_db']:.1f} dB")
    return data

def test_cabin_correction():
    """Test Sonic cabin correction."""
    print("\n🧪 Testing Sonic cabin correction...")
    eq_curve = [
        {'frequency': 63, 'gain_db': 0.0, 'q_factor': 1.41},
        {'frequency': 1000, 'gain_db': 0.0, 'q_factor': 1.41},
        {'frequency': 8000, 'gain_db': 0.0, 'q_factor': 1.41}
    ]
    payload = {'eq_curve': eq_curve}
    response = requests.post(f"{BASE_URL}/api/eq/cabin-correction", json=payload)
    data = response.json()
    assert data['ok'] == True
    print("✅ Cabin Correction OK")
    return data

def test_crossover():
    """Test crossover creation."""
    print("\n🧪 Testing crossover configurations...")
    
    # Test 2-way
    payload = {'frequency': 2500, 'slope_db': 24, 'filter_type': 'linkwitz_riley'}
    response = requests.post(f"{BASE_URL}/api/crossover/create/2-way", json=payload)
    data = response.json()
    assert data['ok'] == True
    print(f"✅ 2-way Crossover OK - {data['crossover_config']['configuration']}")
    
    # Test 3-way
    payload = {'low_mid_freq': 250, 'mid_high_freq': 2500, 'slope_db': 24}
    response = requests.post(f"{BASE_URL}/api/crossover/create/3-way", json=payload)
    data = response.json()
    assert data['ok'] == True
    print(f"✅ 3-way Crossover OK")
    
    # Test 4-way
    payload = {'sub_low_freq': 80, 'low_mid_freq': 250, 'mid_high_freq': 2500, 'slope_db': 24}
    response = requests.post(f"{BASE_URL}/api/crossover/create/4-way", json=payload)
    data = response.json()
    assert data['ok'] == True
    print(f"✅ 4-way Crossover OK")
    
    return data

def test_time_alignment():
    """Test time alignment calculation."""
    print("\n🧪 Testing time alignment...")
    payload = {
        'speaker_distances': {
            'front_left': 36,
            'front_right': 36,
            'rear_left': 60,
            'rear_right': 60,
            'subwoofer': 84
        },
        'listening_position': 'driver',
        'distance_unit': 'inches'
    }
    response = requests.post(f"{BASE_URL}/api/time-alignment/calculate", json=payload)
    data = response.json()
    assert data['ok'] == True
    print(f"✅ Time Alignment OK - {len(data['time_alignment']['speakers'])} speakers configured")
    return data

def test_sonic_defaults():
    """Test Sonic default positions."""
    print("\n🧪 Testing Sonic default speaker positions...")
    response = requests.get(f"{BASE_URL}/api/time-alignment/sonic-defaults/driver")
    data = response.json()
    assert data['ok'] == True
    print("✅ Sonic Defaults OK")
    return data

def test_bass_management():
    """Test bass management."""
    print("\n🧪 Testing bass management...")
    payload = {
        'level_db': 3.0,
        'subsonic_filter_hz': 25,
        'boost_db': 4.0,
        'phase_degrees': 0
    }
    response = requests.post(f"{BASE_URL}/api/bass/settings", json=payload)
    data = response.json()
    assert data['ok'] == True
    print("✅ Bass Management OK")
    return data

def test_loudness():
    """Test loudness compensation."""
    print("\n🧪 Testing loudness compensation...")
    payload = {
        'enabled': True,
        'compensation_curve': 'iso226'
    }
    response = requests.post(f"{BASE_URL}/api/loudness/settings", json=payload)
    data = response.json()
    assert data['ok'] == True
    print("✅ Loudness Compensation OK")
    return data

def test_spectrum_analyzer():
    """Test spectrum analyzer."""
    print("\n🧪 Testing spectrum analyzer...")
    response = requests.get(f"{BASE_URL}/api/analyzer/spectrum?signal_type=music&include_peaks=true")
    data = response.json()
    assert data['ok'] == True
    assert len(data['spectrum']['bands']) == 31
    print(f"✅ Spectrum Analyzer OK - {len(data['spectrum']['bands'])} bands")
    return data

def test_presets():
    """Test preset management."""
    print("\n🧪 Testing preset management...")
    
    # List presets
    response = requests.get(f"{BASE_URL}/api/presets")
    data = response.json()
    assert data['ok'] == True
    print(f"✅ Preset Listing OK - {data['count']} presets available")
    
    # Get specific preset
    response = requests.get(f"{BASE_URL}/api/presets/flat")
    data = response.json()
    assert data['ok'] == True
    print(f"✅ Preset Retrieval OK - {data['preset']['name']}")
    
    # Save preset
    payload = {
        'preset_id': 'test_preset',
        'name': 'Test Preset',
        'description': 'Automated test preset'
    }
    response = requests.post(f"{BASE_URL}/api/presets/save", json=payload)
    data = response.json()
    assert data['ok'] == True
    print("✅ Preset Save OK")
    
    return data

def test_android_export():
    """Test Android configuration export."""
    print("\n🧪 Testing Android export...")
    response = requests.post(f"{BASE_URL}/api/export/android-full")
    data = response.json()
    assert data['ok'] == True
    assert 'android_config' in data
    print("✅ Android Export OK")
    return data

def run_all_tests():
    """Run all DSP tests."""
    print("=" * 60)
    print("🎚️  Advanced DSP Control Center - Test Suite")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health()
        test_eq_info()
        
        # EQ tests
        test_eq_create()
        test_cabin_correction()
        
        # Crossover tests
        test_crossover()
        
        # Time alignment tests
        test_time_alignment()
        test_sonic_defaults()
        
        # Bass and loudness tests
        test_bass_management()
        test_loudness()
        
        # Analyzer tests
        test_spectrum_analyzer()
        
        # Preset tests
        test_presets()
        
        # Export tests
        test_android_export()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 DSP Control Center is fully functional on port 8100")
        print("🎧 Ready for professional audio tuning!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise

if __name__ == '__main__':
    run_all_tests()
