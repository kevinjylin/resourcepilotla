# Demo script (about three minutes)

Before recording:

1. Run `make start` and connect all eight agents with Mailbox.
2. Open ASI:One and start a chat with the ResourcePilot Orchestrator.
3. Have a school email ready at a LibCal school for the room steps (for example Purdue, UCR, or
   UCLA). Know one school that gets the paste-link card (for example MIT), and have its library's
   room-booking link ready. Try both the day before: library sites change.
4. For the taken-room reroute, you need the slot to be taken between the carousel and the
   re-check. The honest way is to book that slot yourself on the school's booking page, in another
   tab with your own school sign-in, and cancel it after recording. If you cannot, use the test in
   step 3 instead.
5. For the optional emergency step, finish the setup in
   [agents/emergency/README.md](../agents/emergency/README.md) and set `EMERGENCY_DEMO_TO_NUMBER`
   to a teammate's phone. Place one test call the day before. Each call is billed to your
   ElevenLabs and phone-provider accounts. Skip the step if this is not set up.

The optional steps add about a minute.

## 1. Set the school and open the services menu (20 s)

Say "hi". The Orchestrator first asks for the school. Enter the school email once and point out
that only its domain is retained. The native carousel then shows **Study rooms**, **Health &
wellness**, **Campus housing**, **Emergency (demo)**, **My bookings**, and **Change school**. The
988 crisis line is in the subtitle. Swipe through the service art. Type a sentence instead, and it
answers with the same menu: every request starts from a card, never an inferred consequential
action.

## 2. A real study room at any school (55 s)

Press **Explore** on **Study rooms**. Show the illustrated overview, then press **Set preferences**.
The overview names the saved school. Enter a day, a time of day, a duration, and the group size in
the native form, then press **Find open rooms**.

As the progress relay updates its structured **Done / Now / Next** list, say: "Intake keeps only
the domain. The Campus Researcher matched
the school in IPEDS and found its LibCal site." For Purdue, that site lives at
`calendar.lib.purdue.edu`, not on `libcal.com`. "Campus Rooms, a separate agent, is reading which
rooms are open right now, and Verification checks every offer before the Planner ranks them."

The carousel shows real rooms, earliest first, each with a **Live · LibCal** badge. Press **View
room** on one, then **Re-check this room**. Campus Rooms reads that slot again, and the **Your
booking link** card arrives with the room, the time, and the school's own link. Say: "It's free,
and ResourcePilot never reserves the room. You book it with your own sign-in." Open the duplicate
markdown link above the card to show that links are tappable in ASI:One.

## 3. A room taken during the re-check (30 s)

Press **Find another room** and run the same search. Open a room, and before you re-check it, book
that slot yourself in the other tab. Back in ASI:One, press **Re-check this room**. The
Orchestrator says "Someone just booked that time; pick another room", the Planner runs again
without that room, and a new carousel shows the other open rooms. Say: "Only that room was
dropped, not the whole search." Cancel your booking in the other tab afterwards.

If you cannot take a slot live, show the same path in the test suite instead:

```bash
uv run pytest tests/test_network.py -k taken -v
```

## 4. No booking system found: the paste-link card (25 s)

Use **Main menu → Change school** and switch to an MIT email. Start a room search. The Researcher
finds no system it
recognizes, so it asks instead of guessing: a card with one field for the room-booking link.
Paste the library's
booking link and press **Check this link**. The Researcher checks the pasted link with the same
rules as one it found itself. Optional: paste a link on another domain first, and the same card
comes back with the reason.

Optional (30 s): switch back to Purdue from **Change school**, press **Main menu**, then **Explore**
on **Health & wellness**, review the safety overview, and fill the form. The hub starts with 988
and 911 and shows verified
room/event counts. Select **Events this week** in the choice grid, open it, then tap a list row to
show its native detail page and official RSVP link. Return to the hub, choose **Open wellness
rooms**, and show the native room carousel. Say: "It never asks about your health. The crisis line
is static, so it shows even when a school has nothing to find."

## 5. Campus housing (25 s)

Press **Main menu**, then **Explore** on **Campus housing** and press **Set preferences**. Using the
saved school, pick **Incoming first-year**, tick **Air conditioning**, and
press **Find housing**. If payments are set up, the hall-match offer appears first: press
**Unlock my hall match** and pay in ASI:One's
payment panel with Stripe's test card `4242 4242 4242 4242` (any future date and CVC) or testnet
FET. Say: "The facts are free. The match is the one paid step, in test mode, and the Orchestrator
checks the payment with Stripe itself before the Planner starts." The carousel then
shows each hall the school lists, matches first, with photos where the school has them. Open one:
style, who it's for, rooms, features, price, and how it fits each criterion, with the apply link.
Say: "Every detail comes from the hall's own page, re-opened by Verification. If the page doesn't
say, it shows 'not listed'. You apply on the school's site." Press **Show all** to see the halls
your criteria ruled out, and **Housing facts** for IPEDS numbers and the portal.

## 6. Optional: Emergency (demo) (30 s)

Put your teammate's phone on speaker, near the microphone. Press **Main menu**, then **Explore** on
**Emergency (demo)**. Point out the illustrated demo-only safety page, press **Set preferences**,
fill the native form, and tick **I understand: demo only**. On the native review card, point at
"not 911" and the masked number, which shows only the last four digits. Say: "It can only call our
demo contact, and the voice opens by saying this is a demo drill." Press **Call now**. The phone
rings, and the voice reports the emergency as the student asking for help. Your teammate answers
as the dispatcher and asks a question or two; the voice answers only from the form, then thanks
them and hangs up. After the call, press **Check the call** to show the summary and transcript.
Say: "One press places one call, and it is never retried. In a real emergency, call 911."

## 7. My bookings (10 s)

Press **Main menu**, then **Open** on **My bookings**. The room from step 2 appears in a carousel. Press
**Open booking** to reconstruct its booking-link detail card.

## 8. An agent profile chat (15 s)

Open the Campus Rooms profile on Agentverse. Show its README and its Chat and Tasks manifests, then
send it a message. It answers with its status card, which names its role and repeats the
Orchestrator's Agentverse profile as a tappable link above the card. Say: "Eight separate agents,
each with its own address and job."

## 9. Close (5 s)

Say: "Free study rooms at any school, re-checked live, and housing facts with official links. The
only payment is the optional hall match, in test mode, and it never pays your school. No
reservations, and you always book with your own sign-in."
