package lane

type EdgeState int

const (
	Free EdgeState = iota
	Unknown
	Blocked
)

type Graph struct {
	edges map[string][]struct {
		to    string
		state EdgeState
	}
}

func New() *Graph {
	return &Graph{edges: map[string][]struct {
		to    string
		state EdgeState
	}{}}
}

func (g *Graph) Add(a, b string, s EdgeState) {
	g.edges[a] = append(g.edges[a], struct {
		to    string
		state EdgeState
	}{b, s})
}

func (g *Graph) Shortest(src, dst string, allowUnknown bool) []string {
	type node struct {
		id   string
		path []string
	}
	q := []node{{src, []string{src}}}
	seen := map[string]struct{}{src: {}}
	for len(q) > 0 {
		cur := q[0]
		q = q[1:]
		if cur.id == dst {
			return cur.path
		}
		for _, e := range g.edges[cur.id] {
			if e.state == Blocked {
				continue
			}
			if e.state == Unknown && !allowUnknown {
				continue
			}
			if _, ok := seen[e.to]; ok {
				continue
			}
			seen[e.to] = struct{}{}
			np := append(append([]string{}, cur.path...), e.to)
			q = append(q, node{e.to, np})
		}
	}
	return nil
}
