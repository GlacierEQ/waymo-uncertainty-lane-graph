package lane

import "testing"

func TestUnknownBlocked(t *testing.T) {
	g := New()
	g.Add("A", "B", Free)
	g.Add("B", "C", Unknown)
	if g.Shortest("A", "C", false) != nil {
		t.Fatal("should refuse unknown")
	}
	p := g.Shortest("A", "C", true)
	if len(p) != 3 {
		t.Fatal(p)
	}
}
