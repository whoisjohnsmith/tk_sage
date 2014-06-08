tk_sage v2.0 or something
=========================

Sim of a TK sage

Simulator for TK sage damage.

Guidelines:
- Play with sage.xml and rotation.xml files
- Ignore primary/secondary stats and insert directly your force sheet stats... hopefully in the near future I will have time to calculate these from your primary/secondary stats
- Please READ the following comments

Some comments:

- TK Throw is by default a psychic project channel
- Turbulence is by default an auto-crit
- Wave hits only one target
- DOT damages are calculated instantly
- Also abilities cooldowns are ignored, which togehter with the comment above it is up to YOU to write a viable rotation
- Ignore potency/alacrity but take into account (common) skill tree buffs for each ability
- Pending to take into account defence/armor of mob and misses maybe
- The Damage_Profile class needs further work in order to be able to report the critical ratio of the rotation
- Force sheet values are taken directly from file at the moment and not calculated from primary/secondary stats

Feedback:
- Thank you for trying it. If you want to leave any feedback, comments or bug reports please post in the following thread:
http://www.swtor.com/community/showthread.php?t=745689
- I will investigate how github handles issues reports