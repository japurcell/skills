# Model the Domain

When phase checks or mutations spread across callers, model the transitions in one place. A state machine can express which transitions are legal, a registry can own dispatch, and a reducer can own updates. Introduce the model when it removes branching callers would otherwise repeat.

Source: [upstream principle-model-the-domain](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-model-the-domain/SKILL.md)
