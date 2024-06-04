package template

import (
	"email/config"
	"testing"
)

func TestTemplate(t *testing.T) {
	cfg := &config.Config{
		TemplatePath: ".",
	}

	env := NewEnvironment(cfg)
	input := &TemplateInput{
		To:      "to@test.com",
		From:    "from@test.com",
		Subject: "Test Subject",
		Data: map[string]interface{}{
			"test": "Test",
		},
	}
	res := env.Render("test_template", input)

	expected := `Subject: Test Subject

Data: Test
`

	if res.Text != expected {
		t.Fatalf("expected %s, got %s", expected, res.Text)
	}

	if res.HTML != "" {
		t.Fatalf("expected no HTML output, got %s", res.HTML)
	}
}

func TestAttachmentInline(t *testing.T) {
	cfg := &config.Config{
		TemplatePath: ".",
	}

	env := NewEnvironment(cfg)
	input := &TemplateInput{
		To:      "to@test.com",
		From:    "from@test.com",
		Subject: "Test Subject",
		Data:    make(map[string]interface{}),
	}
	res := env.Render("test_inline", input)

	expected := "Attachment: 1\n"

	if res.Text != expected {
		t.Fatalf("expected %s, got %s", expected, res.Text)
	}

	if len(res.Attachments.Attachments) != 1 {
		t.Fatalf("expected 1, got %d", len(res.Attachments.Attachments))
	}
}

func TestHTML(t *testing.T) {
	cfg := &config.Config{
		TemplatePath: ".",
	}

	env := NewEnvironment(cfg)
	input := &TemplateInput{
		To:      "to@test.com",
		From:    "from@test.com",
		Subject: "Test Subject",
		Data: map[string]interface{}{
			"test": "Test",
		},
	}
	res := env.Render("test_html", input)

	expected := (`<!doctype html><html><head><title>Test Subject</title></head>` +
		`<body><p style="font-family:Arial, Helvetica, sans-serif">` +
		`<span style="color:red">Test</span></p></body></html>`)

	if res.HTML != expected {
		t.Fatalf("expected %s, got %s", expected, res.HTML)
	}
}
