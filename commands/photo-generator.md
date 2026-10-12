---
description: Set up and run AI image generation (local ComfyUI/SDXL rig or hosted image API) for identity-consistent images. Invoke only as /photo-generator <subject + direction>.
---

# Photo-Generator

Explicit-invocation only; costs nothing until you type it. Read `docs/rulebook/photo-generator.md` (in a global install, `~/.config/opencode/docs/rulebook/photo-generator.md`) and execute it end to end.

Keep the consent, rights, provenance, license, and retention gates yourself; they are never delegated. Delegate the mechanical work (environment setup, model downloads, runner scripts) to `builder` in bounded steps. Review output against the pipeline's done-check, then stop. Never commit; offer the outputs for review.
