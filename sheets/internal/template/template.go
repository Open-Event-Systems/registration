package template

import (
	"fmt"

	"github.com/nikolalohinski/gonja/v2"
	"github.com/nikolalohinski/gonja/v2/exec"
	"github.com/nikolalohinski/gonja/v2/loaders"
	"github.com/nikolalohinski/gonja/v2/nodes"
	"github.com/nikolalohinski/gonja/v2/parser"
	"github.com/nikolalohinski/gonja/v2/tokens"
)

type TemplateConfig struct {
	evaluator exec.Evaluator
}

type Expression struct {
	config *TemplateConfig
	source string
	expr   nodes.Expression
}

func NewTemplateConfig() *TemplateConfig {
	return &TemplateConfig{
		evaluator: exec.Evaluator{
			Config: gonja.DefaultConfig,
			Environment: &exec.Environment{
				Filters:           gonja.DefaultEnvironment.Filters,
				ControlStructures: gonja.DefaultEnvironment.ControlStructures,
				Tests:             gonja.DefaultEnvironment.Tests,
				Methods:           gonja.DefaultEnvironment.Methods,
				Context:           gonja.DefaultContext,
			},
			Loader: loaders.MustNewMemoryLoader(nil),
		},
	}
}

func (c *TemplateConfig) ParseExpression(expr string) (*Expression, error) {
	stream := tokens.Lex(fmt.Sprintf("{{ %s }}", expr), c.evaluator.Config)
	stream.Next()
	parser := parser.NewParser("", stream, c.evaluator.Config, c.evaluator.Loader, c.evaluator.Environment.ControlStructures)
	exprObj, err := parser.ParseExpression()
	if err != nil {
		return nil, err
	}

	return &Expression{
		config: c,
		source: expr,
		expr:   exprObj,
	}, nil
}

func (e *Expression) Evaluate(context map[string]any) any {
	eval := e.config.evaluator
	env := *e.config.evaluator.Environment
	env.Context = env.Context.Inherit().Update(exec.NewContext(context))
	eval.Environment = &env

	resVal := eval.Eval(e.expr)
	val := resVal.ToGoSimpleType(false)
	return val
}

func (e *Expression) String() string {
	return e.source
}
