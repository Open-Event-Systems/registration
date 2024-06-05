package logic

import (
	"fmt"

	"github.com/nikolalohinski/gonja/v2"
	"github.com/nikolalohinski/gonja/v2/exec"
	"github.com/nikolalohinski/gonja/v2/loaders"
	"github.com/nikolalohinski/gonja/v2/nodes"
	"github.com/nikolalohinski/gonja/v2/parser"
	"github.com/nikolalohinski/gonja/v2/tokens"
	"gopkg.in/yaml.v3"
)

type Evaluable interface {
	Evaluate(context *exec.Context) any
}

type ValueOrEvaluable struct {
	value     any
	evaluable Evaluable
}

type Or struct {
	Or []ValueOrEvaluable `yaml:"or"`
}

type And struct {
	And []ValueOrEvaluable `yaml:"and"`
}

type Expression struct {
	source string
	expr   *nodes.Expression
}

type Condition struct {
	expressions []ValueOrEvaluable
}

func (o *Or) Evaluate(context *exec.Context) any {
	for _, item := range o.Or {
		if asBool(item.Evaluate(context)) {
			return true
		}
	}
	return false
}

func (a *And) Evaluate(context *exec.Context) any {
	for _, item := range a.And {
		if !asBool(item.Evaluate(context)) {
			return false
		}
	}
	return true
}

func (c *Condition) Evaluate(context *exec.Context) any {
	for _, item := range c.expressions {
		if !asBool(item.Evaluate(context)) {
			return false
		}
	}
	return true
}

func (c *Condition) EvaluateBool(context *exec.Context) bool {
	res := c.Evaluate(context)
	return asBool(res)
}

func (c *Condition) UnmarshalYAML(value *yaml.Node) error {
	var err error
	var asSlice []ValueOrEvaluable
	err = value.Decode(&asSlice)
	if err == nil {
		*c = Condition{
			expressions: asSlice,
		}
		return nil
	}

	var asScalar ValueOrEvaluable
	err = value.Decode(&asScalar)
	if err == nil {
		*c = Condition{
			expressions: []ValueOrEvaluable{asScalar},
		}
		return nil
	}
	return err
}

func (e *Expression) Evaluate(ctx *exec.Context) any {
	if e.expr == nil {
		return nil
	}

	loader := loaders.MustNewMemoryLoader(nil)
	eval := exec.Evaluator{
		Config: gonja.DefaultConfig,
		Environment: &exec.Environment{
			Filters:           gonja.DefaultEnvironment.Filters,
			ControlStructures: gonja.DefaultEnvironment.ControlStructures,
			Tests:             gonja.DefaultEnvironment.Tests,
			Methods:           gonja.DefaultEnvironment.Methods,
			Context:           ctx,
		},
		Loader: loader,
	}

	resVal := eval.Eval(*e.expr)
	resGoVal := resVal.ToGoSimpleType(false)
	return resGoVal
}

func (e *Expression) UnmarshalYAML(value *yaml.Node) error {
	var strVal string
	err := value.Decode(&strVal)
	if err != nil {
		return err
	}

	expr, err := parseExpression(strVal)
	if err != nil {
		return err
	}
	*e = *expr
	return nil
}

func (c *ValueOrEvaluable) Evaluate(context *exec.Context) any {
	if c.evaluable != nil {
		return c.evaluable.Evaluate(context)
	} else {
		return c.value
	}
}

func (c *ValueOrEvaluable) UnmarshalYAML(value *yaml.Node) error {
	var mapVal map[string]any
	var exprVal Expression
	var err error

	value.Decode(&mapVal)
	_, hasAnd := mapVal["and"]
	_, hasOr := mapVal["or"]
	if hasAnd {
		var andVal And
		err = value.Decode(&andVal)
		if err != nil {
			return err
		}
		*c = ValueOrEvaluable{
			evaluable: &andVal,
		}
		return nil
	}

	if hasOr {
		var orVal Or
		err = value.Decode(&orVal)
		if err != nil {
			return err
		}
		*c = ValueOrEvaluable{
			evaluable: &orVal,
		}
		return nil
	}

	err = value.Decode(&exprVal)
	if err == nil {
		*c = ValueOrEvaluable{
			evaluable: &exprVal,
		}
		return nil
	}

	var anyVal any
	err = value.Decode(&anyVal)
	if err != nil {
		return err
	}

	*c = ValueOrEvaluable{
		value: anyVal,
	}

	return nil
}

func parseExpression(expr string) (*Expression, error) {
	loader, _ := loaders.NewMemoryLoader(nil)
	stream := tokens.Lex(fmt.Sprintf("{{ %s }}", expr), gonja.DefaultConfig)
	stream.Next()
	parser := parser.NewParser("", stream, gonja.DefaultConfig, loader, gonja.DefaultEnvironment.ControlStructures)
	exprObj, err := parser.ParseExpression()
	if err != nil {
		return nil, err
	}

	return &Expression{
		source: expr,
		expr:   &exprObj,
	}, nil
}

func asBool(value any) bool {
	switch v := value.(type) {
	case string:
		return v != ""
	case int:
		return v != 0
	case float64:
		return v != 0
	case bool:
		return v
	case []any:
		return len(v) != 0
	case map[any]any:
		return len(v) != 0
	case nil:
		return false
	default:
		return false
	}
}
