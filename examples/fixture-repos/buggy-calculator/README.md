# Buggy calculator fixture

This synthetic repository is reserved for the first V1 bounded-mission vertical slice. It contains one intentional defect: `apply_discount` returns the discount amount instead of the remaining price.

The fixture is not part of the root Python test suite. Its failing test is expected until a mission proposes and verifies a patch in an isolated branch workspace.
