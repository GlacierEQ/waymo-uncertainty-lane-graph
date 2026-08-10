package lane

import (
	"errors"
	"regexp"
	"sort"
	"strings"
)

type EdgeState int

const (
	Free EdgeState = iota
	Unknown
	Blocked
)

var nodePattern = regexp.MustCompile(`^[A-Za-z0-9_.:/-]+$`)

type Graph struct {
	edges map[string]map[string]EdgeState
}

func New() *Graph {
	return &Graph{edges: map[string]map[string]EdgeState{}}
}

func validNode(node string) bool {
	return node != "" && nodePattern.MatchString(node)
}

func validState(state EdgeState) bool {
	return state == Free || state == Unknown || state == Blocked
}

// Add is idempotent for the exact same directed edge state and refuses
// conflicting redefinitions so topology semantics cannot depend on insertion order.
func (g *Graph) Add(a, b string, state EdgeState) error {
	if g == nil {
		return errors.New("graph is nil")
	}
	if !validNode(a) || !validNode(b) {
		return errors.New("node identifiers must be non-empty machine-safe tokens")
	}
	if !validState(state) {
		return errors.New("invalid edge state")
	}
	if g.edges == nil {
		g.edges = map[string]map[string]EdgeState{}
	}
	if g.edges[a] == nil {
		g.edges[a] = map[string]EdgeState{}
	}
	if existing, ok := g.edges[a][b]; ok {
		if existing == state {
			return nil
		}
		return errors.New("conflicting directed edge state")
	}
	g.edges[a][b] = state
	return nil
}

func (g *Graph) known(node string) bool {
	if g == nil {
		return false
	}
	if _, ok := g.edges[node]; ok {
		return true
	}
	for _, outgoing := range g.edges {
		if _, ok := outgoing[node]; ok {
			return true
		}
	}
	return false
}

func sortedNeighbors(outgoing map[string]EdgeState) []string {
	keys := make([]string, 0, len(outgoing))
	for key := range outgoing {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Shortest returns a deterministic minimum-hop route. UNKNOWN edges are
// refused unless allowUnknown is explicitly true. BLOCKED edges never route.
func (g *Graph) Shortest(src, dst string, allowUnknown bool) []string {
	if !validNode(src) || !validNode(dst) || !g.known(src) || !g.known(dst) {
		return nil
	}
	type node struct {
		id   string
		path []string
	}
	queue := []node{{src, []string{src}}}
	bestHops := map[string]int{src: 0}
	for len(queue) > 0 {
		cur := queue[0]
		queue = queue[1:]
		hops := len(cur.path) - 1
		if knownHops, ok := bestHops[cur.id]; ok && hops != knownHops {
			continue
		}
		if cur.id == dst {
			return cur.path
		}
		for _, neighbor := range sortedNeighbors(g.edges[cur.id]) {
			state := g.edges[cur.id][neighbor]
			if state == Blocked || (state == Unknown && !allowUnknown) {
				continue
			}
			newHops := hops + 1
			knownHops, seen := bestHops[neighbor]
			if seen && newHops > knownHops {
				continue
			}
			if !seen || newHops < knownHops {
				bestHops[neighbor] = newHops
			}
			path := append(append([]string{}, cur.path...), neighbor)
			queue = append(queue, node{neighbor, path})
		}
		// Keep equal-hop candidates lexicographically deterministic.
		sort.SliceStable(queue, func(i, j int) bool {
			if len(queue[i].path) != len(queue[j].path) {
				return len(queue[i].path) < len(queue[j].path)
			}
			return strings.Join(queue[i].path, "\x00") < strings.Join(queue[j].path, "\x00")
		})
	}
	return nil
}

type routeCandidate struct {
	id      string
	path    []string
	unknown int
}

func candidateLess(a, b routeCandidate) bool {
	if a.unknown != b.unknown {
		return a.unknown < b.unknown
	}
	if len(a.path) != len(b.path) {
		return len(a.path) < len(b.path)
	}
	return strings.Join(a.path, "\x00") < strings.Join(b.path, "\x00")
}

// LeastUncertain prefers fewer UNKNOWN edges, then fewer hops, then lexical
// path order. BLOCKED edges never route.
func (g *Graph) LeastUncertain(src, dst string) []string {
	if !validNode(src) || !validNode(dst) || !g.known(src) || !g.known(dst) {
		return nil
	}
	frontier := []routeCandidate{{id: src, path: []string{src}, unknown: 0}}
	best := map[string]routeCandidate{src: frontier[0]}
	for len(frontier) > 0 {
		sort.SliceStable(frontier, func(i, j int) bool { return candidateLess(frontier[i], frontier[j]) })
		cur := frontier[0]
		frontier = frontier[1:]
		currentBest, ok := best[cur.id]
		if !ok || currentBest.unknown != cur.unknown || strings.Join(currentBest.path, "\x00") != strings.Join(cur.path, "\x00") {
			continue
		}
		if cur.id == dst {
			return cur.path
		}
		for _, neighbor := range sortedNeighbors(g.edges[cur.id]) {
			state := g.edges[cur.id][neighbor]
			if state == Blocked {
				continue
			}
			unknown := cur.unknown
			if state == Unknown {
				unknown++
			}
			path := append(append([]string{}, cur.path...), neighbor)
			candidate := routeCandidate{id: neighbor, path: path, unknown: unknown}
			previous, seen := best[neighbor]
			if !seen || candidateLess(candidate, previous) {
				best[neighbor] = candidate
				frontier = append(frontier, candidate)
			}
		}
	}
	return nil
}
