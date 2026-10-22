# ResourcePilot Intake

<img src="https://raw.githubusercontent.com/kevinjylin/resourcepilotla/main/assets/avatars/intake.jpg" alt="ResourcePilot Intake" width="160">

Turns a submitted form into a validated brief for one campus service. A study-room search gets the
saved school domain, day (up to two weeks ahead), time of day, length, and group size. A housing
lookup gets the saved domain and matching criteria. The Orchestrator already reduced the one school
email to its domain; Intake never sees the part before `@`. It reports a missing or invalid detail
instead of guessing, so the Orchestrator can show the form again.

ResourcePilot takes requests only from cards and forms, never free text. Intake never contacts a
school or reads a web page.

Its profile chat shows its role and points to the ResourcePilot Orchestrator.

Protocols: Agent Chat Protocol, ResourcePilotTasks.
