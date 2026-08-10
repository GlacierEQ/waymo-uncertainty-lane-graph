package lane

import (
	"reflect"
	"testing"
)

func mustAdd(t *testing.T, g *Graph, a, b string, state EdgeState) {
	t.Helper()
	if err := g.Add(a, b, state); err != nil {
		t.Fatalf("Add(%q,%q,%v): %v", a, b, state, err)
	}
}

func TestUnknownBlockedByDefault(t *testing.T) {
	g := New()
	mustAdd(t, g, "A", "B", Free)
	mustAdd(t, g, "B", "C", Unknown)
	if g.Shortest("A", "C", false) != nil {
		t.Fatal("should refuse unknown")
	}
	if got := g.Shortest("A", "C", true); !reflect.DeepEqual(got, []string{"A", "B", "C"}) {
		t.Fatalf("%v", got)
	}
}

func TestBlockedNeverRoutes(t *testing.T) {
	g := New()
	mustAdd(t, g, "A", "B", Blocked)
	if g.Shortest("A", "B", true) != nil {
		t.Fatal("blocked edge routed")
	}
	if g.LeastUncertain("A", "B") != nil {
		t.Fatal("blocked edge routed in least-uncertain mode")
	}
}

func TestDuplicateIdempotentAndConflictRefused(t *testing.T) {
	g := New()
	mustAdd(t, g, "A", "B", Free)
	mustAdd(t, g, "A", "B", Free)
	if err := g.Add("A", "B", Blocked); err == nil {
		t.Fatal("conflicting edge state must refuse")
	}
	if got := g.Shortest("A", "B", false); !reflect.DeepEqual(got, []string{"A", "B"}) {
		t.Fatalf("%v", got)
	}
}

func TestShortestIsInsertionOrderIndependent(t *testing.T) {
	first := New()
	mustAdd(t, first, "A", "C", Free)
	mustAdd(t, first, "C", "D", Free)
	mustAdd(t, first, "A", "B", Free)
	mustAdd(t, first, "B", "D", Free)

	second := New()
	mustAdd(t, second, "B", "D", Free)
	mustAdd(t, second, "A", "B", Free)
	mustAdd(t, second, "C", "D", Free)
	mustAdd(t, second, "A", "C", Free)

	want := []string{"A", "B", "D"}
	if got := first.Shortest("A", "D", false); !reflect.DeepEqual(got, want) {
		t.Fatalf("first=%v", got)
	}
	if got := second.Shortest("A", "D", false); !reflect.DeepEqual(got, want) {
		t.Fatalf("second=%v", got)
	}
}

func TestLeastUncertainPrefersFreeRoute(t *testing.T) {
	g := New()
	mustAdd(t, g, "A", "X", Unknown)
	mustAdd(t, g, "X", "D", Free)
	mustAdd(t, g, "A", "B", Free)
	mustAdd(t, g, "B", "C", Free)
	mustAdd(t, g, "C", "D", Free)

	if got := g.Shortest("A", "D", true); !reflect.DeepEqual(got, []string{"A", "X", "D"}) {
		t.Fatalf("shortest=%v", got)
	}
	if got := g.LeastUncertain("A", "D"); !reflect.DeepEqual(got, []string{"A", "B", "C", "D"}) {
		t.Fatalf("least uncertain=%v", got)
	}
}

func TestUnknownEndpointDoesNotCreatePhantomRoute(t *testing.T) {
	g := New()
	if got := g.Shortest("A", "A", true); got != nil {
		t.Fatalf("phantom route=%v", got)
	}
	if got := g.LeastUncertain("A", "A"); got != nil {
		t.Fatalf("phantom least-uncertain route=%v", got)
	}
}

func TestInvalidInputsRefuse(t *testing.T) {
	g := New()
	if err := g.Add("", "B", Free); err == nil {
		t.Fatal("empty node accepted")
	}
	if err := g.Add("bad node", "B", Free); err == nil {
		t.Fatal("unsafe node accepted")
	}
	if err := g.Add("A", "B", EdgeState(99)); err == nil {
		t.Fatal("invalid state accepted")
	}
}
