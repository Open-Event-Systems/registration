package logic

import (
	"os"
	"testing"

	"github.com/nikolalohinski/gonja/v2/exec"
	"gopkg.in/yaml.v3"
)

func TestLogic(t *testing.T) {
	tests := getTests()

	t.Run("test1", func(t *testing.T) {
		ctx := exec.NewContext(make(map[string]interface{}))
		test := tests["test1"]
		res := test.Evaluate(ctx)
		if res != true {
			t.Fatalf("expected true, got %v", res)
		}
	})

	t.Run("test2", func(t *testing.T) {
		ctx := exec.NewContext(make(map[string]interface{}))
		test := tests["test2"]
		res := test.Evaluate(ctx)
		if res != true {
			t.Fatalf("expected true, got %v", res)
		}
	})

	t.Run("test3", func(t *testing.T) {
		ctx := exec.NewContext(make(map[string]interface{}))
		test := tests["test3"]
		res := test.Evaluate(ctx)
		if res != false {
			t.Fatalf("expected false, got %v", res)
		}
	})

	t.Run("test4", func(t *testing.T) {
		ctx := exec.NewContext(make(map[string]interface{}))
		test := tests["test4"]
		ctx.Set("b", 2)
		res := test.Evaluate(ctx)
		if res != true {
			t.Fatalf("expected true, got %v", res)
		}
	})

	t.Run("test5", func(t *testing.T) {
		ctx := exec.NewContext(make(map[string]interface{}))
		test := tests["test5"]
		ctx.Set("a", 2)
		ctx.Set("b", 2)
		res := test.Evaluate(ctx)
		if res != true {
			t.Fatalf("expected true, got %v", res)
		}
	})
}

func getTests() map[string]Condition {
	data, err := os.ReadFile("logic_test.yml")
	if err != nil {
		panic(err)
	}

	var tests map[string]Condition
	err = yaml.Unmarshal(data, &tests)
	if err != nil {
		panic(err)
	}

	return tests
}
