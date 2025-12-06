#!/usr/bin/env python3
"""
Verify all generated personas have required fields
"""

import json
import os
from pathlib import Path

def verify_persona(filepath):
    """Verify a single persona file"""

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)['data']

    issues = []
    warnings = []

    # Check language field
    if 'language' not in data:
        issues.append("Missing 'language' field")
    elif data['language'] != 'en-US':
        warnings.append(f"Language is '{data['language']}' not 'en-US'")

    # Check visual_profile
    if 'visual_profile' not in data:
        issues.append("Missing 'visual_profile' field")
    else:
        vp = data['visual_profile']
        required_vp_fields = ['common_outfits', 'common_props', 'color_preferences']
        for field in required_vp_fields:
            if field not in vp:
                issues.append(f"Missing visual_profile.{field}")
            elif not vp[field]:
                warnings.append(f"Empty visual_profile.{field}")

    # Check tweet_examples have scene_hint
    if 'twitter_persona' in data and 'tweet_examples' in data['twitter_persona']:
        tweets = data['twitter_persona']['tweet_examples']
        tweets_with_scene_hint = sum(1 for t in tweets if 'scene_hint' in t)
        tweets_without = len(tweets) - tweets_with_scene_hint

        if tweets_without > 0:
            issues.append(f"{tweets_without}/{len(tweets)} tweets missing scene_hint")

        # Check scene_hint length
        short_hints = []
        for i, tweet in enumerate(tweets):
            if 'scene_hint' in tweet:
                word_count = len(tweet['scene_hint'].split())
                if word_count < 40:
                    short_hints.append((i, word_count))

        if short_hints:
            warnings.append(f"{len(short_hints)} scene_hints are very short (< 40 words)")

    return issues, warnings, data

def main():
    personas_dir = Path(__file__).parent / 'personas'

    print("🔍 Verifying All Generated Personas")
    print("=" * 70)
    print()

    all_personas = []

    # Main directory
    for f in sorted(personas_dir.glob('*_persona.json')):
        all_personas.append(('MAIN', f))

    # TMP directory
    tmp_dir = personas_dir / 'tmp'
    if tmp_dir.exists():
        for f in sorted(tmp_dir.glob('*_persona.json')):
            all_personas.append(('TMP', f))

    print(f"📊 Found {len(all_personas)} personas")
    print()

    # Statistics
    total_issues = 0
    total_warnings = 0
    perfect_count = 0

    issue_personas = []
    warning_personas = []

    for location, filepath in all_personas:
        try:
            issues, warnings, data = verify_persona(filepath)

            if issues:
                total_issues += len(issues)
                issue_personas.append((location, filepath.name, issues))
            elif warnings:
                total_warnings += len(warnings)
                warning_personas.append((location, filepath.name, warnings))
            else:
                perfect_count += 1

        except Exception as e:
            print(f"❌ {location}: {filepath.name}")
            print(f"   Error: {str(e)}")
            print()

    # Summary
    print("=" * 70)
    print("📊 Verification Summary")
    print("=" * 70)
    print()
    print(f"Total personas: {len(all_personas)}")
    print(f"✅ Perfect: {perfect_count}")
    print(f"⚠️  With warnings: {len(warning_personas)}")
    print(f"❌ With issues: {len(issue_personas)}")
    print()

    # Show issues
    if issue_personas:
        print("❌ Personas with Issues:")
        print("-" * 70)
        for location, name, issues in issue_personas:
            print(f"\n[{location}] {name}")
            for issue in issues:
                print(f"  • {issue}")
        print()

    # Show warnings
    if warning_personas:
        print("⚠️  Personas with Warnings:")
        print("-" * 70)
        for location, name, warnings in warning_personas:
            print(f"\n[{location}] {name}")
            for warning in warnings:
                print(f"  • {warning}")
        print()

    # Field statistics
    print("=" * 70)
    print("📈 Field Statistics (Sample from 3 personas)")
    print("=" * 70)
    print()

    sample_personas = all_personas[:3]
    for location, filepath in sample_personas:
        with open(filepath, 'r') as f:
            data = json.load(f)['data']

        print(f"[{location}] {filepath.name}")
        print(f"  Language: {data.get('language', 'MISSING')}")

        if 'visual_profile' in data:
            vp = data['visual_profile']
            print(f"  Visual Profile:")
            print(f"    - Outfits: {len(vp.get('common_outfits', []))} items")
            print(f"    - Props: {len(vp.get('common_props', []))} items")
            print(f"    - Colors: {len(vp.get('color_preferences', []))} items")

        if 'twitter_persona' in data:
            tweets = data['twitter_persona'].get('tweet_examples', [])
            print(f"  Tweets: {len(tweets)} examples")

            if tweets and 'scene_hint' in tweets[0]:
                hint_words = [len(t['scene_hint'].split()) for t in tweets if 'scene_hint' in t]
                avg_words = sum(hint_words) / len(hint_words) if hint_words else 0
                print(f"  Scene Hints: {len(hint_words)}/{len(tweets)} present, avg {avg_words:.0f} words")

        print()

    print("=" * 70)

    if total_issues == 0:
        print("✨ All personas passed verification!")
    else:
        print(f"⚠️  Found {total_issues} issues across {len(issue_personas)} personas")

if __name__ == '__main__':
    main()
