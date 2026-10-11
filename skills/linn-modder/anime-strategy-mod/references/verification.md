# Strategy-mod verification

Read when checking prepared assets, formats or runtime results. Follow the user's requested scope and validation level.

## Verification

Offline checks can establish file dimensions, alpha, encoding, manifest integrity,
descriptor structure and deterministic conversion round trips. Record those checks
in MODLOG.md. Record runtime verification separately; if no game was run, retain
`not-tested-in-game`. Never imply that a planning-only profile is a working loader.

## CK3 dynamic-description warning

For event descriptions or a startup stall, read the verified
[CK3 1.20.0.4 loading failure](ck3-dynamic-description-loading-failure.md).
In that build, `triggered_desc` accepts only `trigger` and `desc` as direct
children. A direct `first_valid` child caused repeated parser errors and blocked
startup despite passing brace, reference and package checks. Check the generated
event files as well as the generator; confirm that the actual game reaches its
main menu before marking startup verified. Main-menu success does not validate
the event's in-game display or gameplay effects.
