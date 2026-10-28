# Forms, Actions, and Feedback

Use for forms, buttons, validation, dialogs, alerts, snackbars, uploads, tooltips, and progress.

## Forms

- Put labels above inputs.
- Keep labels left-justified and easy to scan.
- Use hint text when input expectations need clarification.
- Search fields need labels, even if visually hidden.
- Search buttons should be real submit buttons and include the word “Search” for assistive tech.
- Ask for files only when required.
- State file size/type restrictions clearly.
- Prefer one file per input unless multi-file upload is needed.
- File inputs need explicit labels and should work if enhancements fail.

## Input patterns

- Collect address parts separately only when structured address data is needed.
- If not, use a simpler freeform address field.
- Input masks should allow paste, correction, and mobile entry.
- U.S. ZIP guidance should support five- and nine-digit codes.
- Date inputs should support typed `MM/DD/YYYY`.
- Use calendar pickers when scheduling context or day of week matters.
- Use simple date entry when users already know the date.

## Choice controls

- Radio buttons: one choice from a small set.
- Checkboxes: many choices, optional choices, or yes/no acknowledgement.
- Select: use sparingly, mainly for about 7–15 options when space is limited.
- Combo box: use when options exceed about 15 and scrolling is hard.
- Do not use multi-select if checkboxes would be clearer.

## Buttons

- Use buttons for actions.
- Use links for navigation.
- Use primary buttons for the main action.
- Use outline buttons for secondary actions on the current page.
- Use inverse/light buttons only on dark backgrounds.
- Button labels should be short, explicit, sentence case, and verb-led.
- Avoid too many competing buttons.
- Buttons must look selectable and have visible focus states.
- Show distinct default, hover, active, focus, disabled, and soft-disabled states.

## Dialogs and destructive actions

- Confirm important actions such as save, submit, update, upload, and delete.
- Destructive actions require clear confirmation with cancel and proceed choices.
- Use modals sparingly.
- Users should trigger modals; avoid surprise interruptions.
- Do not put large complex forms in modals.
- Provide an obvious close path, including an `X` when expected.
- If users must decide before continuing, intentionally disable dismiss-without-choice.
- Dialog buttons should name outcomes, not use vague “Yes” or “No”.

## Alerts, validation, snackbars, progress

- Put critical static system notices in prominent alerts near the top.
- Group related alert messages instead of stacking many alerts.
- Avoid emergency colors unless the situation warrants them.
- Prefer inline validation errors, especially on long forms.
- Use snackbars only for low-risk, non-blocking feedback.
- Do not use snackbars for feedback users cannot afford to miss.
- Auto-dismiss snackbar content should also appear inline or near the triggering action.
- Progress indicators need a clear label describing what is happening and what content is affected.
- Standard date display is `MM/DD/YYYY` unless requirements say otherwise.

## Tooltips

- Tooltips are progressive enhancement, not primary content.
- Use only brief, non-critical helper text.
- Tooltip triggers must be keyboard reachable.
- Keep tooltip trigger markup simple.
