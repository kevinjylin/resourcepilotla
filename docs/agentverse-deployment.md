# Agentverse connection and deployment

## Local Inspector and Mailbox (testing)

1. Run `make start`, then `make profiles`.
2. Sign in to [Agentverse](https://agentverse.ai/).
3. Open every Inspector URL that `make profiles` printed: all eight agents.
4. Confirm the address, click **Connect**, and choose **Mailbox**.
5. On each profile, confirm that the README and the Chat Protocol and `ResourcePilotTasks`
   manifests are there.
6. Open each profile chat and check that it answers with its status card.

Agents send each other messages through their Mailboxes, so all eight must be connected before a
request can complete. Check the current Mailbox limit on your Agentverse plan before connecting
them. If Inspector cannot reach a local agent in a recent Chrome release, allow Local Network
Access for the Agentverse site, then retry once.

Upgrading from the 15-agent version? Keep your `.env`. The agents keep their seeds, so their
addresses and profiles stay the same. `make verify` names the leftover settings for agents that no
longer run. You can disconnect those agents' Mailboxes in Agentverse to free the slots.

Adding the Emergency Dispatcher to an existing `.env`? Add its ElevenLabs and demo-number settings
(see [agents/emergency/README.md](../agents/emergency/README.md)), then run
`make bootstrap-missing`. It adds the Dispatcher's identity without changing any other seed. If
port 8007 is already used by another agent in that `.env` (older layouts used 8007 for Memory and
Audit), it picks the next free port. Then open its Inspector link and connect its Mailbox.

In Docker, every published port is bound to host loopback and targets container port `18000`. A
small TCP relay there forwards to the uAgent through container loopback. uAgents accepts Inspector
`/connect` and `/messages` calls only from local callers, and Docker NAT would otherwise present
your browser as a remote caller. Never expose the relay publicly.

Mailbox relays and queues messages for a local agent. It does not keep a sleeping laptop online.

## A persistent submission

Mailbox queues messages for an unavailable runtime; it does not run Python for a sleeping laptop.
For a real always-on submission, first connect all eight Mailboxes locally, then deploy the same
seeds with the production Compose file:

```bash
# On an always-on Docker host, with the ignored .env copied through a secret channel:
export RESOURCEPILOT_DATABASE_URL='postgresql://...managed-postgres...'
make deploy-check
make deploy-up
docker compose -f compose.deploy.yml ps
```

`compose.deploy.yml` intentionally has no local Postgres container and publishes no ports. Each
agent receives through its already-connected Mailbox using outbound https. The local
`docker-compose.yml` remains the Inspector/bootstrap environment and binds every published port to
loopback only.

- Keep the same eight seeds so addresses and profile ownership do not change. Store the ignored
  `.env`, `RESOURCEPILOT_DATABASE_URL`, and ElevenLabs settings in the host's secret manager.
- Use managed Postgres with TLS and backups. `RESOURCEPILOT_DATABASE_URL` is mapped to the agents'
  `DATABASE_URL`; startup fails instead of silently using process-local memory when it is missing.
- Allow outbound https. The Campus Researcher, Campus Rooms, and Verification read IPEDS (the
  Urban Institute Education Data API), schools' websites, and LibCal. They need no API keys. The
  Emergency Dispatcher calls the ElevenLabs API and needs `ELEVENLABS_API_KEY`. The Orchestrator
  calls `api.stripe.com` and the Fetch testnet only when the paid hall match is set up; keep
  `STRIPE_SECRET_KEY` in the secret manager too.
- Card pictures load in the student's browser from `CARD_IMAGE_BASE`, this repository's
  `assets/` by default. If you deploy from a fork, push `assets/` and point it there, or leave it
  empty to send cards without images.
- Check `make deploy-logs`, re-open every profile after deploying, then test the first school card,
  a study-room search through the re-check, a tappable booking link, a housing lookup, and
  **My bookings**.
- Capture the shared ASI:One chat link with the Orchestrator and all eight profile links for
  Devpost.

Do not upload this repository unchanged as one Agentverse Hosted Agent. It is eight independent
processes plus `asyncpg`, live-network dependencies, and shared Postgres. The supported path here
is eight external, always-on mailbox runtimes. A Hosted Agent port would require packaging and
testing each role separately and retaining the same shared-store and protocol behavior.

## Manual steps are intentional

This repository does not automate any of the following, because each needs the owner in the
browser:

- Agentverse sign-in
- profile ownership
- Mailbox approval
- publishing a shared chat
- the ElevenLabs agent, the Twilio or Telnyx number, and the demo contact's phone
