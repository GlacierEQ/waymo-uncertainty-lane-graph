# ISSUE CONTRACT
## Pain
Maps are treated as truth; topology uncertainty is dropped. Duplicate/conflicting edge updates and insertion-order-dependent routing can make the same nominal graph produce different route semantics.

## Success
- Directed edges preserve `FREE | UNKNOWN | BLOCKED` as distinct states
- Exact duplicate edge declarations are idempotent; conflicting state redefinitions fail closed
- Default path search refuses `UNKNOWN` edges and always refuses `BLOCKED`
- Equal-hop path choice is deterministic and independent of edge insertion order
- Explicit uncertainty-first routing prefers fewer `UNKNOWN` edges, then fewer hops, then lexical path order
- Unknown endpoints do not create phantom self-routes
- Decision receipts bind exact topology identity and route policy
- Python and Go preserve the same core topology/routing outcomes

## Boundary
This is an independent uncertainty-topology reference mechanism. It does not certify freespace, authenticate map/sensor provenance, authorize autonomous-driving actuation, or claim Waymo affiliation/adoption.
