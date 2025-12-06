# Persona Templates

This directory contains high-quality persona templates that can be loaded using the **PersonaTemplateLoader** node.

## What are Templates?

Templates are pre-generated, high-quality personas that serve as:
- **Reference examples** for learning persona structure
- **Starting points** for creating similar personas
- **Quality benchmarks** for comparison

## How to Use Templates

### 1. Load as Reference
```
PersonaTemplateLoader (mode: reference)
   ’ PersonaPreview (study structure)
   ’ PersonaQualityChecker (see quality score)
```

### 2. Customize Template
```
PersonaTemplateLoader (mode: editable_copy, customize name/age)
   ’ PersonaTweetRegenerate (refresh some tweets)
   ’ PersonaSocialGenerator (add new relationships)
   ’ PersonaSaver (save as new persona)
```

## Creating Your Own Templates

Save any high-quality persona (85+ score) as a template:

1. Generate a persona using the full pipeline
2. Use PersonaQualityChecker to verify score e 85
3. Save with PersonaSaver to `personas/` directory
4. Copy the best ones to this `templates/` directory
5. They will appear in PersonaTemplateLoader dropdown

## Available Templates

Currently, the system includes:
- **Reference example**: `examples/bdsm_sub_kitten.json` (can be loaded if no templates exist)

You can create templates for different persona types:
- BDSM personas (sub, dom, switch)
- Fitness personas (gym girl, yoga instructor)
- Artist personas (painter, photographer)
- Professional personas (office worker, entrepreneur)
- Student personas (college, high school)

## Template Quality Standards

A good template should have:
-  **Quality score**: 85-95
-  **Total lines**: 800-1000
-  **Tweets**: 14+ with detailed scene_hints
-  **Social network**: 2-3 detailed friends with 150+ word stories
-  **Authenticity**: Complete language_authenticity and strategic_flaws
-  **Character book**: 5-8 detailed knowledge entries
-  **Visual profile**: Extracted common outfits, props, colors
-  **Consistency**: All parts align with core persona

## Tips for Template Creation

1. **Start with a clear concept**: BDSM sub, fitness influencer, lonely office worker, etc.
2. **Use high-quality portraits**: Clear, well-lit photos that show personality
3. **Follow complete workflow**: Image ’ Core ’ Strategy ’ Tweets ’ Social ’ Authenticity ’ Visual ’ Book ’ Merge
4. **Iterate until perfect**: Use PersonaTweetRegenerate to refine weak tweets
5. **Test quality**: Should score 85+ on PersonaQualityChecker
6. **Save multiple variants**: Create a family of related personas

## Example Workflow for Creating Template

```
PersonaImageInput (high-quality portrait)
   “
PersonaCoreGenerator
   “
PersonaTweetStrategyGenerator
   “
PersonaTweetGenerator
   “
PersonaSocialGenerator
   “
PersonaAuthenticityGenerator
   “
PersonaVisualProfileExtractor
   “
PersonaCharacterBookGenerator
   “
PersonaMerger
   “
PersonaQualityChecker (verify 85+)
   “
PersonaSaver ’ Copy to templates/
```

## Organizing Templates

Suggested naming convention:
- `{type}_{name}_persona.json`
- Examples:
  - `bdsm_sub_kitten_persona.json`
  - `fitness_gym_emily_persona.json`
  - `artist_painter_sophia_persona.json`
  - `lonely_office_olivia_persona.json`

## Template Metadata

Consider adding a `è` field to your templates with:
- Creation date
- Generator version
- Quality score
- Intended use case
- Special features

Example:
```json
{
  "è": "High-quality BDSM sub persona. Score: 92. Created: 2024-01. Features: detailed kink knowledge, realistic typos, rich social network. Use as reference for similar personas."
}
```
