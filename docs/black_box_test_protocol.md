# Navigators: Black-Box User Test Protocol (v1.0)

## Objective
The goal of this test is to observe a new user interacting with the Navigators system without any prior knowledge of how the underlying technology works. This will expose usability flaws, onboarding friction, and unexpected edge cases in the real world.

## Preparation
1. **Device Preparation:** Install `app-release.apk` on a fresh Android device. Do not grant permissions in advance.
2. **Mount:** Provide the user with a standard dashboard or windshield mount.
3. **Route:** Select a route that includes at least one GNSS-denied environment (e.g., a tunnel, an underground parking garage, or a dense urban canyon).
4. **Environment:** Sit in the passenger seat.

## The Instructions
Give the phone to the user. Tell them **only** the following:

> "I need you to use this app, Navigators, for our trip to [Destination]. Please set it up and let's go."

Do **not** explain:
- That it uses AI or IMU sensors.
- How to calibrate it.
- Why it needs specific permissions.
- That the phone must be mounted rigidly.

## Observation Scorecard (To be filled by the observer)

### 1. Onboarding & Permissions
- [ ] Did the user understand why Background Location was requested?
- [ ] Did the user understand why Sensor permissions were requested?
- [ ] Did they hesitate or deny any permissions? (Note which ones)

### 2. Mounting & Calibration
- [ ] Did the user mount the phone rigidly without prompting?
- [ ] Did they hold the phone in their hand? (If they hold it, observe how the system degrades, then gently suggest mounting it after 5 minutes).
- [ ] Did they find the "Calibration" screen?
- [ ] Did they understand that the vehicle needed to be stationary for calibration?

### 3. Navigation & Outage Handling
- [ ] As you entered the GNSS-denied zone, did the user notice the state change to `DEAD_RECKONING`?
- [ ] Was the UI clear that the system was still tracking them?
- [ ] Did the speed estimation feel accurate to the user? (Ask them at the end).
- [ ] When exiting the tunnel, did the system recover smoothly or did it "snap/teleport" violently?

### 4. Post-Session Sync
- [ ] Did the user understand how to end the session?
- [ ] Did the session successfully upload to the cloud backend?

## Debrief
At the end of the trip, ask the user:
1. "What was the most confusing part of setting up the app?"
2. "Did you trust the navigation when we lost GPS in the tunnel?"
3. "Would you change anything about the interface?"

## Next Steps
File any friction points, UI confusions, or catastrophic navigation failures as GitHub Issues. These observations will form the backlog for the **v1.1.0** release.
