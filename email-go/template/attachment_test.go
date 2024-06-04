package template

import (
	"bytes"
	"fmt"
	"mime/multipart"
	"strings"
	"testing"
)

func TestAttachment(t *testing.T) {
	att := Attachment{
		Id:             "1",
		Name:           "test.txt",
		AttachmentType: AttachmentTypeInline,
		MediaType:      "text/plain",
		Data:           []byte("Hello, world!"),
	}
	var buf bytes.Buffer
	mpWriter := multipart.NewWriter(&buf)
	err := att.MakeMIMEPart(mpWriter)
	if err != nil {
		t.Fatal(err)
	}

	mpWriter.Close()

	res := buf.String()

	expected := fmt.Sprintf(`--%s
Content-Disposition: inline; filename="test.txt"
Content-Id: <1>
Content-Transfer-Encoding: base64
Content-Type: text/plain

SGVsbG8sIHdvcmxkIQ==
--%s--
`, mpWriter.Boundary(), mpWriter.Boundary())

	expected = strings.ReplaceAll(expected, "\n", "\r\n")

	if res != expected {
		t.Fatalf("expected %s, got %s", expected, res)
	}
}

func TestAttach(t *testing.T) {
	atts := Attachments{}
	attId, err := atts.AddAttachment(AttachmentTypeInline, ".", "test.gif")
	if err != nil {
		t.Error(err)
	}

	if attId != "1" {
		t.Errorf("expected 1, got %s", attId)
	}

	first := atts.Attachments[0]
	if first.Id != "1" {
		t.Errorf("expected 1, got %s", first.Id)
	}

	if first.MediaType != "image/gif" {
		t.Errorf("expected image/gif, got %s", first.MediaType)
	}

	expectedData := []byte{71, 73, 70, 56, 57, 97, 1, 0, 1, 0, 128, 0, 0, 0, 0, 0, 255, 255, 255, 33, 249, 4, 1, 0, 0, 0, 0, 44, 0, 0, 0, 0, 1, 0, 1, 0, 0, 2, 1, 68, 0, 59}
	if !bytes.Equal(first.Data, expectedData) {
		t.Errorf("data did not match: %v", first.Data)
	}
}
