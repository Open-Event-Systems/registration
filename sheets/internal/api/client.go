package api

import (
	"context"
	"sheets_hook/internal/config"

	"google.golang.org/api/option"
	"google.golang.org/api/sheets/v4"
)

type Client struct {
	service    *sheets.Service
	sheet      *sheets.Spreadsheet
	sheetRange string
}

type Row []any

func MakeClient(ctx context.Context, config *config.Config) (*Client, error) {
	authOpt := option.WithCredentialsFile(config.CredentialsFile)
	svc, err := sheets.NewService(ctx, authOpt)
	if err != nil {
		return nil, err
	}

	sheet, err := svc.Spreadsheets.Get(config.SpreadsheetId).Do()
	if err != nil {
		return nil, err
	}

	return &Client{
		service:    svc,
		sheet:      sheet,
		sheetRange: config.Range,
	}, nil
}

func (c *Client) Append(row Row) error {
	_, err := c.service.Spreadsheets.Values.Append(
		c.sheet.SpreadsheetId,
		c.sheetRange,
		&sheets.ValueRange{
			Values: [][]any{row},
		},
	).ValueInputOption("RAW").Do()

	return err
}
